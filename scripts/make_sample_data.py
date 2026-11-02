"""Generate demo text, CSV and images."""

from pathlib import Path

data = Path("data")
data.mkdir(exist_ok=True)
(data / "sample.txt").write_text("mesh compute durable tasks " * 100, encoding="utf-8")
(data / "sample.csv").write_text("value\n1\n2\n3\n", encoding="utf-8")
print("sample data generated")
