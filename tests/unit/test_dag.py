"""Tests for dependency ordering and critical-path estimates."""

import pytest

from meshcompute.coordinator.api.schemas import JobSubmission
from meshcompute.coordinator.domain.dag import Stage, plan_dag
from meshcompute.coordinator.services import job_service
from meshcompute.coordinator.services.job_service import JobService
from meshcompute.core.errors import InvalidDAGError


def test_plan_dag_returns_topological_order_and_hand_computed_critical_path() -> None:
    plan = plan_dag(
        [
            Stage("map", 2),
            Stage("extract", 3),
            Stage("join", 4, ("map", "extract")),
            Stage("report", 1, ("join",)),
        ]
    )

    assert plan.topological_order.index("map") < plan.topological_order.index("join")
    assert plan.topological_order.index("extract") < plan.topological_order.index("join")
    assert plan.critical_path == ("extract", "join", "report")
    assert plan.estimated_seconds == 8


def test_plan_dag_rejects_cycles_and_unknown_dependencies() -> None:
    with pytest.raises(ValueError, match="cycle"):
        plan_dag([Stage("a", 1, ("b",)), Stage("b", 1, ("a",))])
    with pytest.raises(ValueError, match="invalid dependency"):
        plan_dag([Stage("a", 1, ("missing",))])


def test_job_submission_rejects_dependency_cycle_before_persistence(monkeypatch) -> None:
    class Handler:
        def split(self, input_ref, options):
            return [{"part": index} for index in range(3)]

    monkeypatch.setattr(job_service, "get_handler", lambda _name: Handler())
    request = JobSubmission(
        job_type="word_count",
        input_ref="synthetic.txt",
        task_dependencies=[(0, 1), (1, 2), (2, 0)],
    )

    with pytest.raises(InvalidDAGError, match="cycle"):
        JobService().submit(object(), request)
