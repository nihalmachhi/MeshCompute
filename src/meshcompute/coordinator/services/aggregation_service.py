"""Build a final result after all task work has reached a terminal state."""
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import JobStatus

class AggregationService:
    """Merge committed results exactly once when a job's tasks are terminal."""
    def __init__(self,clock: Clock|None=None): self.clock=clock or SystemClock()
    async def finalize_if_ready(self,uow: UnitOfWork,job_id) -> None:
        """Finalize completed jobs or mark exhausted jobs as failed."""
        uow.session.flush()
        job=uow.jobs.get(job_id,lock=True)
        if job is None or job.status in {JobStatus.COMPLETED.value,JobStatus.FAILED.value}:return
        counts=uow.jobs.task_counts(job_id)
        completed=counts.get("COMPLETED",0);failed=counts.get("FAILED",0)
        if completed==job.chunk_count:
            from meshcompute.worker.handlers.registry import get_handler
            outputs=uow.results.outputs_for_job(job_id)
            job.result=get_handler(job.job_type).merge(outputs)
            uow.jobs.set_status(job,JobStatus.COMPLETED,self.clock.now())
            await _publish("job.completed",job_id)
        elif completed+failed==job.chunk_count and failed:
            uow.jobs.set_status(job,JobStatus.FAILED,self.clock.now())
            await _publish("job.failed",job_id)

async def _publish(event_type: str,job_id) -> None:
    """Publish a concise state notification without task payloads."""
    from meshcompute.coordinator.events import event_hub
    await event_hub.publish({"type":event_type,"job_id":str(job_id)})
