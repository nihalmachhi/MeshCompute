"""Task start, result fencing, retry, and job finalization workflows."""
from datetime import timedelta
from uuid import UUID
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.common.errors import ConflictError,NotFoundError
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import TaskStatus
from meshcompute.coordinator.events import event_hub
from meshcompute.coordinator.services.aggregation_service import AggregationService
from meshcompute.coordinator.services.scheduler import _validate_owner

class TaskService:
    """Validate task ownership and commit results idempotently."""
    def __init__(self,clock: Clock|None=None): self.clock=clock or SystemClock()
    async def complete(self,uow: UnitOfWork,task_id: UUID,worker_id: UUID,attempt: int,output: dict,duration_ms: float) -> dict:
        """Fence stale attempts and commit one result before aggregation."""
        task=uow.tasks.get(task_id,lock=True)
        if task is None:raise NotFoundError("task not found")
        _validate_owner(task,worker_id,attempt)
        if task.status==TaskStatus.COMPLETED.value:
            result=uow.results.get(task.id)
            if result is not None and result.attempt==attempt:
                return {"task_id":task.id,"status":task.status,"idempotent":True}
            raise ConflictError("task was completed by a different attempt")
        self._assert_active(task,attempt)
        now=self.clock.now()
        if task.lease_expires_at is None or task.lease_expires_at<=now:raise ConflictError("task lease expired")
        uow.tasks.set_status(task,TaskStatus.COMPLETED,now,worker_id)
        uow.results.add(task.id,attempt,output,duration_ms,now)
        worker=uow.workers.get(worker_id,lock=True)
        if worker is not None and worker.current_task_id==task.id:worker.current_task_id=None
        await AggregationService(self.clock).finalize_if_ready(uow,task.job_id)
        await event_hub.publish({"type":"task.completed","task_id":str(task.id),"job_id":str(task.job_id)})
        return {"task_id":task.id,"status":task.status,"idempotent":False}
    async def fail(self,uow: UnitOfWork,task_id: UUID,worker_id: UUID,attempt: int,error: str) -> dict:
        """Retry a failed task until its configured attempt budget is exhausted."""
        task=uow.tasks.get(task_id,lock=True)
        if task is None:raise NotFoundError("task not found")
        _validate_owner(task,worker_id,attempt);self._assert_active(task,attempt)
        now=self.clock.now()
        if task.lease_expires_at is None or task.lease_expires_at<=now:raise ConflictError("task lease expired")
        retry=task.attempt<task.max_attempts
        uow.tasks.add_event(task,"attempt_failed",worker_id,{"attempt":attempt,"error":error[:300]})
        target=TaskStatus.PENDING if retry else TaskStatus.FAILED
        uow.tasks.set_status(task,target,now,worker_id)
        worker=uow.workers.get(worker_id,lock=True)
        if worker is not None and worker.current_task_id==task.id:worker.current_task_id=None
        if not retry:await AggregationService(self.clock).finalize_if_ready(uow,task.job_id)
        await event_hub.publish({"type":"task.retry" if retry else "task.failed","task_id":str(task.id),"job_id":str(task.job_id)})
        return {"task_id":task.id,"status":task.status,"idempotent":False}
    @staticmethod
    def _assert_active(task,attempt: int) -> None:
        """Require the currently fenced attempt to own a running task."""
        if task.attempt!=attempt:raise ConflictError("stale attempt number")
        if task.status!=TaskStatus.RUNNING.value:raise ConflictError("task is not RUNNING")
