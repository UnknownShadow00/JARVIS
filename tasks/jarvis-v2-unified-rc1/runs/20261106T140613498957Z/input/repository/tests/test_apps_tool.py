from __future__ import annotations

from unittest.mock import patch

from app.tools import apps
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert apps.SAFETY_LEVEL == 0


def test_dry_run() -> None:
    with patch("app.config.settings.safety.dry_run", True):
        result = apps.execute({"app": "vscode"})
    assert "dry" in str(result).lower()


def test_unknown_app() -> None:
    with patch("app.config.settings.safety.dry_run", False):
        result = apps.execute({"app": "nonexistent_xyz_app_12345"})
    assert isinstance(result, dict)
    assert "error" in result


def test_registered() -> None:
    assert ToolRegistry().get("apps") is not None
