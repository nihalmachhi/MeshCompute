"""Deliver transactional outbox events to every coordinator via PostgreSQL."""

import asyncio
import contextlib
import logging
import threading
from datetime import datetime
from uuid import UUID

import psycopg

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.events import event_hub
from meshcompute.core.settings import get_settings

logger = logging.getLogger(__name__)
Cursor = tuple[datetime, UUID] | None


def latest_cursor() -> Cursor:
    """Start a coordinator at the current outbox head; future events are consumed locally."""
    with UnitOfWork() as uow:
        return uow.outbox.latest_cursor()


def dispatch_since(cursor: Cursor, limit: int = 100) -> tuple[int, Cursor]:
    """Publish a batch after one process-local cursor without globally claiming rows."""
    with UnitOfWork() as uow:
        records = uow.outbox.after_cursor(cursor, limit)
        for record in records:
            event_hub.publish(record.payload)
        if records:
            last = records[-1]
            cursor = (last.created_at, last.id)
        return len(records), cursor


def _listen(stop: threading.Event, interval_seconds: float) -> None:
    """Listen in a thread so psycopg works with Windows' default event loop too."""
    cursor: Cursor = None
    conninfo = get_settings().sync_database_url.replace("postgresql+psycopg://", "postgresql://")
    while not stop.is_set():
        try:
            if cursor is None:
                cursor = latest_cursor()
            with psycopg.connect(conninfo, autocommit=True) as connection:
                connection.execute("LISTEN meshcompute_events")
                _, cursor = dispatch_since(cursor)
                while not stop.is_set():
                    notifications = connection.notifies(timeout=interval_seconds, stop_after=1)
                    next(notifications, None)
                    _, cursor = dispatch_since(cursor)
        except Exception:
            logger.exception("outbox listener failed")
            stop.wait(interval_seconds)


async def run_outbox_dispatcher(stop: asyncio.Event, interval_seconds: float = 0.5) -> None:
    """Listen for committed notifications and poll the durable log as a recovery path."""
    thread_stop = threading.Event()
    listener = asyncio.create_task(asyncio.to_thread(_listen, thread_stop, interval_seconds))
    try:
        await stop.wait()
    finally:
        thread_stop.set()
        with contextlib.suppress(asyncio.CancelledError):
            await listener
