from __future__ import annotations

from types import SimpleNamespace

from app.computer import mouse_keyboard
from app.computer.mouse_keyboard import SAFETY_LEVEL, execute
from app.config import settings
from app.tools.registry import ToolRegistry


def test_safety_level() -> None:
    assert SAFETY_LEVEL == 2


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = execute({"action": "move", "x": 100, "y": 200})
    assert "dry" in str(result).lower()


def test_move_calls_pyautogui(monkeypatch) -> None:  # noqa: ANN001
    calls: list[tuple[int, int, float]] = []

    def fake_move_to(x: int, y: int, duration: float = 0.0) -> None:
        calls.append((x, y, duration))

    fake_gui = SimpleNamespace(moveTo=fake_move_to)
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(mouse_keyboard, "pyautogui", fake_gui)

    result = execute({"action": "move", "x": 10, "y": 20})

    assert result == {"success": True, "action": "move"}
    assert calls == [(10, 20, 0.2)]


def test_type_calls_pyautogui(monkeypatch) -> None:  # noqa: ANN001
    calls: list[tuple[str, float]] = []

    def fake_typewrite(text: str, interval: float = 0.0) -> None:
        calls.append((text, interval))

    fake_gui = SimpleNamespace(typewrite=fake_typewrite)
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(mouse_keyboard, "pyautogui", fake_gui)

    result = execute({"action": "type", "text": "hello"})

    assert result == {"success": True, "action": "type"}
    assert calls == [("hello", 0.05)]


def test_execute_unknown_action(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(mouse_keyboard, "pyautogui", SimpleNamespace())
    result = execute({"action": "fly"})
    assert result.get("error") == "unknown action"


def test_registered() -> None:
    assert ToolRegistry().get("mouse_keyboard") is not None
