"""Operational dashboard summary endpoint."""
from fastapi import APIRouter,Depends
from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.metrics_service import MetricsService

router=APIRouter(tags=["metrics"])
service=MetricsService()
@router.get("/metrics/summary")
def metrics_summary(uow: UnitOfWork=Depends(get_uow)):
    """Return worker, queue, retry, throughput, and duration metrics."""
    return service.summary(uow)
