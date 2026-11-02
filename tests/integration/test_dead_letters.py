from datetime import UTC, datetime
from uuid import uuid4

from meshcompute.coordinator.db.tables import JobRecord, TaskRecord, WorkerRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.task_service import TaskService


def test_exhausted_task_is_retained_in_dead_letter_queue():
    job_id, worker_id, task_id = uuid4(), uuid4(), uuid4()
    with UnitOfWork() as uow:
        uow.session.add_all(
            [
                JobRecord(
                    id=job_id,
                    job_type="word_count",
                    input_ref="dead-letter-test.txt",
                    chunk_count=1,
                    status="RUNNING",
                ),
                WorkerRecord(
                    id=worker_id,
                    name=f"dead-letter-{worker_id}",
                    status="ACTIVE",
                    current_task_id=task_id,
                ),
            ]
        )
        uow.session.flush()
        uow.session.add(
            TaskRecord(
                id=task_id,
                job_id=job_id,
                task_index=0,
                payload={"input_ref": "private/sample.txt"},
                status="RUNNING",
                attempt=1,
                max_attempts=1,
                worker_id=worker_id,
            )
        )
        uow.commit()

    with UnitOfWork() as uow:
        TaskService().fail(uow, task_id, worker_id, 1, "synthetic terminal failure")

    with UnitOfWork() as uow:
        rows = uow.tasks.dead_letters()
        row = next(item for item in rows if item.task_id == task_id)
        assert row.job_id == job_id
        assert row.payload == {"input_ref": "private/sample.txt"}
        assert row.attempts == 1
        assert row.reason == "synthetic terminal failure"
        assert row.created_at <= datetime.now(UTC)
