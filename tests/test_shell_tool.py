from __future__ import annotations

from unittest.mock import patch

from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    from app.tools.shell import SAFETY_LEVEL

    assert SAFETY_LEVEL == 2


def test_dry_run() -> None:
    from app.tools.shell import execute

    with patch("app.config.settings.safety.dry_run", True):
        result = execute({"command": "echo hello"})

    if isinstance(result, str):
        assert "dry" in result.lower()
    else:
        assert result.get("dry_run") is True


def test_missing_command() -> None:
    from app.tools.shell import execute

    result = execute({})
    assert "error" in result


def test_registered() -> None:
    assert ToolRegistry().get("shell") is not None
