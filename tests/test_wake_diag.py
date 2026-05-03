from __future__ import annotations

import py_compile
from pathlib import Path

from scripts.wake_diag import CSV_COLUMNS, summarize


def test_script_compiles() -> None:
    py_compile.compile("scripts/wake_diag.py", doraise=True)


def test_has_main_guard() -> None:
    contents = Path("scripts/wake_diag.py").read_text(encoding="utf-8")
    assert "__main__" in contents


def test_csv_columns() -> None:
    assert CSV_COLUMNS == ["timestamp_ms", "score", "detected"]


def test_summary_keys() -> None:
    result = summarize(
        [
            {"timestamp_ms": 0, "score": 0.9, "detected": True},
            {"timestamp_ms": 80, "score": 0.3, "detected": False},
        ]
    )
    assert "max_score" in result and "detection_count" in result
