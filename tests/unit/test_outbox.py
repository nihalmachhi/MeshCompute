from unittest.mock import MagicMock

from meshcompute.coordinator.db.unit_of_work import UnitOfWork


def test_event_is_stored_in_transaction_and_not_published_inline(monkeypatch):
    session = MagicMock()
    transaction = MagicMock()
    session.begin.return_value = transaction
    monkeypatch.setattr(
        "meshcompute.coordinator.db.unit_of_work.session_factory",
        lambda: lambda: session,
    )
    published = []
    monkeypatch.setattr("meshcompute.coordinator.events.event_hub.publish", published.append)
    uow = UnitOfWork()
    uow.__enter__()
    uow.enqueue_event({"type": "job.submitted", "job_id": "job-1"})
    assert session.add.call_count == 1
    assert published == []
    uow.commit()
    assert published == []
    uow.__exit__(None, None, None)
