"""Worker registration, polling, execution, heartbeats, and result submission."""

import logging
import os
import signal
import time
from uuid import UUID

import httpx

from meshcompute.core.errors import TaskExecutionError
from meshcompute.core.settings import get_settings
from meshcompute.worker.coordinator_client import CoordinatorClient
from meshcompute.worker.executor import execute_with_timeout
from meshcompute.worker.heartbeat import HeartbeatLoop

logger = logging.getLogger(__name__)


def run_worker(name: str | None = None, stop_event=None) -> None:
    """Run one worker until stopped, polling only the coordinator HTTP API."""
    settings = get_settings()
    client = CoordinatorClient()
    worker_name = (
        name
        or os.getenv("MESH_COMPUTE_WORKER_ID")
        or os.getenv("WORKER_NAME", f"worker-{os.getenv('HOSTNAME', 'local')}")
    )
    registration = _register_with_retry(client, worker_name or "worker")
    worker_id = UUID(registration["worker_id"])
    heartbeat = HeartbeatLoop(client, worker_id, registration["heartbeat_interval_seconds"])
    heartbeat.start()

    stopping = {"value": False}

    def _handle_term(signum, frame):
        stopping["value"] = True

    signal.signal(signal.SIGTERM, _handle_term)
    signal.signal(signal.SIGINT, _handle_term)

    logger.info("worker registered", extra={"worker_id": worker_id, "event": "worker_registered"})
    try:
        while not stopping["value"] and (stop_event is None or not stop_event.is_set()):
            try:
                task = client.claim(worker_id)
            except httpx.HTTPError:
                logger.exception("task claim failed", extra={"worker_id": worker_id})
                time.sleep(settings.worker_poll_interval_seconds)
                continue
            if task is None:
                time.sleep(settings.worker_poll_interval_seconds)
                continue
            task_id = UUID(task["task_id"])
            attempt = int(task["attempt"])
            heartbeat.set_task(task_id, attempt)
            try:
                _execute_task(client, worker_id, task, settings.task_timeout_seconds)
            finally:
                heartbeat.set_task(None, None)
    finally:
        heartbeat.stop()
        client.close()


def _register_with_retry(client: CoordinatorClient, name: str, attempts: int = 5) -> dict:
    delay = 1.0
    for i in range(attempts):
        try:
            return client.register(name)
        except httpx.HTTPError:
            if i == attempts - 1:
                raise
            time.sleep(delay)
            delay = min(delay * 2, 10.0)
    return {}


def _execute_task(client: CoordinatorClient, worker_id: UUID, task: dict, timeout: int) -> None:
    """Run one claimed task and report exactly one completion or failure."""
    task_id = UUID(task["task_id"])
    attempt = int(task["attempt"])
    try:
        client.start(task_id, worker_id, attempt)
        started = time.perf_counter()
        output = execute_with_timeout(task["job_type"], task["payload"], timeout)
        duration_ms = (time.perf_counter() - started) * 1000
        _post_with_retry(lambda: client.complete(task_id, worker_id, attempt, output, duration_ms))
        logger.info(
            "task completed",
            extra={
                "worker_id": worker_id,
                "task_id": task_id,
                "job_id": task["job_id"],
                "event": "task_completed",
            },
        )
    except TaskExecutionError as exc:
        error_message = str(exc)
        _post_with_retry(lambda: client.fail(task_id, worker_id, attempt, error_message))
        logger.warning(
            "task attempt failed",
            extra={"worker_id": worker_id, "task_id": task_id, "event": "task_attempt_failed"},
        )
    except httpx.HTTPStatusError:
        logger.exception(
            "task operation rejected", extra={"worker_id": worker_id, "task_id": task_id}
        )
    except httpx.HTTPError:
        logger.exception(
            "transient coordinator error", extra={"worker_id": worker_id, "task_id": task_id}
        )


def _post_with_retry(action, attempts: int = 5) -> None:
    delay = 0.5
    for i in range(attempts):
        try:
            action()
            return
        except httpx.HTTPStatusError:
            raise
        except httpx.HTTPError:
            if i == attempts - 1:
                raise
            time.sleep(delay + 0.1 * i)
            delay = min(delay * 2, 8.0)
