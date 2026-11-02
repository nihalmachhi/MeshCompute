"""Run allow-listed task handlers in a terminable child process."""

import multiprocessing
import time
from queue import Empty

from meshcompute.core.errors import TaskExecutionError
from meshcompute.handlers.registry import get_handler


def _execute_child(job_type: str, payload: dict, output_queue) -> None:
    """Execute one registered handler and return a JSON-safe result."""
    try:
        output_queue.put((True, get_handler(job_type).execute(payload)))
    except Exception as exc:
        output_queue.put((False, f"{type(exc).__name__}: {exc}"))


def execute_with_timeout(job_type: str, payload: dict, timeout_seconds: int) -> dict:
    """Terminate a hung handler process and return only successful outputs."""
    context = multiprocessing.get_context("spawn")
    output = context.Queue(maxsize=1)
    process = context.Process(target=_execute_child, args=(job_type, payload, output), daemon=True)
    process.start()
    deadline = time.monotonic() + timeout_seconds
    result = None
    while process.is_alive():
        try:
            result = output.get(timeout=0.1)
            break
        except Empty:
            if time.monotonic() >= deadline:
                process.terminate()
                process.join()
                raise TaskExecutionError(
                    f"handler exceeded {timeout_seconds}s execution timeout"
                ) from None
    if result is None:
        try:
            result = output.get(timeout=1)
        except Empty as exc:
            raise TaskExecutionError(
                f"handler exited without a result (code {process.exitcode})"
            ) from exc
    success, value = result
    if not success:
        raise TaskExecutionError(str(value))
    if not isinstance(value, dict):
        raise TaskExecutionError("handler result must be a JSON object")
    return value
