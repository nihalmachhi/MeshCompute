"""The only worker module that communicates with the coordinator API."""

from typing import Any
from uuid import UUID

import httpx

from meshcompute.core.settings import get_settings


class CoordinatorClient:
    """Typed HTTP adapter with a shared timeout-configured client."""

    def __init__(self, base_url: str | None = None):
        settings = get_settings()
        headers = (
            {"Authorization": f"Bearer {settings.admin_token}"} if settings.admin_token else {}
        )
        self._client = httpx.Client(
            base_url=base_url or settings.coordinator_url, timeout=10.0, headers=headers
        )
        self._token: str | None = None

    def close(self) -> None:
        """Close the worker HTTP connection pool."""
        self._client.close()

    def register(self, name: str) -> dict[str, Any]:
        """Register the worker process and receive its UUID."""
        result = self._post("/api/v1/workers/register", {"name": name})
        self._token = result.get("worker_token")
        if self._token:
            self._client.headers["Authorization"] = f"Bearer {self._token}"
        return result

    def heartbeat(
        self, worker_id: UUID, task_id: UUID | None, attempt: int | None
    ) -> dict[str, Any]:
        """Report liveness and renew one task lease."""
        return self._post(
            f"/api/v1/workers/{worker_id}/heartbeat",
            {"task_id": str(task_id) if task_id else None, "attempt": attempt},
        )

    def claim(self, worker_id: UUID) -> dict[str, Any] | None:
        """Request the next FIFO task; 204 means the queue is empty."""
        response = self._client.post("/api/v1/tasks/claim", json={"worker_id": str(worker_id)})
        if response.status_code == 204:
            return None
        response.raise_for_status()
        return response.json()

    def start(self, task_id: UUID, worker_id: UUID, attempt: int) -> None:
        """Mark the claimed task as running."""
        self._post(
            f"/api/v1/tasks/{task_id}/start", {"worker_id": str(worker_id), "attempt": attempt}
        )

    def complete(
        self,
        task_id: UUID,
        worker_id: UUID,
        attempt: int,
        output: dict[str, Any],
        duration_ms: float,
    ) -> dict[str, Any]:
        """Submit one result with its attempt fencing token."""
        return self._post(
            f"/api/v1/tasks/{task_id}/complete",
            {
                "worker_id": str(worker_id),
                "attempt": attempt,
                "output": output,
                "duration_ms": duration_ms,
            },
        )

    def fail(self, task_id: UUID, worker_id: UUID, attempt: int, error: str) -> dict[str, Any]:
        """Report a retryable handler failure."""
        return self._post(
            f"/api/v1/tasks/{task_id}/fail",
            {"worker_id": str(worker_id), "attempt": attempt, "error": error[:900]},
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send one JSON POST and raise on non-success responses."""
        response = self._client.post(path, json=payload)
        response.raise_for_status()
        return response.json()
