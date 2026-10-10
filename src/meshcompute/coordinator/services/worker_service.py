"""Worker registration and heartbeat application services."""
from uuid import UUID
from meshcompute.common.clock import Clock,SystemClock
from meshcompute.common.settings import Settings,get_settings
from meshcompute.coordinator.db.unit_of_work import UnitOfWork
from meshcompute.coordinator.events import event_hub
from meshcompute.coordinator.services.lease_manager import LeaseManager

class WorkerService:
    """Manage coordinator-side worker lifecycle records."""
    def __init__(self,settings: Settings|None=None,clock: Clock|None=None):
        self.settings=settings or get_settings();self.clock=clock or SystemClock()
    async def register(self,uow: UnitOfWork,name: str) -> dict:
        """Create a worker identity and expose the configured heartbeat cadence."""
        worker=uow.workers.register(name,self.clock.now())
        await event_hub.publish({"type":"worker.registered","worker_id":str(worker.id),"name":worker.name})
        return {"worker_id":worker.id,"heartbeat_interval_seconds":self.settings.heartbeat_interval_seconds}
    def list(self,uow: UnitOfWork) -> list[dict]:
        """Return read-only worker health and lease information."""
        now=self.clock.now()
        return [{"worker_id":worker.id,"name":worker.name,"status":worker.status,
            "last_heartbeat_at":worker.last_heartbeat_at,
            "heartbeat_age_seconds":max(0,int((now-worker.last_heartbeat_at).total_seconds())),
            "current_task_id":worker.current_task_id} for worker in uow.workers.all()]
    async def heartbeat(self,uow: UnitOfWork,worker_id: UUID,task_id: UUID|None,attempt: int|None) -> dict:
        """Delegate liveness and lease fencing to the lease manager."""
        return await LeaseManager(self.settings,self.clock).heartbeat(uow,worker_id,task_id,attempt)
