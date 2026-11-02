"""Worker registration and liveness endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends

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


@router.get("", response_model=list[WorkerView])
def list_workers(uow: UnitOfWork = Depends(get_uow)):
    """List worker heartbeat and current lease status for operations."""
    return WorkerService().list(uow)


@router.post("/register", response_model=WorkerRegistered)
def register_worker(request: WorkerRegistration, uow: UnitOfWork = Depends(get_uow)):
    """Register an HTTP-only worker process."""
    return WorkerService().register(uow, request.name)


@router.post("/{worker_id}/heartbeat", response_model=WorkerHeartbeatResponse)
def heartbeat(worker_id: UUID, request: HeartbeatRequest, uow: UnitOfWork = Depends(get_uow)):
    """Refresh liveness and extend the current fenced task lease."""
    return WorkerService().heartbeat(uow, worker_id, request.task_id, request.attempt)
