"""Pure scheduling score and worker/task compatibility rules."""

from datetime import datetime


def effective_priority(
    priority: int, queued_at: datetime, now: datetime, aging_seconds: int
) -> int:
    """Raise a queued job's priority by one class for each complete aging interval."""
    if aging_seconds < 1:
        raise ValueError("aging_seconds must be positive")
    age = max(0.0, (now - queued_at).total_seconds())
    return priority + int(age // aging_seconds)


def supports_capabilities(required: list[str], available: list[str]) -> bool:
    """Return whether a worker declares every capability a task requires."""
    return set(required).issubset(available)
