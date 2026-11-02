"""Scheduler policies for the discrete-event simulator."""


def fifo(pending, workers_idle, state):
    return sorted(pending, key=lambda t: (t["arrival"], t["task_id"]))[: len(workers_idle)]


def fair(pending, workers_idle, state):
    # round-robin by job: pick the job with fewest completed tasks first
    job_counts = {}
    for t in pending:
        job_counts.setdefault(t["job_id"], 0)
    for job_id in job_counts:
        job_counts[job_id] = sum(1 for t in pending if t["job_id"] == job_id)
    # schedule one task per job in round-robin order
    ordered_jobs = sorted(job_counts, key=lambda j: (state.get("rr_counter", {}).get(j, 0), j))
    result = []
    remaining = list(pending)
    for _ in range(len(workers_idle)):
        progressed = False
        for job_id in ordered_jobs:
            candidates = [t for t in remaining if t["job_id"] == job_id]
            if candidates:
                chosen = min(candidates, key=lambda t: (t["arrival"], t["task_id"]))
                result.append(chosen)
                remaining.remove(chosen)
                progressed = True
                if len(result) >= len(workers_idle):
                    break
        if not progressed or len(result) >= len(workers_idle):
            break
    return result


def sjf(pending, workers_idle, state):
    return sorted(pending, key=lambda t: (t["duration"], t["arrival"], t["task_id"]))[
        : len(workers_idle)
    ]


SCHEDULERS = {"fifo": fifo, "fair": fair, "sjf": sjf}
