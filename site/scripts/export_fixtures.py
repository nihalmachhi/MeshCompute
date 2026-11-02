"""Generate deterministic simulator fixtures and reported site results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from meshcompute.evaluation import generate_evaluation
from meshcompute.sim.engine import simulate
from meshcompute.sim.workloads import make_workload

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "site/src/features/simulator/__fixtures__/cluster.json"
RESULTS = ROOT / "site/src/data/results.generated.json"
SCHEDULERS = ("fifo", "fair", "sjf")


def generate() -> tuple[dict[str, Any], dict[str, Any]]:
    """Run the checked-in simulator over a fixed synthetic cluster workload."""
    jobs, _ = make_workload(seed=42, num_jobs=6, tasks_per_job=8)
    parity = {
        scheduler: {
            "normal": simulate(4, jobs, scheduler),
            "worker_failure": simulate(4, jobs, scheduler, kill_worker=True),
        }
        for scheduler in SCHEDULERS
    }
    results = {
        "synthetic": True,
        "seed": 42,
        "workers": 4,
        "scheduler_comparison": parity,
        "handler_evaluation": generate_evaluation(seed=42),
        "note": (
            "Seeded simulation only. These values compare scheduling behavior; "
            "they are not production throughput measurements."
        ),
    }
    fixture = {"seed": 42, "workers": 4, "jobs": jobs, "expected": parity}
    return fixture, results


def main() -> None:
    """Write the Python-derived parity fixture and report consumed by the site."""
    fixture, results = generate()
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(fixture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
