from __future__ import annotations

import builtins

from app.config import settings
from app.tools import computer_use as computer_use_tool


def test_safety_level() -> None:
    assert computer_use_tool.SAFETY_LEVEL == 2


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)

    result = computer_use_tool.execute({"task": "click ok button"})

    assert "dry_run" in result


def test_missing_task() -> None:
    result = computer_use_tool.execute({})

    assert "error" in result


def test_no_package(monkeypatch) -> None:  # noqa: ANN001
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):  # noqa: ANN001, A002
        if name == "computer_use":
            raise ImportError("missing computer_use")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = computer_use_tool.execute({"task": "test"})

    assert "error" in result
