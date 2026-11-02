"""Discrete-event simulator comparing schedulers."""

from .schedulers import SCHEDULERS


def simulate(
    num_workers: int, jobs, scheduler_name: str, seed: int = 42, kill_worker: bool = False
):
    scheduler = SCHEDULERS[scheduler_name]
    # flatten tasks
    pending = []
    for job in jobs:
        for task in job["tasks"]:
            pending.append(dict(task))
    # worker availability
    worker_available = [0.0] * num_workers
    task_end = {}
    task_start = {}
    completed_by_job = {job["job_id"]: 0 for job in jobs}
    total_tasks = len(pending)
    remaining = list(pending)
    # simple list scheduling: repeatedly assign when a worker is free
    # Greedy assign all possible now, then jump time.
    state = {"rr_counter": {}}
    completed = 0
    # track in-flight
    in_flight = []  # list of (end_time, worker_idx, task)
    now = 0.0
    # if kill worker, remove one worker at a time
    killed = False
    while completed < total_tasks:
        # free workers
        idle = [i for i in range(len(worker_available)) if worker_available[i] <= now + 1e-9]
        # assign
        if idle and remaining:
            batch = scheduler(remaining, idle, state)
            # only assign up to idle count
            for task, w in zip(batch, idle[: len(batch)], strict=False):
                remaining.remove(task)
                start = max(now, worker_available[w])
                end = start + task["duration"]
                task_start[task["task_id"]] = start
                task_end[task["task_id"]] = end
                worker_available[w] = end
                in_flight.append((end, w, task))
            continue
        # advance time to next completion
        if not in_flight and not remaining:
            break
        next_time = min((we for we, _, _ in in_flight), default=None)
        if next_time is None:
            break
        # handle completions at next_time
        now = next_time
        still = []
        for end, w, task in in_flight:
            if end <= now + 1e-9:
                completed += 1
                completed_by_job[task["job_id"]] += 1
            else:
                still.append((end, w, task))
        in_flight = still
        # kill worker once
        if kill_worker and not killed and now >= 2.0:
            killed = True
            # remove last worker, requeue its in-flight task
            if worker_available:
                # find in-flight on last worker
                to_requeue = [t for (e, w, t) in in_flight if w == len(worker_available) - 1]
                for t in to_requeue:
                    in_flight = [
                        (e, w, x) for (e, w, x) in in_flight if x["task_id"] != t["task_id"]
                    ]
                    remaining.append(t)
                worker_available = worker_available[:-1]
    makespan = max(task_end.values()) if task_end else 0.0
    waits = [task_start[t["task_id"]] - t["arrival"] for job in jobs for t in job["tasks"]]
    mean_wait = sum(waits) / len(waits) if waits else 0.0
    p95_wait = sorted(waits)[int(0.95 * (len(waits) - 1))] if waits else 0.0
    total_work = sum(t["duration"] for job in jobs for t in job["tasks"])
    util = total_work / (len(worker_available or [1]) * makespan) if makespan > 0 else 0.0
    # Jain fairness over per-job completion counts
    job_values = [completed_by_job[j["job_id"]] for j in jobs]
    ssum = sum(job_values)
    sq = sum(v * v for v in job_values)
    n = len(job_values)
    jain = (ssum * ssum) / (n * sq) if sq > 0 else 0.0
    return {
        "makespan": round(makespan, 3),
        "mean_wait": round(mean_wait, 3),
        "p95_wait": round(p95_wait, 3),
        "utilization": round(util, 3),
        "fairness": round(jain, 3),
        "tasks": total_tasks,
    }
