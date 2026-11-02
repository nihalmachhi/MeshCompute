from uuid import uuid4

from meshcompute.coordinator.db.tables import OutboxEventRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork


def test_outbox_event_is_visible_after_transaction_commit():
    event_id = None
    payload = {"type": "integration.test", "nonce": str(uuid4())}
    with UnitOfWork() as uow:
        record = uow.enqueue_event(payload)
        event_id = record.id
        uow.commit()

    with UnitOfWork() as uow:
        stored = uow.session.get(OutboxEventRecord, event_id)
        assert stored is not None
        assert stored.payload == payload
        uow.session.delete(stored)
        uow.commit()
