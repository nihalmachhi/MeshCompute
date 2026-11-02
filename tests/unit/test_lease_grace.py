from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from meshcompute.coordinator.services.task_service import TaskService
from meshcompute.core.clock import Clock


class FixedClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)


def test_expired_lease_can_complete_before_reaper_reassigns_it():
    worker_id = uuid4()
    task = SimpleNamespace(
        id=uuid4(),
        job_id=uuid4(),
        status="RUNNING",
        attempt=1,
        worker_id=worker_id,
        lease_expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )
    worker = SimpleNamespace(current_task_id=task.id)
    uow = MagicMock()
    uow.tasks.get.return_value = task
    uow.tasks.set_status.side_effect = lambda task_row, target, *_args: setattr(
        task_row, "status", target.value
    )
    uow.workers.get.return_value = worker
    service = TaskService(clock=FixedClock())
    result = service.complete(uow, task.id, worker_id, 1, {"count": 1}, 1.0)
    assert result["status"] == "COMPLETED"
    assert result["idempotent"] is False


def test_reassigned_attempt_still_rejects_the_stale_completion():
    import pytest

    from meshcompute.core.errors import ConflictError

    worker_id = uuid4()
    task = SimpleNamespace(
        id=uuid4(),
        status="ASSIGNED",
        attempt=2,
        worker_id=worker_id,
        lease_expires_at=datetime.now(UTC) + timedelta(minutes=1),
    )
    uow = MagicMock()
    uow.tasks.get.return_value = task
    with pytest.raises(ConflictError, match="stale task attempt"):
        TaskService(clock=FixedClock()).complete(uow, task.id, worker_id, 1, {}, 1.0)
