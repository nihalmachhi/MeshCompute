from datetime import UTC, datetime, timedelta
from uuid import uuid4

from meshcompute.coordinator.db.tables import JobRecord, TaskRecord, WorkerRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.job_service import JobService


def test_cancel_fences_claimed_task_and_clears_worker_lease():
    now = datetime.now(UTC)
    job_id, worker_id = uuid4(), uuid4()
    pending_id, running_id = uuid4(), uuid4()
    with UnitOfWork() as uow:
        job = JobRecord(
            id=job_id, job_type="word_count", input_ref="x", chunk_count=2, status="RUNNING"
        )
        worker = WorkerRecord(
            id=worker_id, name=f"cancel-{worker_id}", status="ACTIVE", current_task_id=running_id
        )
        pending = TaskRecord(
            id=pending_id,
            job_id=job_id,
            task_index=0,
            payload={},
            status="PENDING",
            attempt=0,
            max_attempts=3,
        )
        running = TaskRecord(
            id=running_id,
            job_id=job_id,
            task_index=1,
            payload={},
            status="RUNNING",
            attempt=1,
            max_attempts=3,
            worker_id=worker_id,
            lease_expires_at=now + timedelta(minutes=1),
        )
        uow.session.add_all([job, worker])
        uow.session.flush()
        uow.session.add_all([pending, running])
        uow.commit()

    with UnitOfWork() as uow:
        JobService().cancel(uow, job_id)

    with UnitOfWork() as uow:
        job = uow.jobs.get(job_id)
        tasks = uow.tasks.list_by_job(job_id)
        worker = uow.workers.get(worker_id)
        assert job.status == "CANCELLED"
        assert all(task.status == "CANCELLED" for task in tasks)
        assert next(task for task in tasks if task.id == running_id).attempt == 2
        assert worker.current_task_id is None
