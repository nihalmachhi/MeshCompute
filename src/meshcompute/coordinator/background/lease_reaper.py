"""Periodic lease expiry and stale-worker maintenance."""
import asyncio
import logging
from meshcompute.common.settings import get_settings
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.lease_manager import LeaseManager

logger=logging.getLogger(__name__)
def _reap_once() -> int:
    """Run one transactional reaper pass in a worker thread."""
    async def run():
        with UnitOfWork() as uow:return await LeaseManager().reap(uow)
    return asyncio.run(run())
async def run_reaper(stop: asyncio.Event) -> None:
    """Reap expired leases on a configurable interval until shutdown."""
    settings=get_settings()
    while not stop.is_set():
        try:
            count=await asyncio.to_thread(_reap_once)
            if count:logger.info("expired leases recovered",extra={"event":"lease_reaped","count":count})
        except Exception:
            logger.exception("lease reaper failed")
        try:await asyncio.wait_for(stop.wait(),timeout=settings.reaper_interval_seconds)
        except TimeoutError:continue
