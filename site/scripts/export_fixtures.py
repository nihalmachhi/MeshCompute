import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from meshcompute.sim.engine import simulate
from meshcompute.sim.workloads import make_workload

out = Path(__file__).resolve().parents[1] / "src" / "features" / "simulator" / "__fixtures__"
out.mkdir(parents=True, exist_ok=True)

jobs, _ = make_workload(seed=42)
tasks = [t for job in jobs for t in job["tasks"]]
fixture = {"tasks": tasks, "expected_fifo": simulate(4, jobs, "fifo")}
(out / "sim.json").write_text(json.dumps(fixture, indent=2))

# results
results = {}
for sched in ("fifo", "fair", "sjf"):
    results[sched] = simulate(4, jobs, sched)
    results[sched + "_kill"] = simulate(4, jobs, sched, kill_worker=True)
(Path(__file__).resolve().parents[1] / "src" / "data" / "results.generated.json").write_text(
    json.dumps(results, indent=2)
)
print("fixtures exported")
