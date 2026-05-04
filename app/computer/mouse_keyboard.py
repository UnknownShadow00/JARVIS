from __future__ import annotations

from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 2
DESCRIPTION = "Control mouse and keyboard via PyAutoGUI"
SHORT_TEXT_LIMIT = 50

try:
    import pyautogui

    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    pyautogui = None


def _dry_run_narration(action: str, params: dict[str, Any]) -> str:
    return f"[DRY RUN] Would execute mouse_keyboard action '{action}' with params {params}"


def _load_pyautogui() -> Any:
    if pyautogui is None:
        raise ImportError("pyautogui not installed: pip install pyautogui")
    return pyautogui


def _coerce_int(params: dict[str, Any], key: str) -> int:
    return int(params[key])


def _maybe_position(params: dict[str, Any]) -> tuple[int, int] | None:
    if "x" in params and "y" in params:
        return (_coerce_int(params, "x"), _coerce_int(params, "y"))
    return None


def execute(params: dict[str, Any]) -> dict[str, Any] | str:
    action = str(params.get("action") or "").strip().lower()
    audit.log("tool_mouse_keyboard", {"action": action, "params": params, "dry_run": settings.safety.dry_run})

    if settings.safety.dry_run:
        return _dry_run_narration(action, params)

    try:
        gui = _load_pyautogui()

        if action == "move":
            gui.moveTo(_coerce_int(params, "x"), _coerce_int(params, "y"), duration=0.2)
        elif action == "click":
            position = _maybe_position(params)
            if position is None:
                gui.click()
            else:
                gui.click(*position)
        elif action == "double_click":
            gui.doubleClick(_coerce_int(params, "x"), _coerce_int(params, "y"))
        elif action == "right_click":
            gui.rightClick(_coerce_int(params, "x"), _coerce_int(params, "y"))
        elif action == "type":
            text = str(params.get("text") or "")
            if len(text) <= SHORT_TEXT_LIMIT:
                gui.typewrite(text, interval=0.05)
            else:
                gui.write(text, interval=0.05)
        elif action == "key":
            keys = params.get("keys")
            if isinstance(keys, list):
                gui.hotkey(*[str(key) for key in keys])
            else:
                key = params.get("key", keys)
                gui.press(str(key))
        elif action == "scroll":
            clicks = int(params.get("clicks", 0))
            position = _maybe_position(params)
            if position is None:
                gui.scroll(clicks)
            else:
                gui.scroll(clicks, x=position[0], y=position[1])
        elif action == "drag":
            gui.dragTo(_coerce_int(params, "x"), _coerce_int(params, "y"), duration=0.5)
        else:
            return {"error": "unknown action"}
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}

    return {"success": True, "action": action}
