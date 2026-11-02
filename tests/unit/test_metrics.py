"""Prometheus exposition includes queue, worker, failure, lease, and runtime data."""

from uuid import uuid4

from meshcompute.coordinator.services.metrics_service import prometheus_text


def test_prometheus_metrics_render_task_queue_and_latency_histogram():
    job_id = uuid4()
    summary = {
        "workers": {"ACTIVE": 2, "STALE": 1},
        "completed_last_minute": 7,
        "retries": 2,
        "failures": 1,
        "lease_expiries": 3,
    }

    rendered = prometheus_text(summary, [(job_id, 4, 5)], [5, 50, 200, 10_000])

    assert f'meshcompute_queue_depth{{job_id="{job_id}",priority="4"}} 5' in rendered
    assert 'meshcompute_workers{status="active"} 2' in rendered
    assert "meshcompute_lease_expiries_total 3" in rendered
    assert 'meshcompute_task_duration_milliseconds_bucket{le="50"} 2' in rendered
    assert "meshcompute_task_duration_milliseconds_count 4" in rendered
