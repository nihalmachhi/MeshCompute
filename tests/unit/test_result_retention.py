from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

from meshcompute.coordinator.services.aggregation_service import AggregationService
from meshcompute.core.settings import Settings


def test_job_completion_sets_expiration_from_configured_retention(monkeypatch):
    now = datetime.now(UTC)
    job = SimpleNamespace(id=uuid4(), status="RUNNING", chunk_count=1, job_type="word_count")
    uow = MagicMock()
    uow.jobs.get.return_value = job
    uow.jobs.task_counts.return_value = {"COMPLETED": 1}
    uow.results.outputs_for_job.return_value = [{"word_counts": {"mesh": 1}}]
    monkeypatch.setattr(
        "meshcompute.handlers.registry.get_handler",
        lambda _job_type: SimpleNamespace(merge=lambda results: {"merged": results}),
    )
    service = AggregationService(
        clock=SimpleNamespace(now=lambda: now), settings=Settings(result_retention_seconds=120)
    )
    service.finalize_if_ready(uow, job.id)
    assert job.expires_at == now + timedelta(seconds=120)
