"""Administrative dead-letter queue inspection endpoint."""

from fastapi import APIRouter, Depends, Query

from meshcompute.coordinator.api.auth import require_admin
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.api.schemas import DeadLetterView
from meshcompute.coordinator.db.unit_of_work import UnitOfWork

router = APIRouter(prefix="/dead-letters", tags=["dead letters"])


@router.get("", response_model=list[DeadLetterView], dependencies=[Depends(require_admin)])
def list_dead_letters(
    limit: int = Query(default=50, ge=1, le=200), uow: UnitOfWork = Depends(get_uow)
):
    """List a bounded page of exhausted tasks for an authenticated administrator."""
    return uow.tasks.dead_letters(limit)
