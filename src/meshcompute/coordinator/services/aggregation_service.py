"""Build a final result after all task work has reached a terminal state."""

from datetime import timedelta

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import JobStatus
from meshcompute.core.clock import Clock, SystemClock
from meshcompute.core.settings import Settings, get_settings


class AggregationService:
    """Merge committed results exactly once when a job's tasks are terminal."""

    def __init__(self, clock: Clock | None = None, settings: Settings | None = None):
        self.clock = clock or SystemClock()
        self.settings = settings or get_settings()

    def finalize_if_ready(self, uow: UnitOfWork, job_id) -> None:
        """Finalize completed jobs or mark exhausted jobs as failed."""
        uow.session.flush()
        job = uow.jobs.get(job_id, lock=True)
        if job is None or job.status in {JobStatus.COMPLETED.value, JobStatus.FAILED.value}:
            return
        counts = uow.jobs.task_counts(job_id)
        completed = counts.get("COMPLETED", 0)
        failed = counts.get("FAILED", 0)
        cancelled = counts.get("CANCELLED", 0)
        if completed == job.chunk_count:
            from meshcompute.handlers.registry import get_handler

            outputs = uow.results.outputs_for_job(job_id)
            job.result = get_handler(job.job_type).merge(outputs)
            finished_at = self.clock.now()
            uow.jobs.set_status(job, JobStatus.COMPLETED, finished_at)
            job.expires_at = finished_at + timedelta(seconds=self.settings.result_retention_seconds)
            uow.enqueue_event({"type": "job.completed", "job_id": str(job_id)})
        elif completed + failed + cancelled == job.chunk_count and failed:
            finished_at = self.clock.now()
            uow.jobs.set_status(job, JobStatus.FAILED, finished_at)
            job.expires_at = finished_at + timedelta(seconds=self.settings.result_retention_seconds)
            uow.enqueue_event({"type": "job.failed", "job_id": str(job_id)})
