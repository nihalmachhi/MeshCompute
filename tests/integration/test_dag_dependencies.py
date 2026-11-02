from datetime import UTC, datetime, timedelta
from uuid import uuid4

from meshcompute.coordinator.db.tables import (
    JobRecord,
    TaskDependencyRecord,
    TaskRecord,
    WorkerRecord,
)
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.models import TaskStatus


def test_claim_releases_dependency_only_after_prerequisite_completes():
    job_id, worker_id = uuid4(), uuid4()
    prerequisite_id, dependent_id = uuid4(), uuid4()
    with UnitOfWork() as uow:
        uow.session.add_all(
            [
                JobRecord(
                    id=job_id,
                    job_type="word_count",
                    input_ref="x",
                    chunk_count=2,
                    status="SUBMITTED",
                ),
                WorkerRecord(id=worker_id, name=f"dag-{worker_id}", status="ACTIVE"),
            ]
        )
        uow.session.flush()
        uow.session.add_all(
            [
                TaskRecord(
                    id=prerequisite_id,
                    job_id=job_id,
                    task_index=0,
                    payload={},
                    status="PENDING",
                    attempt=0,
                    max_attempts=3,
                ),
                TaskRecord(
                    id=dependent_id,
                    job_id=job_id,
                    task_index=1,
                    payload={},
                    status="PENDING",
                    attempt=0,
                    max_attempts=3,
                ),
            ]
        )
        uow.session.flush()
        uow.session.add(
            TaskDependencyRecord(task_id=dependent_id, depends_on_task_id=prerequisite_id)
        )
        uow.commit()

    now = datetime.now(UTC)
    with UnitOfWork() as uow:
        first = uow.tasks.claim_next(worker_id, now, now + timedelta(seconds=30))
        assert first is not None and first.id == prerequisite_id
        first.status = TaskStatus.COMPLETED.value
        uow.commit()

    with UnitOfWork() as uow:
        second = uow.tasks.claim_next(worker_id, now, now + timedelta(seconds=30))
        assert second is not None and second.id == dependent_id


def test_terminal_failure_cancels_queued_descendants():
    job_id = uuid4()
    ids = [uuid4() for _ in range(3)]
    with UnitOfWork() as uow:
        uow.session.add(
            JobRecord(
                id=job_id,
                job_type="word_count",
                input_ref="x",
                chunk_count=3,
                status="RUNNING",
            )
        )
        uow.session.flush()
        tasks = [
            TaskRecord(
                id=task_id,
                job_id=job_id,
                task_index=index,
                payload={},
                status="FAILED" if index == 0 else "PENDING",
                attempt=1,
                max_attempts=1,
            )
            for index, task_id in enumerate(ids)
        ]
        uow.session.add_all(tasks)
        uow.session.flush()
        uow.session.add_all(
            [
                TaskDependencyRecord(task_id=ids[1], depends_on_task_id=ids[0]),
                TaskDependencyRecord(task_id=ids[2], depends_on_task_id=ids[1]),
            ]
        )
        uow.commit()

    with UnitOfWork() as uow:
        cancelled = uow.tasks.cancel_descendants(ids[0], datetime.now(UTC))
        assert {task.id for task in cancelled} == {ids[1], ids[2]}
        uow.commit()

    with UnitOfWork() as uow:
        assert [task.status for task in uow.tasks.list_by_job(job_id)] == [
            "FAILED",
            "CANCELLED",
            "CANCELLED",
        ]
