"""Operational dashboard summary endpoint."""

from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from meshcompute.coordinator.api.deps import get_uow
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services.metrics_service import MetricsService, prometheus_text
from meshcompute.core.clock import SystemClock

router = APIRouter(tags=["metrics"])


@router.get("/metrics/summary")
def metrics_summary(uow: UnitOfWork = Depends(get_uow)):
    """Return worker, queue, retry, throughput, and duration metrics."""
    return MetricsService().summary(uow)


@router.get("/metrics", response_class=PlainTextResponse)
def prometheus_metrics(uow: UnitOfWork = Depends(get_uow)):
    """Expose queue, worker, retry, failure, and task-duration metrics for scraping."""
    now = SystemClock().now()
    service = MetricsService()
    summary = service.summary(uow)
    return prometheus_text(
        summary,
        uow.tasks.pending_by_job_priority(),
        uow.results.durations_since(now - timedelta(hours=24)),
    )
