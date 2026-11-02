"""Operational summaries computed from coordinator repositories."""

from datetime import timedelta

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.core.clock import Clock, SystemClock
from meshcompute.core.settings import Settings, get_settings


class MetricsService:
    """Expose real queue, worker, retry, throughput, and duration counts."""

    def __init__(self, settings: Settings | None = None, clock: Clock | None = None):
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()

    def summary(self, uow: UnitOfWork) -> dict:
        """Return dashboard metrics using one consistent unit of work."""
        now = self.clock.now()
        return {
            "workers": uow.workers.active_and_stale_counts(
                now - timedelta(seconds=self.settings.lease_ttl_seconds * 2)
            ),
            "queue_size": uow.tasks.pending_count(),
            **uow.results.summary(now - timedelta(minutes=1)),
        }
