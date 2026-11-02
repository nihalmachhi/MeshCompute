"""Deterministic overhead/parallelism model for choosing task chunk sizes."""

from __future__ import annotations

import math


def choose_chunk_size(
    total_bytes: int,
    worker_count: int,
    bytes_per_second: float,
    fixed_overhead_seconds: float,
    candidates: tuple[int, ...] = (262_144, 524_288, 1_048_576, 2_097_152, 4_194_304),
) -> dict[str, int | float]:
    """Choose the candidate with the lowest modeled makespan under round-robin workers."""
    if total_bytes < 1 or worker_count < 1 or bytes_per_second <= 0 or fixed_overhead_seconds < 0:
        raise ValueError("input size, workers, throughput, and overhead must be valid")
    if not candidates or any(candidate < 1 for candidate in candidates):
        raise ValueError("chunk candidates must be positive")

    estimates: list[tuple[float, int, int]] = []
    for chunk_size in candidates:
        worker_loads = [0.0] * worker_count
        chunk_count = math.ceil(total_bytes / chunk_size)
        remaining = total_bytes
        for index in range(chunk_count):
            current_size = min(chunk_size, remaining)
            remaining -= current_size
            worker_loads[index % worker_count] += (
                fixed_overhead_seconds + current_size / bytes_per_second
            )
        estimates.append((max(worker_loads), chunk_size, chunk_count))
    makespan, chunk_size, chunk_count = min(estimates, key=lambda item: (item[0], item[1]))
    return {
        "chunk_size_bytes": chunk_size,
        "task_count": chunk_count,
        "estimated_makespan_seconds": round(makespan, 3),
    }
