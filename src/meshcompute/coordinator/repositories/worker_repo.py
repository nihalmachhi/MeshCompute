"""Worker registration, heartbeat, and status persistence."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from meshcompute.coordinator.db.tables import WorkerRecord
from meshcompute.coordinator.domain.models import WorkerStatus
from meshcompute.coordinator.domain.states import transition_worker


class WorkerRepository:
    """Track workers without exposing database access to worker processes."""

    def __init__(self, session: Session):
        self.session = session

    def register(self, name: str, now: datetime, token_hash: str | None = None) -> WorkerRecord:
        """Create a worker identity with an initial heartbeat."""
        worker = WorkerRecord(
            id=uuid4(),
            name=name,
            status=WorkerStatus.ACTIVE.value,
            registered_at=now,
            last_heartbeat_at=now,
            token_hash=token_hash,
        )
        self.session.add(worker)
        self.session.flush()
        return worker

    def get_by_token_hash(self, token_hash: str) -> WorkerRecord | None:
        """Look up a worker by its hashed bearer token."""
        return self.session.scalar(
            select(WorkerRecord).where(WorkerRecord.token_hash == token_hash)
        )

    def get(self, worker_id: UUID, lock: bool = False) -> WorkerRecord | None:
        """Look up a worker, optionally locking it for a lease operation."""
        statement = select(WorkerRecord).where(WorkerRecord.id == worker_id)
        if lock:
            statement = statement.with_for_update()
        return self.session.scalar(statement)

    def heartbeat(self, worker: WorkerRecord, now: datetime) -> None:
        """Refresh last-seen time and restore a stale worker to active."""
        worker.last_heartbeat_at = now
        if worker.status != WorkerStatus.ACTIVE.value:
            worker.status = transition_worker(worker.status, WorkerStatus.ACTIVE).value

    def active_and_stale_counts(self, stale_before: datetime) -> dict[str, int]:
        """Aggregate online and stale worker counts for metrics."""
        from sqlalchemy import func

        rows = self.session.execute(
            select(WorkerRecord.status, func.count())
            .where(WorkerRecord.last_heartbeat_at >= stale_before)
            .group_by(WorkerRecord.status)
        )
        result = {status: count for status, count in rows}
        result["STALE"] = (
            self.session.query(WorkerRecord)
            .filter(WorkerRecord.last_heartbeat_at < stale_before)
            .count()
        )
        return result

    def stale_before(self, cutoff: datetime) -> list[WorkerRecord]:
        """Lock active workers whose heartbeat is older than a cutoff."""
        statement = (
            select(WorkerRecord)
            .where(
                WorkerRecord.status == WorkerStatus.ACTIVE.value,
                WorkerRecord.last_heartbeat_at < cutoff,
            )
            .with_for_update(skip_locked=True)
        )
        return list(self.session.scalars(statement))

    def offline_before(self, cutoff: datetime) -> list[WorkerRecord]:
        """Lock stale workers old enough to mark offline."""
        statement = (
            select(WorkerRecord)
            .where(
                WorkerRecord.status == WorkerStatus.STALE.value,
                WorkerRecord.last_heartbeat_at < cutoff,
            )
            .with_for_update(skip_locked=True)
        )
        return list(self.session.scalars(statement))

    def purge_offline_before(self, cutoff: datetime) -> int:
        """Delete expired offline identities that no longer own a task."""
        deleted_ids = self.session.scalars(
            delete(WorkerRecord)
            .where(
                WorkerRecord.status == WorkerStatus.OFFLINE.value,
                WorkerRecord.last_heartbeat_at < cutoff,
                WorkerRecord.current_task_id.is_(None),
            )
            .returning(WorkerRecord.id)
        )
        return len(list(deleted_ids))

    def set_status(self, worker: WorkerRecord, target: WorkerStatus) -> None:
        """Apply a legal worker status transition."""
        worker.status = transition_worker(worker.status, target).value

    def all(self) -> list[WorkerRecord]:
        """Return workers ordered by most recent heartbeat."""
        return list(
            self.session.scalars(
                select(WorkerRecord).order_by(WorkerRecord.last_heartbeat_at.desc())
            )
        )
