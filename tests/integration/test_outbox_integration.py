import asyncio
from uuid import uuid4

import psycopg
import pytest

from meshcompute.coordinator.background.outbox_dispatcher import run_outbox_dispatcher
from meshcompute.coordinator.db.tables import OutboxEventRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.events import event_hub
from meshcompute.core.settings import get_settings


def test_outbox_event_is_visible_after_transaction_commit():
    event_id = None
    payload = {"type": "integration.test", "nonce": str(uuid4())}
    connection_url = get_settings().sync_database_url.replace(
        "postgresql+psycopg://", "postgresql://"
    )
    with psycopg.connect(connection_url, autocommit=True) as listener:
        listener.execute("LISTEN meshcompute_events")
        with UnitOfWork() as uow:
            record = uow.enqueue_event(payload)
            event_id = record.id
            assert list(listener.notifies(timeout=0.1, stop_after=1)) == []
            uow.commit()
        notifications = list(listener.notifies(timeout=2, stop_after=1))
        assert notifications
        assert notifications[0].payload == str(event_id)

    with UnitOfWork() as uow:
        stored = uow.session.get(OutboxEventRecord, event_id)
        assert stored is not None
        assert stored.payload == payload
        uow.session.delete(stored)
        uow.commit()


@pytest.mark.asyncio
async def test_listener_fans_out_committed_events_from_the_durable_cursor():
    stop = asyncio.Event()
    listener = asyncio.create_task(run_outbox_dispatcher(stop, interval_seconds=0.1))
    try:
        await asyncio.sleep(0.25)
        async with event_hub.subscribe() as queue:
            payload = {"type": "listener.test", "nonce": str(uuid4())}
            with UnitOfWork() as uow:
                uow.enqueue_event(payload)
                uow.commit()
            received = await asyncio.wait_for(queue.get(), timeout=3)
            assert received == payload
    finally:
        stop.set()
        await asyncio.wait_for(listener, timeout=3)
