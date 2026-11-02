from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import select

from meshcompute.coordinator.db.tables import JobRecord, TaskRecord, WorkerRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.scheduling import effective_priority


def test_aged_priority_prevents_a_low_priority_job_from_waiting_forever():
    now = datetime.now(UTC)
    aged_low_priority = effective_priority(0, now - timedelta(seconds=120), now, 30)
    new_high_priority = effective_priority(3, now, now, 30)
    assert aged_low_priority > new_high_priority


def test_claim_only_assigns_tasks_supported_by_worker_capabilities():
    job_id, worker_id = uuid4(), uuid4()
    with UnitOfWork() as uow:
        uow.session.add_all(
            [
                JobRecord(
                    id=job_id,
                    job_type="word_count",
                    input_ref="gpu",
                    chunk_count=1,
                    status="SUBMITTED",
                ),
                WorkerRecord(
                    id=worker_id,
                    name=f"capability-{worker_id}",
                    status="ACTIVE",
                    capabilities=["python"],
                ),
            ]
        )
        uow.session.flush()
        task = TaskRecord(
            job_id=job_id,
            task_index=0,
            payload={},
            required_capabilities=["python", "gpu"],
            status="PENDING",
            attempt=0,
            max_attempts=3,
        )
        uow.session.add(task)
        uow.commit()

    with UnitOfWork() as uow:
        unsupported = uow.session.scalar(
            select(TaskRecord).where(
                TaskRecord.id == task.id,
                TaskRecord.required_capabilities.contained_by(["python"]),
            )
        )
        supported = uow.session.scalar(
            select(TaskRecord).where(
                TaskRecord.id == task.id,
                TaskRecord.required_capabilities.contained_by(["python", "gpu"]),
            )
        )
        assert unsupported is None
        assert supported is not None and supported.job_id == job_id
