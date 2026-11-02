"""Synthetic workloads for the simulator."""

from .prng import mulberry32


def make_workload(seed: int = 42, num_jobs: int = 6, tasks_per_job: int = 8):
    rng = mulberry32(seed)
    jobs = []
    task_id = 0
    for job_idx in range(num_jobs):
        # one big job plus small jobs: first job has many long tasks
        size = tasks_per_job * (4 if job_idx == 0 else 1)
        tasks = []
        for _ in range(size):
            dur = 1.0 + rng() * (5.0 if job_idx == 0 else 2.0)
            tasks.append(
                {"task_id": task_id, "job_id": f"job-{job_idx}", "duration": dur, "arrival": 0.0}
            )
            task_id += 1
        jobs.append({"job_id": f"job-{job_idx}", "tasks": tasks})
    return jobs, num_jobs
