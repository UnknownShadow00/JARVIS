from __future__ import annotations

from unittest.mock import patch

from app.tools import system_stats
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert system_stats.SAFETY_LEVEL == 0


def test_dry_run() -> None:
    with patch("app.config.settings.safety.dry_run", True):
        result = system_stats.execute({})
    assert "dry" in str(result).lower()


def test_returns_expected_keys() -> None:
    with patch("app.config.settings.safety.dry_run", False):
        result = system_stats.execute({})
    assert isinstance(result, dict)
    assert {"cpu_percent", "ram_total_gb", "disk_total_gb"} <= result.keys()


def test_registered() -> None:
    assert ToolRegistry().get("system_stats") is not None
