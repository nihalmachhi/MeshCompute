"""Independent heartbeat thread keeps long-running task leases alive."""
import logging
import threading
from uuid import UUID
from meshcompute.common.settings import get_settings
from meshcompute.worker.coordinator_client import CoordinatorClient

logger=logging.getLogger(__name__)
class HeartbeatLoop:
    """Send liveness in the background while the handler runs in a child process."""
    def __init__(self,client: CoordinatorClient,worker_id: UUID,interval_seconds: int|None=None):
        self.client=client;self.worker_id=worker_id
        self.interval=interval_seconds or get_settings().heartbeat_interval_seconds
        self._stop=threading.Event();self._lock=threading.Lock()
        self._task_id: UUID|None=None;self._attempt: int|None=None
        self._thread=threading.Thread(target=self._run,name=f"heartbeat-{worker_id}",daemon=True)
    def start(self) -> None:
        """Start the daemon heartbeat thread."""
        self._thread.start()
    def set_task(self,task_id: UUID|None,attempt: int|None) -> None:
        """Atomically update the lease token sent with future heartbeats."""
        with self._lock:self._task_id,self._attempt=task_id,attempt
        self._send()
    def stop(self) -> None:
        """Stop and join the heartbeat thread."""
        self._stop.set();self._thread.join(timeout=self.interval+1)
    def _run(self) -> None:
        """Periodically send worker liveness until shutdown."""
        while not self._stop.wait(self.interval):self._send()
    def _send(self) -> None:
        with self._lock:task_id,attempt=self._task_id,self._attempt
        try:self.client.heartbeat(self.worker_id,task_id,attempt)
        except Exception:
            logger.exception("worker heartbeat request failed",extra={"worker_id":self.worker_id,"task_id":task_id})
