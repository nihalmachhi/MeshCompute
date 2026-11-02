"""Run allow-listed task handlers in a terminable child process."""

import json
import multiprocessing
import time
from importlib import import_module
from queue import Empty
from typing import Any

try:
    resource: Any = import_module("resource")
except ImportError:  # pragma: no cover - Windows has no resource module
    resource = None

from meshcompute.core.errors import TaskExecutionError
from meshcompute.handlers.registry import get_handler


def _apply_resource_limits(cpu_seconds: int, memory_bytes: int, file_bytes: int) -> None:
    """Apply Linux/POSIX process limits before running an input handler."""
    if resource is None:
        return
    resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
    resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    resource.setrlimit(resource.RLIMIT_FSIZE, (file_bytes, file_bytes))


def _execute_child(
    job_type: str,
    payload: dict,
    output_queue: Any,
    cpu_seconds: int,
    memory_bytes: int,
    file_bytes: int,
    max_result_bytes: int,
) -> None:
    """Execute one registered handler and return a JSON-safe result."""
    try:
        _apply_resource_limits(cpu_seconds, memory_bytes, file_bytes)
        result = get_handler(job_type).execute(payload)
        encoded = json.dumps(result, separators=(",", ":")).encode()
        if len(encoded) > max_result_bytes:
            raise ValueError(f"handler output exceeds {max_result_bytes} bytes")
        output_queue.put((True, result))
    except Exception as exc:
        output_queue.put((False, f"{type(exc).__name__}: {exc}"))


def execute_with_timeout(
    job_type: str,
    payload: dict,
    timeout_seconds: int,
    cpu_seconds: int = 300,
    memory_bytes: int = 1_073_741_824,
    file_bytes: int = 10_000_000,
    max_result_bytes: int = 10_000_000,
) -> dict:
    """Terminate a hung handler process and return only successful outputs."""
    context = multiprocessing.get_context("spawn")
    output = context.Queue(maxsize=1)
    process = context.Process(
        target=_execute_child,
        args=(job_type, payload, output, cpu_seconds, memory_bytes, file_bytes, max_result_bytes),
        daemon=True,
    )
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
