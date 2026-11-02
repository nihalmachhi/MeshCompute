"""Small, deterministic DAG planning primitives shared by the API and simulator."""

from collections import defaultdict, deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Stage:
    """One named stage with an estimated duration and prerequisite stage ids."""

    stage_id: str
    duration: float
    dependencies: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DagPlan:
    """Validated stage order and longest dependency path in a submitted DAG."""

    topological_order: tuple[str, ...]
    critical_path: tuple[str, ...]
    estimated_seconds: float


def plan_dag(stages: list[Stage]) -> DagPlan:
    """Validate stage references/cycles and calculate the duration-weighted critical path."""
    by_id = {stage.stage_id: stage for stage in stages}
    if not stages or len(by_id) != len(stages):
        raise ValueError("a DAG must contain uniquely named stages")
    if any(not stage.stage_id or stage.duration < 0 for stage in stages):
        raise ValueError("stage ids must be non-empty and durations non-negative")

    indegree = {stage_id: 0 for stage_id in by_id}
    children: dict[str, list[str]] = defaultdict(list)
    for stage in stages:
        for dependency in stage.dependencies:
            if dependency not in by_id or dependency == stage.stage_id:
                raise ValueError(f"invalid dependency {dependency!r} for {stage.stage_id!r}")
            children[dependency].append(stage.stage_id)
            indegree[stage.stage_id] += 1

    ready = deque(sorted(stage_id for stage_id, degree in indegree.items() if degree == 0))
    order: list[str] = []
    longest: dict[str, float] = {}
    parent: dict[str, str | None] = {}
    while ready:
        stage_id = ready.popleft()
        order.append(stage_id)
        stage = by_id[stage_id]
        if not stage.dependencies:
            longest[stage_id] = stage.duration
            parent[stage_id] = None
        else:
            predecessor = max(stage.dependencies, key=lambda item: longest[item])
            longest[stage_id] = longest[predecessor] + stage.duration
            parent[stage_id] = predecessor
        for child in sorted(children[stage_id]):
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)

    if len(order) != len(stages):
        raise ValueError("stage dependencies contain a cycle")
    end_id = max(order, key=lambda item: longest[item])
    path: list[str] = []
    current: str | None = end_id
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    return DagPlan(tuple(order), tuple(path), longest[path[-1]])
