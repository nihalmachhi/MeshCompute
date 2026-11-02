"""Operational summaries computed from coordinator repositories."""

from collections.abc import Sequence
from datetime import timedelta
from math import ceil

from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.core.clock import Clock, SystemClock
from meshcompute.core.settings import Settings, get_settings


class MetricsService:
    """Expose real queue, worker, retry, throughput, and duration counts."""

    def __init__(self, settings: Settings | None = None, clock: Clock | None = None):
        self.settings = settings or get_settings()
        self.clock = clock or SystemClock()

    def summary(self, uow: UnitOfWork) -> dict:
        """Return dashboard metrics using one consistent unit of work."""
        now = self.clock.now()
        workers = uow.workers.active_and_stale_counts(
            now - timedelta(seconds=self.settings.lease_ttl_seconds * 2)
        )
        queue_size = uow.tasks.pending_count()
        results = uow.results.summary(now - timedelta(minutes=1))
        active_workers = workers.get("ACTIVE", 0)
        completions_per_worker_second = (
            results["completed_last_minute"] / 60 / max(active_workers, 1)
        )
        needed_workers = (
            ceil(queue_size / (completions_per_worker_second * 60))
            if completions_per_worker_second > 0
            else None
        )
        return {
            "workers": workers,
            "queue_size": queue_size,
            **results,
            "autoscaling_hint": {
                "target_drain_seconds": 60,
                "suggested_additional_workers": (
                    max(0, needed_workers - active_workers) if needed_workers is not None else None
                ),
                "basis": (
                    "recent completions per active worker; heuristic, not a capacity guarantee"
                ),
            },
        }


def prometheus_text(
    summary: dict,
    queue_by_job: Sequence[tuple[object, int, int]],
    durations_ms: list[float],
) -> str:
    """Format the coordinator summary and queue/runtime samples as Prometheus text."""
    lines = [
        "# HELP meshcompute_queue_depth Pending tasks by job and priority.",
        "# TYPE meshcompute_queue_depth gauge",
    ]
    for job_id, priority, count in queue_by_job:
        lines.append(f'meshcompute_queue_depth{{job_id="{job_id}",priority="{priority}"}} {count}')
    lines.extend(
        [
            "# HELP meshcompute_workers Workers by reported status.",
            "# TYPE meshcompute_workers gauge",
        ]
    )
    for status, count in sorted(summary["workers"].items()):
        lines.append(f'meshcompute_workers{{status="{status.lower()}"}} {count}')
    lines.extend(
        [
            "# TYPE meshcompute_tasks_completed_last_minute gauge",
            f"meshcompute_tasks_completed_last_minute {summary['completed_last_minute']}",
        ]
    )
    for name in ("retries", "failures", "lease_expiries"):
        lines.extend(
            [
                f"# TYPE meshcompute_{name}_total counter",
                f"meshcompute_{name}_total {summary[name]}",
            ]
        )
    lines.extend(
        [
            "# HELP meshcompute_task_duration_milliseconds Task runtimes over the last 24 hours.",
            "# TYPE meshcompute_task_duration_milliseconds histogram",
        ]
    )
    for boundary in (10, 50, 100, 500, 1_000, 5_000):
        count = sum(duration <= boundary for duration in durations_ms)
        lines.append(f'meshcompute_task_duration_milliseconds_bucket{{le="{boundary}"}} {count}')
    lines.extend(
        [
            f'meshcompute_task_duration_milliseconds_bucket{{le="+Inf"}} {len(durations_ms)}',
            f"meshcompute_task_duration_milliseconds_sum {sum(durations_ms):.3f}",
            f"meshcompute_task_duration_milliseconds_count {len(durations_ms)}",
            "",
        ]
    )
    return "\n".join(lines)
