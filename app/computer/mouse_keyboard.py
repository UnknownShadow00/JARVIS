from __future__ import annotations

import builtins
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "Control mouse and keyboard via PyAutoGUI"


def _load_pyautogui() -> Any:
    try:
        return builtins.__import__("pyautogui")
    except ImportError:
        return None


def click(x: int, y: int, button: str = "left") -> dict[str, Any]:
    audit.log("tool_mouse_keyboard", {"action": "click", "dry_run": settings.safety.dry_run})
    if settings.safety.dry_run:
        return {"dry_run": True, "action": "click", "x": x, "y": y}

    pyautogui = _load_pyautogui()
    if pyautogui is None:
        return {"error": "pyautogui not installed: pip install pyautogui"}

    pyautogui.click(x, y, button=button)
    return {"action": "click", "x": x, "y": y, "button": button}


def type_text(text: str, interval: float = 0.05) -> dict[str, Any]:
    audit.log("tool_mouse_keyboard", {"action": "type", "dry_run": settings.safety.dry_run})
    if settings.safety.dry_run:
        return {"dry_run": True, "action": "type", "text": text}

    pyautogui = _load_pyautogui()
    if pyautogui is None:
        return {"error": "pyautogui not installed: pip install pyautogui"}

    pyautogui.typewrite(text, interval=interval)
    return {"action": "type", "chars": len(text)}


def hotkey(*keys: str) -> dict[str, Any]:
    audit.log("tool_mouse_keyboard", {"action": "hotkey", "dry_run": settings.safety.dry_run})
    if settings.safety.dry_run:
        return {"dry_run": True, "action": "hotkey", "keys": list(keys)}

    pyautogui = _load_pyautogui()
    if pyautogui is None:
        return {"error": "pyautogui not installed: pip install pyautogui"}

    pyautogui.hotkey(*keys)
    return {"action": "hotkey", "keys": list(keys)}


def execute(params: dict[str, Any]) -> dict[str, Any]:
    action = str(params.get("action") or "").strip().lower()
    if action == "click":
        return click(
            int(params.get("x", 0)),
            int(params.get("y", 0)),
            str(params.get("button", "left")),
        )
    if action == "type":
        return type_text(
            str(params.get("text", "")),
            float(params.get("interval", 0.05)),
        )
    if action == "hotkey":
        keys = params.get("keys", [])
        if isinstance(keys, str):
            keys = [keys]
        return hotkey(*[str(key) for key in keys])
    return {"error": "unknown action"}
