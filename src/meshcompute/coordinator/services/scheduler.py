"""FIFO task scheduling with transactional lease assignment."""
from datetime import timedelta
from uuid import UUID
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.common.errors import ConflictError,NotFoundError
from meshcompute.common.settings import Settings,get_settings
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import JobStatus,TaskStatus,WorkerStatus
from meshcompute.coordinator.events import event_hub

class SchedulerService:
    """Coordinate worker claims without running business handlers."""
    def __init__(self,settings: Settings|None=None,clock: Clock|None=None):
        self.settings=settings or get_settings();self.clock=clock or SystemClock()
    async def claim(self,uow: UnitOfWork,worker_id: UUID) -> dict|None:
        """Atomically lease the oldest pending task to an idle worker."""
        now=self.clock.now();worker=uow.workers.get(worker_id,lock=True)
        if worker is None:raise NotFoundError("worker is not registered")
        if worker.current_task_id is not None:raise ConflictError("worker already owns a task")
        uow.workers.heartbeat(worker,now)
        task=uow.tasks.claim_next(worker_id,now,now+timedelta(seconds=self.settings.lease_ttl_seconds))
        if task is None:return None
        job=uow.jobs.get(task.job_id,lock=True)
        if job is None:raise NotFoundError("task job does not exist")
        if job.status==JobStatus.SUBMITTED.value:uow.jobs.set_status(job,JobStatus.RUNNING)
        worker.current_task_id=task.id
        await event_hub.publish({"type":"task.assigned","job_id":str(job.id),"task_id":str(task.id)})
        return {"task_id":task.id,"job_id":job.id,"task_index":task.task_index,
                "job_type":job.job_type,"payload":task.payload,"attempt":task.attempt,
                "lease_expires_at":task.lease_expires_at}
    async def start(self,uow: UnitOfWork,task_id: UUID,worker_id: UUID,attempt: int) -> dict:
        """Move an owned task from ASSIGNED to RUNNING."""
        task=uow.tasks.get(task_id,lock=True)
        if task is None:raise NotFoundError("task not found")
        _validate_owner(task,worker_id,attempt)
        if task.status!=TaskStatus.ASSIGNED.value:raise ConflictError("task is not awaiting start")
        uow.tasks.set_status(task,TaskStatus.RUNNING,self.clock.now(),worker_id)
        await event_hub.publish({"type":"task.running","task_id":str(task.id),"job_id":str(task.job_id)})
        return {"task_id":task.id,"status":task.status}
def _validate_owner(task,worker_id: UUID,attempt: int) -> None:
    """Reject stale or foreign worker attempts."""
    if task.attempt!=attempt:raise ConflictError("stale task attempt")
    if task.worker_id!=worker_id:raise ConflictError("worker does not own this task")
