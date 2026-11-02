"""Atomic task claiming, lease scans, and state persistence."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from meshcompute.coordinator.db.tables import TaskDependencyRecord, TaskEventRecord, TaskRecord
from meshcompute.coordinator.domain.models import TaskStatus
from meshcompute.coordinator.domain.states import transition


class TaskRepository:
    """Perform task row locks and append-only event writes."""

    def __init__(self, session: Session):
        self.session = session

    def claim_next(
        self,
        worker_id: UUID,
        now: datetime,
        lease_until: datetime,
        capabilities: list[str] | None = None,
        aging_seconds: int = 30,
    ) -> TaskRecord | None:
        """Claim a ready, compatible task using aging priority and per-job fairness."""
        from sqlalchemy import func

        from meshcompute.coordinator.db.tables import JobRecord
        from meshcompute.coordinator.domain.scheduling import effective_priority

        available = capabilities or []

        blocked_tasks = (
            select(TaskDependencyRecord.task_id)
            .join(TaskRecord, TaskRecord.id == TaskDependencyRecord.depends_on_task_id)
            .where(TaskRecord.status != TaskStatus.COMPLETED.value)
        )
        pending_jobs = [
            row[0]
            for row in self.session.execute(
                select(TaskRecord.job_id)
                .where(
                    TaskRecord.status == TaskStatus.PENDING.value,
                    TaskRecord.id.not_in(blocked_tasks),
                    TaskRecord.required_capabilities.contained_by(available),
                )
                .distinct()
            )
        ]
        if not pending_jobs:
            return None
        best_job = None
        best_rank = None
        for job_id in pending_jobs:
            job = self.session.get(JobRecord, job_id)
            oldest_queued = self.session.scalar(
                select(func.min(TaskRecord.queued_at)).where(
                    TaskRecord.job_id == job_id,
                    TaskRecord.status == TaskStatus.PENDING.value,
                    TaskRecord.id.not_in(blocked_tasks),
                    TaskRecord.required_capabilities.contained_by(available),
                )
            )
            active = (
                self.session.scalar(
                    select(func.count())
                    .select_from(TaskRecord)
                    .where(
                        TaskRecord.job_id == job_id,
                        TaskRecord.status.in_(
                            [TaskStatus.ASSIGNED.value, TaskStatus.RUNNING.value]
                        ),
                    )
                )
                or 0
            )
            if oldest_queued is None:
                continue
            score = effective_priority(
                job.priority if job is not None else 0, oldest_queued, now, aging_seconds
            )
            rank = (
                score,
                -active,
                -oldest_queued.timestamp(),
            )
            if best_rank is None or rank > best_rank:
                best_rank = rank
                best_job = job_id
        statement = (
            select(TaskRecord)
            .where(
                TaskRecord.status == TaskStatus.PENDING.value,
                TaskRecord.job_id == best_job,
                TaskRecord.id.not_in(blocked_tasks),
                TaskRecord.required_capabilities.contained_by(available),
            )
            .order_by(TaskRecord.queued_at, TaskRecord.task_index)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        task = self.session.scalar(statement)
        if task is None:
            return None
        task.status = transition(task.status, TaskStatus.ASSIGNED).value
        task.attempt += 1
        task.worker_id = worker_id
        task.lease_expires_at = lease_until
        self.add_event(task, "assigned", worker_id, {"attempt": task.attempt})
        self.session.flush()
        return task

    def list_by_job(self, job_id: UUID) -> list[TaskRecord]:
        """List tasks for a job in stable task order."""
        return list(
            self.session.scalars(
                select(TaskRecord)
                .where(TaskRecord.job_id == job_id)
                .order_by(TaskRecord.task_index)
            )
        )

    def get(self, task_id: UUID, lock: bool = False) -> TaskRecord | None:
        """Get one task, optionally obtaining a row lock."""
        statement = select(TaskRecord).where(TaskRecord.id == task_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def cancel_for_job(self, job_id: UUID) -> list[TaskRecord]:
        """Lock all queued and leased tasks so cancellation fences old attempts."""
        statement = (
            select(TaskRecord)
            .where(
                TaskRecord.job_id == job_id,
                TaskRecord.status.in_(
                    [TaskStatus.PENDING.value, TaskStatus.ASSIGNED.value, TaskStatus.RUNNING.value]
                ),
            )
            .order_by(TaskRecord.task_index)
            .with_for_update()
        )
        return list(self.session.scalars(statement))

    def cancel_descendants(self, failed_task_id: UUID, now: datetime) -> list[TaskRecord]:
        """Cancel queued descendants when a prerequisite exhausts its retries."""
        edges = list(
            self.session.execute(
                select(TaskDependencyRecord.task_id, TaskDependencyRecord.depends_on_task_id)
            )
        )
        children: dict[UUID, list[UUID]] = {}
        for task_id, prerequisite_id in edges:
            children.setdefault(prerequisite_id, []).append(task_id)
        descendants: set[UUID] = set()
        pending = [failed_task_id]
        while pending:
            for child_id in children.get(pending.pop(), []):
                if child_id not in descendants:
                    descendants.add(child_id)
                    pending.append(child_id)
        if not descendants:
            return []
        tasks = list(
            self.session.scalars(
                select(TaskRecord)
                .where(
                    TaskRecord.id.in_(descendants),
                    TaskRecord.status == TaskStatus.PENDING.value,
                )
                .order_by(TaskRecord.task_index)
                .with_for_update()
            )
        )
        for task in tasks:
            self.set_status(task, TaskStatus.CANCELLED, now)
        return tasks

    def dependencies_for_job(self, job_id: UUID) -> list[tuple[int, int]]:
        """Return dependency edges as stable task-index pairs for lineage views."""
        dependent = aliased(TaskRecord)
        prerequisite = aliased(TaskRecord)
        rows = self.session.execute(
            select(prerequisite.task_index, dependent.task_index)
            .join(TaskDependencyRecord, TaskDependencyRecord.depends_on_task_id == prerequisite.id)
            .join(dependent, dependent.id == TaskDependencyRecord.task_id)
            .where(dependent.job_id == job_id)
            .order_by(prerequisite.task_index, dependent.task_index)
        )
        return [(source, target) for source, target in rows]

    def expired(self, now: datetime) -> list[TaskRecord]:
        """Lock expired assigned and running tasks without blocking other reapers."""
        statement = (
            select(TaskRecord)
            .where(
                TaskRecord.status.in_([TaskStatus.ASSIGNED.value, TaskStatus.RUNNING.value]),
                TaskRecord.lease_expires_at <= now,
            )
            .order_by(TaskRecord.lease_expires_at)
            .with_for_update(skip_locked=True)
        )
        return list(self.session.scalars(statement))

    def state_counts(self, job_id: UUID) -> dict[str, int]:
        """Count persisted tasks by state for one job."""
        from sqlalchemy import func

        rows = self.session.execute(
            select(TaskRecord.status, func.count())
            .where(TaskRecord.job_id == job_id)
            .group_by(TaskRecord.status)
        )
        return {status: count for status, count in rows}

    def pending_count(self) -> int:
        """Count queue entries in the current transaction."""
        from sqlalchemy import func

        return (
            self.session.scalar(
                select(func.count())
                .select_from(TaskRecord)
                .where(TaskRecord.status == TaskStatus.PENDING.value)
            )
            or 0
        )

    def set_status(
        self, task: TaskRecord, target: TaskStatus, now: datetime, worker_id: UUID | None = None
    ) -> None:
        """Validate status changes and persist one matching audit event."""
        task.status = transition(task.status, target).value
        if target in {
            TaskStatus.PENDING,
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        }:
            task.lease_expires_at = None
        if target == TaskStatus.RUNNING:
            task.started_at = now
        if target in {TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED}:
            task.finished_at = now
        if target == TaskStatus.PENDING:
            task.worker_id = None
        self.add_event(task, target.value.lower(), worker_id, {"attempt": task.attempt})
        self.session.flush()

    def add_event(
        self, task: TaskRecord, event_type: str, worker_id: UUID | None, details: dict
    ) -> None:
        """Append an immutable task lifecycle event."""
        self.session.add(
            TaskEventRecord(
                task_id=task.id, event_type=event_type, worker_id=worker_id, details=details
            )
        )
