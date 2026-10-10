"""Read-only task timeline queries for job detail views."""
from uuid import UUID
from meshcompute.common.errors import NotFoundError
from meshcompute.coordinator.db.unit_of_work import UnitOfWork

class TaskQueryService:
    """Expose task state without leaking ORM objects to API routes."""
    def list_for_job(self,uow: UnitOfWork,job_id: UUID) -> list[dict]:
        """Return task state, attempt, worker, and current lease for a job."""
        if uow.jobs.get(job_id) is None:raise NotFoundError("job not found")
        return [{"task_id":task.id,"task_index":task.task_index,"status":task.status,
            "attempt":task.attempt,"max_attempts":task.max_attempts,"worker_id":task.worker_id,
            "lease_expires_at":task.lease_expires_at,"queued_at":task.queued_at,
            "started_at":task.started_at,"finished_at":task.finished_at}
            for task in uow.tasks.list_by_job(job_id)]
