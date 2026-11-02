"""Job submission and read-only job endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, status

from meshcompute.coordinator.api.auth import require_admin
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.api.schemas import (
    JobAccepted,
    JobPage,
    JobSubmission,
    JobView,
    TaskPageItem,
)
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post(
    "",
    response_model=JobAccepted,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_admin)],
)
def submit_job(
    request: JobSubmission,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=256),
    uow: UnitOfWork = Depends(get_uow),
):
    """Accept a registered job and return its identifier immediately."""
    return JobService().submit(uow, request, idempotency_key)


@router.get("", response_model=JobPage)
def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    uow: UnitOfWork = Depends(get_uow),
):
    """List recent jobs with task-state counts."""
    return JobService().list(uow, limit, offset)


@router.get("/{job_id}/tasks", response_model=list[TaskPageItem])
def get_job_tasks(job_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    """Show per-task attempt and lease state."""
    return JobService().tasks(uow, job_id)


@router.get("/{job_id}/dag")
def get_job_dag(job_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    """Return dependency lineage and a unit-cost critical-path estimate."""
    return JobService().dag(uow, job_id)


@router.get("/{job_id}", response_model=JobView)
def get_job(job_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    """Return progress counts for a submitted job."""
    return JobService().get(uow, job_id)


@router.get("/{job_id}/result")
def get_job_result(job_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    """Return the merged result only after every task succeeds."""
    return JobService().result(uow, job_id)


@router.post("/{job_id}/cancel", dependencies=[Depends(require_admin)])
def cancel_job(job_id: UUID, uow: UnitOfWork = Depends(get_uow)):
    """Cancel a submitted or running job."""
    return JobService().cancel(uow, job_id)
