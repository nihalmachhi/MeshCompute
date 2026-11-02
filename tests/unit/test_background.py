from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from meshcompute.coordinator.background import lease_reaper, outbox_dispatcher


@pytest.mark.asyncio
async def test_reaper_runs_sync_database_work_outside_active_event_loop(monkeypatch):
    uow = MagicMock()
    manager = MagicMock()
    manager.reap.return_value = 3

    class Context:
        def __enter__(self):
            return uow

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(lease_reaper, "UnitOfWork", Context)
    monkeypatch.setattr(lease_reaper, "LeaseManager", lambda: manager)
    assert await lease_reaper._reap_once() == 3


def test_outbox_dispatch_publishes_from_a_process_local_cursor(monkeypatch):
    record = MagicMock(payload={"type": "task.completed"}, created_at=datetime.now(UTC), id=uuid4())
    uow = MagicMock()
    uow.outbox.after_cursor.return_value = [record]

    class Context:
        def __enter__(self):
            return uow

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(outbox_dispatcher, "UnitOfWork", Context)
    monkeypatch.setattr(outbox_dispatcher.event_hub, "publish", MagicMock())
    count, cursor = outbox_dispatcher.dispatch_since(None)
    assert count == 1
    assert cursor == (record.created_at, record.id)
    outbox_dispatcher.event_hub.publish.assert_called_once_with(record.payload)
