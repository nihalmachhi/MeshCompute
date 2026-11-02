"""Retry jitter is reproducible per attempt and grows within the configured cap."""

from datetime import UTC, datetime
from uuid import uuid4

from meshcompute.core.retry import retry_available_at


def test_retry_backoff_is_deterministic_jittered_and_exponentially_bounded():
    now = datetime(2026, 11, 2, tzinfo=UTC)
    task_id = uuid4()
    first = retry_available_at(task_id, 1, now, 1, 10, 0.2)
    first_again = retry_available_at(task_id, 1, now, 1, 10, 0.2)
    second = retry_available_at(task_id, 2, now, 1, 10, 0.2)
    capped = retry_available_at(task_id, 10, now, 1, 10, 0.2)

    assert first == first_again
    assert now < first < second < capped
    assert 8 <= (capped - now).total_seconds() <= 12
