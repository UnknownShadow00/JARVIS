from __future__ import annotations

import builtins
from typing import Any

from app.computer.mouse_keyboard import SAFETY_LEVEL, click, execute, hotkey, type_text
from app.config import settings


def test_safety_level() -> None:
    assert SAFETY_LEVEL == 1


def test_click_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = click(100, 200)
    assert result["dry_run"] is True


def test_type_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = type_text("hello")
    assert result["dry_run"] is True


def test_hotkey_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = hotkey("ctrl", "c")
    assert result["keys"] == ["ctrl", "c"]


def test_pyautogui_not_installed(monkeypatch) -> None:  # noqa: ANN001
    original_import = builtins.__import__

    def fake_import(name: str, globals=None, locals=None, fromlist=(), level=0) -> Any:  # noqa: ANN001
        if name == "pyautogui":
            raise ImportError("missing pyautogui")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(builtins, "__import__", fake_import)

    result = click(0, 0)

    assert "error" in result


def test_execute_unknown_action(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = execute({"action": "fly"})
    assert result.get("error") == "unknown action"
