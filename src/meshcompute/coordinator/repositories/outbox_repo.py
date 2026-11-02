"""Transactional outbox persistence and per-process cursor reads."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from meshcompute.coordinator.db.tables import OutboxEventRecord


class OutboxRepository:
    """Persist events with domain writes and read events for each coordinator process."""

    def __init__(self, session: Session):
        self.session = session

    def enqueue(self, payload: dict) -> OutboxEventRecord:
        """Add an event row to the current transaction."""
        record = OutboxEventRecord(payload=payload)
        self.session.add(record)
        self.session.flush()
        return record

    def latest_cursor(self) -> tuple[datetime, UUID] | None:
        """Return the latest stored event cursor when a coordinator starts."""
        statement = (
            select(OutboxEventRecord.created_at, OutboxEventRecord.id)
            .order_by(OutboxEventRecord.created_at.desc(), OutboxEventRecord.id.desc())
            .limit(1)
        )
        row = self.session.execute(statement).first()
        return (row[0], row[1]) if row is not None else None

    def after_cursor(
        self, cursor: tuple[datetime, UUID] | None, limit: int = 100
    ) -> list[OutboxEventRecord]:
        """Read ordered events after one coordinator's last delivered event."""
        statement = select(OutboxEventRecord)
        if cursor is not None:
            created_at, event_id = cursor
            statement = statement.where(
                or_(
                    OutboxEventRecord.created_at > created_at,
                    and_(
                        OutboxEventRecord.created_at == created_at,
                        OutboxEventRecord.id > event_id,
                    ),
                )
            )
        statement = statement.order_by(OutboxEventRecord.created_at, OutboxEventRecord.id).limit(
            limit
        )
        return list(self.session.scalars(statement))
