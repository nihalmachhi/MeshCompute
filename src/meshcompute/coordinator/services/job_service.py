"""Job submission, admission control, and read-side job summaries."""

import hashlib
import json
import threading
from datetime import timedelta
from uuid import UUID, uuid4

from meshcompute.coordinator.api.schemas import JobSubmission
from meshcompute.coordinator.db.tables import JobRecord, TaskRecord
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.domain.dag import Stage, plan_dag
from meshcompute.coordinator.domain.models import JobStatus, TaskStatus
from meshcompute.core.clock import Clock, SystemClock
from meshcompute.core.errors import BackpressureError, ConflictError, InvalidDAGError, NotFoundError
from meshcompute.core.settings import Settings, get_settings
from meshcompute.handlers.registry import get_handler

_ADMISSION_LOCK = threading.Lock()


class JobService:
    """Validate job intent and persist its deterministic task plan."""

    def __init__(self, settings: Settings | None = None, clock: Clock | None = None):
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()

    def submit(
        self, uow: UnitOfWork, request: JobSubmission, idempotency_key: str | None = None
    ) -> dict:
        """Split a registered handler workload and enqueue within queue limits."""
        key_hash = None
        request_hash = None
        if idempotency_key is not None:
            if not idempotency_key.strip():
                raise ConflictError("Idempotency-Key must not be empty")
            key_hash = hashlib.sha256(idempotency_key.encode()).hexdigest()
            request_bytes = json.dumps(
                request.model_dump(mode="json"), sort_keys=True, separators=(",", ":")
            ).encode()
            request_hash = hashlib.sha256(request_bytes).hexdigest()
            uow.jobs.lock_idempotency_key(key_hash)
            prior = uow.jobs.get_idempotency_key(key_hash)
            if prior is not None:
                if prior.request_hash != request_hash:
                    raise ConflictError("Idempotency-Key was already used for a different request")
                job = uow.jobs.get(prior.job_id)
                if job is None:
                    raise ConflictError("Idempotency-Key refers to an expired job")
                uow.commit()
                return {"job_id": job.id, "status": job.status, "task_count": job.chunk_count}

        handler = get_handler(request.job_type)
        chunks = handler.split(request.input_ref, request.options)
        if not chunks:
            raise ValueError("job input produced no tasks")
        dependencies = request.task_dependencies
        try:
            if len(set(dependencies)) != len(dependencies):
                raise ValueError("dependency edges must be unique")
            if any(
                source < 0
                or target < 0
                or source >= len(chunks)
                or target >= len(chunks)
                or source == target
                for source, target in dependencies
            ):
                raise ValueError("dependency task index is outside the planned task range")
            plan_dag(
                [
                    Stage(
                        str(index),
                        1.0,
                        tuple(str(source) for source, target in dependencies if target == index),
                    )
                    for index in range(len(chunks))
                ]
            )
        except ValueError as exc:
            raise InvalidDAGError(str(exc)) from exc
        with _ADMISSION_LOCK:
            if uow.tasks.pending_count() + len(chunks) > self.settings.max_pending_tasks:
                raise BackpressureError("pending task limit reached")
        job = JobRecord(
            id=uuid4(),
            job_type=request.job_type,
            input_ref=request.input_ref,
            chunk_count=len(chunks),
            status=JobStatus.SUBMITTED.value,
            priority=request.priority,
        )
        tasks = [
            TaskRecord(
                job_id=job.id,
                task_index=index,
                payload=payload,
                required_capabilities=request.required_capabilities,
                status=TaskStatus.PENDING.value,
                attempt=0,
                max_attempts=self.settings.max_task_attempts,
            )
            for index, payload in enumerate(chunks)
        ]
        uow.jobs.add(job, tasks, dependencies)
        if key_hash is not None and request_hash is not None:
            uow.jobs.add_idempotency_key(key_hash, request_hash, job.id)
        uow.enqueue_event(
            {"type": "job.submitted", "job_id": str(job.id), "task_count": len(tasks)}
        )
        uow.commit()
        return {"job_id": job.id, "status": job.status, "task_count": len(tasks)}

    def get(self, uow: UnitOfWork, job_id: UUID) -> dict:
        """Return a job and grouped task-state counts."""
        job = uow.jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        counts = uow.jobs.task_counts(job_id)
        return {
            "id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "task_count": job.chunk_count,
            "tasks_by_state": counts,
            "created_at": job.created_at,
            "finished_at": job.finished_at,
        }

    def tasks(self, uow: UnitOfWork, job_id: UUID) -> list[dict]:
        """Return task-level details for the read-only job timeline."""
        from meshcompute.coordinator.services.task_query_service import TaskQueryService

        return TaskQueryService().list_for_job(uow, job_id)

    def result(self, uow: UnitOfWork, job_id: UUID) -> dict:
        """Return an aggregated result only after successful completion."""
        job = uow.jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        if job.status != JobStatus.COMPLETED.value:
            from meshcompute.core.errors import ConflictError

            raise ConflictError("job result is not ready")
        return {"job_id": job.id, "job_type": job.job_type, "result": job.result}

    def dag(self, uow: UnitOfWork, job_id: UUID) -> dict:
        """Return the persisted task graph and its unit-cost critical path."""
        job = uow.jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        edges = uow.tasks.dependencies_for_job(job_id)
        stages = [
            Stage(
                str(index), 1.0, tuple(str(source) for source, target in edges if target == index)
            )
            for index in range(job.chunk_count)
        ]
        plan = plan_dag(stages)
        return {
            "job_id": job.id,
            "task_count": job.chunk_count,
            "dependencies": edges,
            "topological_order": [int(item) for item in plan.topological_order],
            "critical_path": [int(item) for item in plan.critical_path],
            "estimated_seconds": plan.estimated_seconds,
        }

    def cancel(self, uow: UnitOfWork, job_id: UUID) -> dict:
        """Cancel a submitted or running job."""
        job = uow.jobs.get(job_id)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        # Match completion's task-then-job lock order and invalidate active attempts.
        tasks = uow.tasks.cancel_for_job(job_id)
        finished_at = self.clock.now()
        for task in tasks:
            worker_id = task.worker_id
            task.attempt += 1
            uow.tasks.set_status(task, TaskStatus.CANCELLED, finished_at, worker_id)
            if worker_id is not None:
                worker = uow.workers.get(worker_id, lock=True)
                if worker is not None and worker.current_task_id == task.id:
                    worker.current_task_id = None
        job = uow.jobs.get(job_id, lock=True)
        if job is None:
            raise NotFoundError(f"job {job_id} not found")
        uow.jobs.set_status(job, JobStatus.CANCELLED, finished_at)
        job.expires_at = finished_at + timedelta(seconds=self.settings.result_retention_seconds)
        uow.enqueue_event({"type": "job.cancelled", "job_id": str(job.id)})
        uow.commit()
        return {"job_id": job.id, "status": job.status}

    def list(self, uow: UnitOfWork, limit: int = 50, offset: int = 0) -> dict:
        """Return a bounded page of recent jobs with progress counts."""
        items = []
        for job in uow.jobs.list(limit, offset):
            items.append(
                {
                    "id": job.id,
                    "job_type": job.job_type,
                    "status": job.status,
                    "task_count": job.chunk_count,
                    "tasks_by_state": uow.jobs.task_counts(job.id),
                    "created_at": job.created_at,
                    "finished_at": job.finished_at,
                }
            )
        return {"items": items, "limit": limit, "offset": offset}
