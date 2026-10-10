"""Read-only live event stream for dashboard clients."""
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from meshcompute.coordinator.events import event_hub

router=APIRouter()
@router.websocket("/ws/events")
async def websocket_events(socket: WebSocket):
    """Push compact state-change events to one dashboard connection."""
    await socket.accept()
    try:
        async with event_hub.subscribe() as queue:
            while True:
                event=await queue.get()
                await socket.send_json(event)
    except WebSocketDisconnect:
        return
