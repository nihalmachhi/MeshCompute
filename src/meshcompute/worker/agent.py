"""Worker registration, polling, execution, heartbeats, and result submission."""
import logging
import os
import time
from uuid import UUID
import httpx
from meshcompute.common.errors import TaskExecutionError
from meshcompute.common.logging import configure_logging
from meshcompute.common.settings import get_settings
from meshcompute.worker.coordinator_client import CoordinatorClient
from meshcompute.worker.executor import execute_with_timeout
from meshcompute.worker.heartbeat import HeartbeatLoop

logger=logging.getLogger(__name__)
def run_worker(name: str|None=None,stop_event=None) -> None:
    """Run one worker until stopped, polling only the coordinator HTTP API."""
    settings=get_settings();client=CoordinatorClient()
    worker_name=name or os.getenv("MESH_COMPUTE_WORKER_ID") or os.getenv("WORKER_NAME",f"worker-{os.getenv('HOSTNAME','local')}")
    registration=client.register(worker_name);worker_id=UUID(registration["worker_id"])
    heartbeat=HeartbeatLoop(client,worker_id,registration["heartbeat_interval_seconds"]);heartbeat.start()
    logger.info("worker registered",extra={"worker_id":worker_id,"event":"worker_registered"})
    try:
        while stop_event is None or not stop_event.is_set():
            try:task=client.claim(worker_id)
            except httpx.HTTPError:
                logger.exception("task claim failed",extra={"worker_id":worker_id})
                time.sleep(settings.worker_poll_interval_seconds);continue
            if task is None:
                time.sleep(settings.worker_poll_interval_seconds);continue
            task_id=UUID(task["task_id"]);attempt=int(task["attempt"])
            heartbeat.set_task(task_id,attempt)
            _execute_task(client,worker_id,task,settings.task_timeout_seconds)
            heartbeat.set_task(None,None)
    finally:
        heartbeat.stop();client.close()

def _execute_task(client: CoordinatorClient,worker_id: UUID,task: dict,timeout: int) -> None:
    """Run one claimed task and report exactly one completion or failure."""
    task_id=UUID(task["task_id"]);attempt=int(task["attempt"])
    try:
        client.start(task_id,worker_id,attempt)
        started=time.perf_counter()
        output=execute_with_timeout(task["job_type"],task["payload"],timeout)
        duration_ms=(time.perf_counter()-started)*1000
        client.complete(task_id,worker_id,attempt,output,duration_ms)
        logger.info("task completed",extra={"worker_id":worker_id,"task_id":task_id,"job_id":task["job_id"],"event":"task_completed"})
    except TaskExecutionError as exc:
        client.fail(task_id,worker_id,attempt,str(exc))
        logger.warning("task attempt failed",extra={"worker_id":worker_id,"task_id":task_id,"event":"task_attempt_failed"})
    except httpx.HTTPStatusError:
        logger.exception("task operation rejected",extra={"worker_id":worker_id,"task_id":task_id})
