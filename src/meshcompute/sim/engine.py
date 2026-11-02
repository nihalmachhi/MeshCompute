"""Deterministic discrete-event simulation for scheduler comparison."""

from __future__ import annotations

from typing import Any

from meshcompute.sim.schedulers import SCHEDULERS


def simulate(
    num_workers: int,
    jobs: list[dict[str, Any]],
    scheduler_name: str,
    seed: int = 42,
    kill_worker: bool = False,
) -> dict[str, Any]:
    """Run a fixed workload and return queue metrics plus the task timeline."""
    if num_workers < 1:
        raise ValueError("num_workers must be positive")
    try:
        scheduler = SCHEDULERS[scheduler_name]
    except KeyError as exc:
        raise ValueError(f"unknown scheduler: {scheduler_name}") from exc

    del seed  # The workload generator owns seeded task durations.
    remaining = [dict(task) for job in jobs for task in job["tasks"]]
    worker_available = [0.0] * num_workers
    task_start: dict[int, float] = {}
    task_end: dict[int, float] = {}
    completed_by_job = {job["job_id"]: 0 for job in jobs}
    in_flight: list[dict[str, Any]] = []
    schedule: list[dict[str, Any]] = []
    state: dict[str, Any] = {"rr_counter": {}}
    total_tasks = len(remaining)
    completed = 0
    now = 0.0
    killed = False
    kill_time: float | None = None
    retries = 0
    busy_time = 0.0

    while completed < total_tasks:
        idle = [
            worker
            for worker, available_at in enumerate(worker_available)
            if available_at <= now + 1e-9
        ]
        if idle and remaining:
            batch = scheduler(remaining, idle, state)
            for task, worker in zip(batch, idle[: len(batch)], strict=False):
                remaining.remove(task)
                start = max(now, worker_available[worker])
                end = start + task["duration"]
                task_start[task["task_id"]] = start
                task_end[task["task_id"]] = end
                worker_available[worker] = end
                attempt = {
                    "task_id": task["task_id"],
                    "job_id": task["job_id"],
                    "worker": worker,
                    "start": start,
                    "end": end,
                    "success": True,
                }
                schedule.append(attempt)
                in_flight.append({"end": end, "worker": worker, "task": task, "attempt": attempt})
            continue

        if not in_flight:
            break
        next_completion = min(item["end"] for item in in_flight)
        if kill_worker and not killed and now < 2.0 <= next_completion and worker_available:
            now = 2.0
            killed = True
            kill_time = now
            dead_worker = len(worker_available) - 1
            retry_items = [item for item in in_flight if item["worker"] == dead_worker]
            in_flight = [item for item in in_flight if item["worker"] != dead_worker]
            for item in retry_items:
                attempt = item["attempt"]
                attempt["success"] = False
                attempt["end"] = now
                busy_time += max(0.0, now - attempt["start"])
                remaining.append(item["task"])
                retries += 1
            worker_available.pop()
            continue
        now = next_completion
        still: list[dict[str, Any]] = []
        for item in in_flight:
            if item["end"] <= now + 1e-9:
                completed += 1
                busy_time += item["end"] - item["attempt"]["start"]
                completed_by_job[item["task"]["job_id"]] += 1
            else:
                still.append(item)
        in_flight = still

    makespan = max(task_end.values(), default=0.0)
    waits = [task_start[task["task_id"]] - task["arrival"] for job in jobs for task in job["tasks"]]
    sorted_waits = sorted(waits)
    mean_wait = sum(waits) / len(waits) if waits else 0.0
    p95_wait = sorted_waits[int(0.95 * (len(sorted_waits) - 1))] if waits else 0.0
    capacity = num_workers * makespan
    if kill_time is not None:
        capacity -= max(0.0, makespan - kill_time)
    utilization = min(1.0, busy_time / capacity) if capacity > 0 else 0.0

    job_values = list(completed_by_job.values())
    value_sum = sum(job_values)
    square_sum = sum(value * value for value in job_values)
    fairness = (value_sum * value_sum) / (len(job_values) * square_sum) if square_sum else 0.0

    return {
        "makespan": round(makespan, 3),
        "mean_wait": round(mean_wait, 3),
        "p95_wait": round(p95_wait, 3),
        "utilization": round(utilization, 3),
        "fairness": round(fairness, 3),
        "tasks": total_tasks,
        "retries": retries,
        "schedule": schedule,
    }
