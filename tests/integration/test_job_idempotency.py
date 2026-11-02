from uuid import UUID

import pytest

from meshcompute.coordinator.api.schemas import JobSubmission
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.services import job_service
from meshcompute.coordinator.services.job_service import JobService
from meshcompute.core.errors import ConflictError


class FakeHandler:
    def split(self, input_ref, options):
        return [{"part": 0}, {"part": 1}]


def test_job_submission_replays_by_key_and_rejects_request_mismatch(monkeypatch):
    monkeypatch.setattr(job_service, "get_handler", lambda _name: FakeHandler())
    request = JobSubmission(job_type="word_count", input_ref="idempotent.txt")
    with UnitOfWork() as uow:
        first = JobService().submit(uow, request, "same-client-retry")

    with UnitOfWork() as uow:
        replay = JobService().submit(uow, request, "same-client-retry")
    assert replay["job_id"] == first["job_id"]
    assert replay["task_count"] == first["task_count"] == 2

    changed = request.model_copy(update={"input_ref": "different.txt"})
    with UnitOfWork() as uow, pytest.raises(ConflictError, match="different request"):
        JobService().submit(uow, changed, "same-client-retry")

    assert isinstance(first["job_id"], UUID)
