"""Deliver committed outbox events to the process-local live event hub."""

import asyncio
import logging
from datetime import UTC, datetime

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.events import event_hub

logger = logging.getLogger(__name__)


def dispatch_once(limit: int = 100) -> int:
    """Publish one locked batch and mark it delivered in its own transaction.

    Delivery is at least once: a crash after publication but before commit may
    produce a duplicate notification, while never losing the committed event.
    """
    with UnitOfWork() as uow:
        records = uow.outbox.claim_pending(limit)
        for record in records:
            event_hub.publish(record.payload)
            record.published_at = datetime.now(UTC)
        if records:
            uow.commit()
        return len(records)


async def run_outbox_dispatcher(stop: asyncio.Event, interval_seconds: float = 0.5) -> None:
    """Drain durable notifications until the coordinator shuts down."""
    while not stop.is_set():
        try:
            await asyncio.to_thread(dispatch_once)
        except Exception:
            logger.exception("outbox dispatcher failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
        except TimeoutError:
            continue
