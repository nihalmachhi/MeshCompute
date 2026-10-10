"""Job submission, admission control, and read-side job summaries."""
from uuid import UUID
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.common.errors import BackpressureError,NotFoundError
from meshcompute.common.settings import Settings,get_settings
from meshcompute.coordinator.api.schemas import JobSubmission
from meshcompute.coordinator.db.tables import JobRecord,TaskRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import JobStatus,TaskStatus
from meshcompute.coordinator.events import event_hub
from meshcompute.worker.handlers.registry import get_handler

class JobService:
    """Validate job intent and persist its deterministic task plan."""
    def __init__(self,settings: Settings|None=None,clock: Clock|None=None):
        self.settings=settings or get_settings();self.clock=clock or SystemClock()
    async def submit(self,uow: UnitOfWork,request: JobSubmission) -> dict:
        """Split a registered handler workload and enqueue within queue limits."""
        handler=get_handler(request.job_type)
        chunks=handler.split(request.input_ref,request.options)
        if not chunks:raise ValueError("job input produced no tasks")
        if uow.tasks.pending_count()+len(chunks)>self.settings.max_pending_tasks:
            raise BackpressureError("pending task limit reached")
        job=JobRecord(job_type=request.job_type,input_ref=request.input_ref,
                      chunk_count=len(chunks),status=JobStatus.SUBMITTED.value)
        tasks=[TaskRecord(job_id=job.id,task_index=index,payload=payload,
                          status=TaskStatus.PENDING.value,attempt=0,
                          max_attempts=self.settings.max_task_attempts)
               for index,payload in enumerate(chunks)]
        uow.jobs.add(job,tasks)
        await event_hub.publish({"type":"job.submitted","job_id":str(job.id),"task_count":len(tasks)})
        return {"job_id":job.id,"status":job.status,"task_count":len(tasks)}
    def get(self,uow: UnitOfWork,job_id: UUID) -> dict:
        """Return a job and grouped task-state counts."""
        job=uow.jobs.get(job_id)
        if job is None:raise NotFoundError(f"job {job_id} not found")
        counts=uow.jobs.task_counts(job_id)
        return {"id":job.id,"job_type":job.job_type,"status":job.status,
                "task_count":job.chunk_count,"tasks_by_state":counts,
                "created_at":job.created_at,"finished_at":job.finished_at}
    def tasks(self,uow: UnitOfWork,job_id: UUID) -> list[dict]:
        """Return task-level details for the read-only job timeline."""
        from meshcompute.coordinator.services.task_query_service import TaskQueryService
        return TaskQueryService().list_for_job(uow,job_id)
    def result(self,uow: UnitOfWork,job_id: UUID) -> dict:
        """Return an aggregated result only after successful completion."""
        job=uow.jobs.get(job_id)
        if job is None:raise NotFoundError(f"job {job_id} not found")
        if job.status!=JobStatus.COMPLETED.value:
            from meshcompute.common.errors import ConflictError
            raise ConflictError("job result is not ready")
        return {"job_id":job.id,"job_type":job.job_type,"result":job.result}
    def list(self,uow: UnitOfWork,limit: int=50,offset: int=0) -> dict:
        """Return a bounded page of recent jobs with progress counts."""
        items=[]
        for job in uow.jobs.list(limit,offset):
            items.append({"id":job.id,"job_type":job.job_type,"status":job.status,
                "task_count":job.chunk_count,"tasks_by_state":uow.jobs.task_counts(job.id),
                "created_at":job.created_at,"finished_at":job.finished_at})
        return {"items":items,"limit":limit,"offset":offset}
