from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from meshcompute.coordinator.services.task_service import TaskService
from meshcompute.core.errors import PayloadTooLargeError
from meshcompute.core.settings import Settings


def test_completion_rejects_results_over_the_configured_limit():
    task = SimpleNamespace(
        id=uuid4(),
        job_id=uuid4(),
        status="RUNNING",
        attempt=1,
        worker_id=uuid4(),
        lease_expires_at=datetime.now(UTC) + timedelta(minutes=1),
    )
    uow = MagicMock()
    uow.tasks.get.return_value = task
    service = TaskService(settings=Settings(max_result_bytes=1024))
    with pytest.raises(PayloadTooLargeError):
        service.complete(uow, task.id, task.worker_id, 1, {"value": "x" * 2000}, 1.0)
    uow.tasks.set_status.assert_not_called()
