"""Atomic task claiming, lease scans, and state persistence."""
from datetime import datetime
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session
from meshcompute.coordinator.db.tables import TaskEventRecord,TaskRecord
from meshcompute.coordinator.domain.models import TaskStatus
from meshcompute.coordinator.domain.states import transition

class TaskRepository:
    """Perform task row locks and append-only event writes."""
    def __init__(self,session: Session): self.session=session
    def claim_next(self,worker_id: UUID,now: datetime,lease_until: datetime) -> TaskRecord|None:
        """Lock and assign the oldest pending task using PostgreSQL SKIP LOCKED."""
        statement=select(TaskRecord).where(TaskRecord.status==TaskStatus.PENDING.value).order_by(
            TaskRecord.queued_at,TaskRecord.task_index).limit(1).with_for_update(skip_locked=True)
        task=self.session.scalar(statement)
        if task is None:return None
        task.status=transition(task.status,TaskStatus.ASSIGNED).value
        task.attempt+=1;task.worker_id=worker_id;task.lease_expires_at=lease_until
        self.add_event(task,"assigned",worker_id,{"attempt":task.attempt})
        self.session.flush()
        return task
    def list_by_job(self,job_id: UUID) -> list[TaskRecord]:
        """List tasks for a job in stable task order."""
        return list(self.session.scalars(select(TaskRecord).where(TaskRecord.job_id==job_id).order_by(TaskRecord.task_index)))
    def get(self,task_id: UUID,lock: bool=False) -> TaskRecord|None:
        """Get one task, optionally obtaining a row lock."""
        statement=select(TaskRecord).where(TaskRecord.id==task_id)
        if lock:statement=statement.with_for_update()
        return self.session.scalar(statement)
    def expired(self,now: datetime) -> list[TaskRecord]:
        """Lock expired assigned and running tasks without blocking other reapers."""
        statement=select(TaskRecord).where(
            TaskRecord.status.in_([TaskStatus.ASSIGNED.value,TaskStatus.RUNNING.value]),
            TaskRecord.lease_expires_at<=now).order_by(TaskRecord.lease_expires_at).with_for_update(skip_locked=True)
        return list(self.session.scalars(statement))
    def state_counts(self,job_id: UUID) -> dict[str,int]:
        """Count persisted tasks by state for one job."""
        from sqlalchemy import func
        rows=self.session.execute(select(TaskRecord.status,func.count()).where(TaskRecord.job_id==job_id).group_by(TaskRecord.status))
        return {status:count for status,count in rows}
    def pending_count(self) -> int:
        """Count queue entries in the current transaction."""
        from sqlalchemy import func
        return self.session.scalar(select(func.count()).select_from(TaskRecord).where(TaskRecord.status==TaskStatus.PENDING.value)) or 0
    def set_status(self,task: TaskRecord,target: TaskStatus,now: datetime,worker_id: UUID|None=None) -> None:
        """Validate status changes and persist one matching audit event."""
        task.status=transition(task.status,target).value
        if target in {TaskStatus.PENDING,TaskStatus.COMPLETED,TaskStatus.FAILED}:
            task.lease_expires_at=None
        if target==TaskStatus.RUNNING: task.started_at=now
        if target in {TaskStatus.COMPLETED,TaskStatus.FAILED}: task.finished_at=now
        if target==TaskStatus.PENDING: task.worker_id=None
        self.add_event(task,target.value.lower(),worker_id,{"attempt":task.attempt})
        self.session.flush()
    def add_event(self,task: TaskRecord,event_type: str,worker_id: UUID|None,details: dict) -> None:
        """Append an immutable task lifecycle event."""
        self.session.add(TaskEventRecord(task_id=task.id,event_type=event_type,worker_id=worker_id,details=details))
