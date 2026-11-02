"""Periodic lease expiry and stale-worker maintenance."""

import asyncio
import logging

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.lease_manager import LeaseManager
from meshcompute.core.settings import get_settings

logger = logging.getLogger(__name__)


async def _reap_once() -> int:
    """Run one transactional reaper pass in a worker thread."""

    def run():
        with UnitOfWork() as uow:
            return LeaseManager().reap(uow)

    return await asyncio.to_thread(run)


async def run_reaper(stop: asyncio.Event) -> None:
    """Reap expired leases on a configurable interval until shutdown."""
    settings = get_settings()
    while not stop.is_set():
        try:
            count = await _reap_once()
            if count:
                logger.info(
                    "expired leases recovered", extra={"event": "lease_reaped", "count": count}
                )
        except Exception:
            logger.exception("lease reaper failed")
        try:
            await asyncio.wait_for(stop.wait(), timeout=settings.reaper_interval_seconds)
        except TimeoutError:
            continue
