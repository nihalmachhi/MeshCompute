"""Injectable UTC clock for services and deterministic tests."""
from datetime import datetime,timezone
from typing import Protocol

class Clock(Protocol):
    """Time source required by lease and event logic."""
    def now(self) -> datetime: ...

class SystemClock:
    """Production UTC clock implementation."""
    def now(self) -> datetime:
        """Return current timezone-aware UTC time."""
        return datetime.now(timezone.utc)
