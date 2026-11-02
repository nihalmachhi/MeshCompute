"""Thread-safe in-process event fanout for dashboard WebSocket clients."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any


class EventHub:
    """Broadcast compact state-change events without blocking the coordinator."""

    def __init__(self):
        self._subscribers: dict[asyncio.Queue[dict[str, Any]], asyncio.AbstractEventLoop] = {}

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[dict[str, Any]]]:
        """Register a bounded queue on the current event loop."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=100)
        self._subscribers[queue] = asyncio.get_running_loop()
        try:
            yield queue
        finally:
            self._subscribers.pop(queue, None)

    def publish(self, event: dict[str, Any]) -> None:
        """Deliver events safely from sync or async callers."""
        try:
            current = asyncio.get_event_loop()
        except RuntimeError:
            current = None
        for queue, loop in tuple(self._subscribers.items()):
            try:
                if loop is current and loop.is_running():
                    self._enqueue(queue, event)
                else:
                    loop.call_soon_threadsafe(self._enqueue, queue, event)
            except RuntimeError:
                pass

    @staticmethod
    def _enqueue(queue: asyncio.Queue[dict[str, Any]], event: dict[str, Any]) -> None:
        """Drop the oldest item for slow clients rather than blocking producers."""
        if queue.full():
            import contextlib

            with contextlib.suppress(asyncio.QueueEmpty):
                queue.get_nowait()
        queue.put_nowait(event)

    @property
    def subscriber_count(self) -> int:
        """Report the number of connected dashboards."""
        return len(self._subscribers)


event_hub = EventHub()
