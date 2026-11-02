"""Generate a reproducible simulation report."""

import json

from .engine import simulate
from .workloads import make_workload


def generate(seed: int = 42):
    jobs, _ = make_workload(seed=seed)
    results = {}
    for sched in ("fifo", "fair", "sjf"):
        results[sched] = simulate(4, jobs, sched, seed=seed)
        results[sched + "_kill"] = simulate(4, jobs, sched, seed=seed, kill_worker=True)
    return results


if __name__ == "__main__":
    print(json.dumps(generate(), indent=2))
