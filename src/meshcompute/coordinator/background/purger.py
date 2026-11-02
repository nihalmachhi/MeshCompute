"""Delete terminal job data after its configured retention window."""

import asyncio
import logging
from datetime import UTC, datetime

from meshcompute.coordinator.db.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


def purge_once() -> int:
    """Remove expired jobs and their dependent task/result/audit rows."""
    with UnitOfWork() as uow:
        count = uow.jobs.purge_expired(datetime.now(UTC))
        if count:
            uow.commit()
        return count


async def run_purger(stop: asyncio.Event, interval_seconds: float = 60.0) -> None:
    """Run retention cleanup until coordinator shutdown."""
    while not stop.is_set():
        try:
            removed = await asyncio.to_thread(purge_once)
            if removed:
                logger.info("expired jobs purged", extra={"event": "job_purged", "count": removed})
        except Exception:
            logger.exception("job retention purge failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=interval_seconds)
        except TimeoutError:
            continue
