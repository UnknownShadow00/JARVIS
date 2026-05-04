from __future__ import annotations

from unittest.mock import patch

from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    from app.tools.interpreter import SAFETY_LEVEL

    assert SAFETY_LEVEL == 2


def test_dry_run(monkeypatch) -> None:
    from app.tools.interpreter import execute

    monkeypatch.setattr("app.config.settings.safety.dry_run", True)
    result = execute({"task": "list files"})
    assert result["dry_run"] is True


def test_missing_task() -> None:
    from app.tools.interpreter import execute

    result = execute({})
    assert "error" in result


def test_no_interpreter_binary() -> None:
    from app.tools.interpreter import execute

    with patch("app.config.settings.safety.dry_run", False), patch("shutil.which", return_value=None):
        result = execute({"task": "run ls"})
    assert "error" in result


def test_registered() -> None:
    assert ToolRegistry().get("interpreter") is not None
