"""Worker registration and heartbeat application services."""

import hashlib
import secrets
from uuid import UUID

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.lease_manager import LeaseManager
from meshcompute.core.clock import Clock, SystemClock
from meshcompute.core.settings import Settings, get_settings


class WorkerService:
    """Manage coordinator-side worker lifecycle records."""

    def __init__(self, settings: Settings | None = None, clock: Clock | None = None):
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()

    def register(self, uow: UnitOfWork, name: str, capabilities: list[str] | None = None) -> dict:
        """Create a worker identity and expose the configured heartbeat cadence."""
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        worker = uow.workers.register(name, self.clock.now(), token_hash, capabilities)
        uow.enqueue_event(
            {"type": "worker.registered", "worker_id": str(worker.id), "name": worker.name}
        )
        uow.commit()
        return {
            "worker_id": worker.id,
            "heartbeat_interval_seconds": self.settings.heartbeat_interval_seconds,
            "worker_token": token,
        }

    def list(self, uow: UnitOfWork) -> list[dict]:
        """Return read-only worker health and lease information."""
        now = self.clock.now()
        return [
            {
                "worker_id": worker.id,
                "name": worker.name,
                "status": worker.status,
                "last_heartbeat_at": worker.last_heartbeat_at,
                "heartbeat_age_seconds": max(
                    0, int((now - worker.last_heartbeat_at).total_seconds())
                ),
                "current_task_id": worker.current_task_id,
                "capabilities": worker.capabilities,
            }
            for worker in uow.workers.all()
        ]

    def heartbeat(
        self, uow: UnitOfWork, worker_id: UUID, task_id: UUID | None, attempt: int | None
    ) -> dict:
        """Delegate liveness and lease fencing to the lease manager."""
        return LeaseManager(self.settings, self.clock).heartbeat(uow, worker_id, task_id, attempt)
