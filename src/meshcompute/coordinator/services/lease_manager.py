"""Heartbeats extend task leases; the reaper recovers expired attempts."""
from datetime import timedelta
from uuid import UUID
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.common.errors import ConflictError,NotFoundError
from meshcompute.common.settings import Settings,get_settings
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import TaskStatus
from meshcompute.coordinator.events import event_hub
from meshcompute.coordinator.services.aggregation_service import AggregationService
from meshcompute.coordinator.services.scheduler import _validate_owner

class LeaseManager:
    """Own heartbeat fencing and lease expiry behavior."""
    def __init__(self,settings: Settings|None=None,clock: Clock|None=None):
        self.settings=settings or get_settings();self.clock=clock or SystemClock()
    async def heartbeat(self,uow: UnitOfWork,worker_id: UUID,task_id: UUID|None,attempt: int|None) -> dict:
        """Refresh worker liveness and extend its current task lease."""
        now=self.clock.now();worker=uow.workers.get(worker_id,lock=True)
        if worker is None:raise NotFoundError("worker not found")
        uow.workers.heartbeat(worker,now)
        if task_id is None:
            worker.current_task_id=None
            return {"worker_id":worker_id,"lease_expires_at":None}
        if attempt is None:raise ConflictError("attempt is required with task_id")
        task=uow.tasks.get(task_id,lock=True)
        if task is None:raise NotFoundError("task not found")
        _validate_owner(task,worker_id,attempt)
        if task.status not in {TaskStatus.ASSIGNED.value,TaskStatus.RUNNING.value}:
            raise ConflictError("task no longer has an active lease")
        task.lease_expires_at=now+timedelta(seconds=self.settings.lease_ttl_seconds)
        worker.current_task_id=task.id
        return {"worker_id":worker_id,"lease_expires_at":task.lease_expires_at}
    async def reap(self,uow: UnitOfWork) -> int:
        """Requeue expired leases, terminally fail exhausted tasks, and finalize jobs."""
        now=self.clock.now();affected=set()
        for task in uow.tasks.expired(now):
            former_worker=task.worker_id
            if former_worker is not None:
                worker=uow.workers.get(former_worker,lock=True)
                if worker is not None and worker.current_task_id==task.id:worker.current_task_id=None
            target=TaskStatus.PENDING if task.attempt<task.max_attempts else TaskStatus.FAILED
            uow.tasks.add_event(task,"lease_expired",former_worker,{"attempt":task.attempt,"requeued":target==TaskStatus.PENDING})
            uow.tasks.set_status(task,target,now,former_worker)
            affected.add(task.job_id)
            await event_hub.publish({"type":"task.lease_expired","task_id":str(task.id),"job_id":str(task.job_id)})
        await _mark_stale_workers(uow,now-timedelta(seconds=self.settings.lease_ttl_seconds))
        aggregator=AggregationService(self.clock)
        for job_id in affected:await aggregator.finalize_if_ready(uow,job_id)
        return len(affected)

async def _mark_stale_workers(uow: UnitOfWork,cutoff) -> None:
    """Mark workers whose heartbeat has exceeded their lease window."""
    from meshcompute.coordinator.domain.models import WorkerStatus
    for worker in uow.workers.stale_before(cutoff):
        uow.workers.set_status(worker,WorkerStatus.STALE)
        await event_hub.publish({"type":"worker.stale","worker_id":str(worker.id)})
