from datetime import UTC, datetime, timedelta
from uuid import uuid4

from meshcompute.coordinator.db.tables import JobRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork


def test_expired_terminal_job_is_purged():
    job_id = uuid4()
    now = datetime.now(UTC)
    with UnitOfWork() as uow:
        uow.session.add(
            JobRecord(
                id=job_id,
                job_type="word_count",
                input_ref="x",
                chunk_count=0,
                status="COMPLETED",
                expires_at=now - timedelta(seconds=1),
            )
        )
        uow.commit()
    with UnitOfWork() as uow:
        assert uow.jobs.purge_expired(now) == 1
        uow.commit()
    with UnitOfWork() as uow:
        assert uow.jobs.get(job_id) is None
