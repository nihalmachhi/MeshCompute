"""Job persistence and progress queries."""
from uuid import UUID
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from meshcompute.coordinator.db.tables import JobRecord,TaskRecord
from meshcompute.coordinator.domain.models import JobStatus
from meshcompute.coordinator.domain.states import transition_job

class JobRepository:
    """Persist jobs and compute their task-state summaries."""
    def __init__(self,session: Session): self.session=session
    def add(self,job: JobRecord,tasks: list[TaskRecord]) -> None:
        """Add a job and all of its pending tasks in the current unit of work."""
        self.session.add(job);self.session.add_all(tasks);self.session.flush()
    def get(self,job_id: UUID,lock: bool=False) -> JobRecord|None:
        """Look up a job, optionally locking it for a state transition."""
        statement=select(JobRecord).where(JobRecord.id==job_id)
        if lock: statement=statement.with_for_update()
        return self.session.scalar(statement)
    def set_status(self,job: JobRecord,target: JobStatus,finished_at=None) -> None:
        """Apply a validated job transition and optional completion timestamp."""
        job.status=transition_job(job.status,target).value
        if finished_at is not None: job.finished_at=finished_at
    def set_result(self,job: JobRecord,result: dict) -> None:
        """Store the merged job output."""
        job.result=result
    def list(self,limit: int,offset: int) -> list[JobRecord]:
        """Return newest jobs using stable pagination."""
        return list(self.session.scalars(select(JobRecord).order_by(JobRecord.created_at.desc()).limit(limit).offset(offset)))
    def task_counts(self,job_id: UUID) -> dict[str,int]:
        """Return counts by task state for one job."""
        rows=self.session.execute(select(TaskRecord.status,func.count()).where(TaskRecord.job_id==job_id).group_by(TaskRecord.status))
        return {status:count for status,count in rows}
    def queue_size(self) -> int:
        """Count pending tasks for admission control."""
        return self.session.scalar(select(func.count()).select_from(TaskRecord).where(TaskRecord.status=="PENDING")) or 0
