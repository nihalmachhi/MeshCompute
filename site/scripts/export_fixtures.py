from __future__ import annotations

import json
from pathlib import Path

from cipherscope.features.beacon import periodicity_score

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / "output" / "reports" / "synthetic-evaluation.json"
OUT = Path(__file__).resolve().parents[1] / "src" / "features" / "simulator" / "__fixtures__"
DATA = Path(__file__).resolve().parents[1] / "src" / "data"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    cases = {
        "regular_beacon": [0.0, 30.0, 60.0, 90.0, 120.0, 150.0],
        "jittered": [0.0, 28.0, 63.0, 89.0, 125.0, 148.0],
        "web_burst": [0.0, 0.2, 0.4, 5.0, 5.1, 10.0],
    }
    fixtures = {
        name: {"times": times, "result": periodicity_score(times)} for name, times in cases.items()
    }
    (OUT / "beacon.json").write_text(json.dumps(fixtures, indent=2), encoding="utf-8")

    report = json.loads(REPORT.read_text(encoding="utf-8"))
    s1 = report["splits"]["S1_random_caution_only"]["summary"]["macro_f1"]
    s4 = report["splits"]["S4_cross_dataset"]["summary"]["macro_f1"]
    results = {
        "random_split": {"macro_f1": s1["mean"], "std": s1["std"]},
        "cross_environment": {"macro_f1": s4["mean"], "std": s4["std"]},
        "robustness": report["robustness"],
        "data_kind": report["data_kind"],
    }
    (DATA / "results.generated.json").write_text(json.dumps(results, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
