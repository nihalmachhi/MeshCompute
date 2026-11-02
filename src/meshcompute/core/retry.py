"""Deterministic bounded exponential retry delay with per-attempt jitter."""

from __future__ import annotations

import hashlib
import random
from datetime import datetime, timedelta
from uuid import UUID


def retry_available_at(
    task_id: UUID,
    attempt: int,
    now: datetime,
    base_seconds: float,
    max_seconds: float,
    jitter_fraction: float,
) -> datetime:
    """Return the next retry time, stable for a task attempt across coordinator restarts."""
    if attempt < 1 or base_seconds <= 0 or max_seconds <= 0 or not 0 <= jitter_fraction <= 1:
        raise ValueError("retry policy parameters are out of range")
    exponent = min(attempt - 1, 30)
    delay = min(max_seconds, base_seconds * (2**exponent))
    seed = int.from_bytes(hashlib.sha256(f"{task_id}:{attempt}".encode()).digest()[:8], "big")
    delay *= 1 + random.Random(seed).uniform(-jitter_fraction, jitter_fraction)
    return now + timedelta(seconds=max(0, delay))
