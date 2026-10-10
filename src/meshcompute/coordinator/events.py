"""Thread-safe in-process event fanout for dashboard WebSocket clients."""
import asyncio
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from typing import Any

class EventHub:
    """Broadcast compact state-change events without blocking the coordinator."""
    def __init__(self):
        self._subscribers:dict[asyncio.Queue[dict[str,Any]],asyncio.AbstractEventLoop]={}
    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[asyncio.Queue[dict[str,Any]]]:
        """Register a bounded queue on the current event loop."""
        queue:asyncio.Queue[dict[str,Any]]=asyncio.Queue(maxsize=100)
        self._subscribers[queue]=asyncio.get_running_loop()
        try:yield queue
        finally:self._subscribers.pop(queue,None)
    async def publish(self,event: dict[str,Any]) -> None:
        """Deliver events safely, including from the background reaper thread."""
        current=asyncio.get_running_loop()
        for queue,loop in tuple(self._subscribers.items()):
            if loop is current:self._enqueue(queue,event)
            else:loop.call_soon_threadsafe(self._enqueue,queue,event)
    @staticmethod
    def _enqueue(queue: asyncio.Queue[dict[str,Any]],event: dict[str,Any]) -> None:
        """Drop the oldest item for slow clients rather than blocking producers."""
        if queue.full():
            try:queue.get_nowait()
            except asyncio.QueueEmpty:pass
        queue.put_nowait(event)
    @property
    def subscriber_count(self) -> int:
        """Report the number of connected dashboards."""
        return len(self._subscribers)

event_hub=EventHub()
