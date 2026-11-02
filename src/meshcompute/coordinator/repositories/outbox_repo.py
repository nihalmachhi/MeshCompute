"""Transactional outbox persistence and delivery bookkeeping."""

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from meshcompute.coordinator.db.tables import OutboxEventRecord


class OutboxRepository:
    """Persist events with domain writes and claim unpublished records."""

    def __init__(self, session: Session):
        self.session = session

    def enqueue(self, payload: dict) -> OutboxEventRecord:
        """Add an event row to the current transaction."""
        record = OutboxEventRecord(payload=payload)
        self.session.add(record)
        self.session.flush()
        return record

    def claim_pending(self, limit: int = 100) -> list[OutboxEventRecord]:
        """Lock a bounded batch for at-least-once in-process publication."""
        statement = (
            select(OutboxEventRecord)
            .where(OutboxEventRecord.published_at.is_(None))
            .order_by(OutboxEventRecord.created_at, OutboxEventRecord.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(self.session.scalars(statement))

    def mark_published(self, record: OutboxEventRecord, at: datetime) -> None:
        """Mark one record delivered in the current transaction."""
        record.published_at = at
