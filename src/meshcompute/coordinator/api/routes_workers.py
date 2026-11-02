"""Worker registration and liveness endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Header

from meshcompute.coordinator.api.auth import require_admin, verify_worker
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.api.schemas import (
    HeartbeatRequest,
    WorkerHeartbeatResponse,
    WorkerRegistered,
    WorkerRegistration,
    WorkerView,
)
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.worker_service import WorkerService

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=list[WorkerView], dependencies=[Depends(require_admin)])
def list_workers(uow: UnitOfWork = Depends(get_uow)):
    """List worker heartbeat and current lease status for operations."""
    return WorkerService().list(uow)


@router.post("/register", response_model=WorkerRegistered, dependencies=[Depends(require_admin)])
def register_worker(request: WorkerRegistration, uow: UnitOfWork = Depends(get_uow)):
    """Register an HTTP-only worker process."""
    return WorkerService().register(uow, request.name, request.capabilities)


@router.post("/{worker_id}/heartbeat", response_model=WorkerHeartbeatResponse)
def heartbeat(
    worker_id: UUID,
    request: HeartbeatRequest,
    authorization: str | None = Header(default=None),
    uow: UnitOfWork = Depends(get_uow),
):
    """Refresh liveness and extend the current fenced task lease."""
    verify_worker(uow, worker_id, authorization)
    return WorkerService().heartbeat(uow, worker_id, request.task_id, request.attempt)
