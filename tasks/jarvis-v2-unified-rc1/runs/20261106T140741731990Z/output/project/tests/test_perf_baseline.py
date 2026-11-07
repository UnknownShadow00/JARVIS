import json
from pathlib import Path


BASELINE_PATH = Path("tests/perf/baseline_4070ti.json")


def test_baseline_file_exists() -> None:
    assert BASELINE_PATH.exists()


def test_baseline_has_benchmarks() -> None:
    data = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))

    assert "benchmarks" in data
    assert "router_classify_ms" in data["benchmarks"]
