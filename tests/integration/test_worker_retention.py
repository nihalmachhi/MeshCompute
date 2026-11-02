from datetime import UTC, datetime, timedelta
from uuid import uuid4

from meshcompute.coordinator.db.tables import WorkerRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import WorkerStatus


def test_stale_worker_transitions_offline_then_is_purged():
    worker_id = uuid4()
    now = datetime.now(UTC)
    with UnitOfWork() as uow:
        worker = WorkerRecord(
            id=worker_id,
            name=f"retention-{worker_id}",
            status=WorkerStatus.STALE.value,
            registered_at=now - timedelta(days=2),
            last_heartbeat_at=now - timedelta(days=2),
        )
        uow.session.add(worker)
        uow.commit()

    with UnitOfWork() as uow:
        offline = uow.workers.offline_before(now - timedelta(days=1))
        worker = next(item for item in offline if item.id == worker_id)
        uow.workers.set_status(worker, WorkerStatus.OFFLINE)
        uow.commit()

    with UnitOfWork() as uow:
        assert uow.workers.purge_offline_before(now - timedelta(days=1)) == 1
        uow.commit()
    with UnitOfWork() as uow:
        assert uow.workers.get(worker_id) is None
