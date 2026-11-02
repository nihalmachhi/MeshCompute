from types import SimpleNamespace
from unittest.mock import MagicMock

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


def test_outbox_dispatch_publishes_and_marks_records(monkeypatch):
    record = SimpleNamespace(payload={"type": "task.completed"}, published_at=None)
    uow = MagicMock()
    uow.outbox.claim_pending.return_value = [record]

    class Context:
        def __enter__(self):
            return uow

        def __exit__(self, *_args):
            return False

    monkeypatch.setattr(outbox_dispatcher, "UnitOfWork", Context)
    monkeypatch.setattr(outbox_dispatcher.event_hub, "publish", MagicMock())
    assert outbox_dispatcher.dispatch_once() == 1
    outbox_dispatcher.event_hub.publish.assert_called_once_with(record.payload)
    assert record.published_at is not None
    uow.commit.assert_called_once()
