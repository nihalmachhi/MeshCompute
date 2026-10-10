"""Idempotent task result persistence and benchmark event queries."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from meshcompute.coordinator.db.tables import TaskEventRecord,TaskResultRecord

class ResultRepository:
    """Read and write one durable result per task."""
    def __init__(self,session: Session): self.session=session
    def get(self,task_id: UUID) -> TaskResultRecord|None:
        """Find a result already committed for a task."""
        return self.session.get(TaskResultRecord,task_id)
    def add(self,task_id: UUID,attempt: int,output: dict,duration_ms: float,now: datetime) -> TaskResultRecord:
        """Stage the result; database primary key enforces idempotency."""
        row=TaskResultRecord(task_id=task_id,attempt=attempt,output=output,duration_ms=duration_ms,committed_at=now)
        self.session.add(row);self.session.flush();return row
    def outputs_for_job(self,job_id: UUID) -> list[dict]:
        """Return committed outputs in task-index order for deterministic merge."""
        from meshcompute.coordinator.db.tables import TaskRecord
        rows=self.session.execute(select(TaskResultRecord.output).join(TaskRecord,TaskRecord.id==TaskResultRecord.task_id)
                                  .where(TaskRecord.job_id==job_id).order_by(TaskRecord.task_index))
        return [output for (output,) in rows]
    def summary(self,since: datetime) -> dict[str,float|int]:
        """Calculate completion rate, retries, failures, and mean task runtime."""
        completed=self.session.scalar(select(func.count()).select_from(TaskEventRecord).where(
            TaskEventRecord.event_type=="completed",TaskEventRecord.at>=since)) or 0
        retries=self.session.scalar(select(func.count()).select_from(TaskEventRecord).where(TaskEventRecord.event_type=="pending")) or 0
        failed=self.session.scalar(select(func.count()).select_from(TaskEventRecord).where(TaskEventRecord.event_type=="failed")) or 0
        mean=self.session.scalar(select(func.avg(TaskResultRecord.duration_ms))) or 0.0
        return {"completed_last_minute":completed,"retries":retries,"failures":failed,"mean_task_duration_ms":round(float(mean),2)}
