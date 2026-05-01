"""Kill switch - Ctrl+Alt+J hotkey and voice phrase trigger."""
from __future__ import annotations

import re
import threading
from typing import Callable

from app.logs.audit import audit

SAFETY_LEVEL = 0
JARVIS_ACTIVE = True

_VOICE_TRIGGERS = frozenset({"shutdown jarvis", "kill jarvis", "emergency stop", "power down"})
_STOP_WORDS = re.compile(r"\b(stop|cancel|freeze|abort)\b", re.IGNORECASE)

_lock = threading.Lock()
_triggered = False
_callbacks: list[Callable[[], None]] = []


def register_callback(fn: Callable[[], None]) -> None:
    """Register a function to call when the kill switch fires."""
    with _lock:
        _callbacks.append(fn)


def trigger(reason: str = "manual") -> None:
    """Fire the kill switch without exiting the host process."""
    global _triggered, JARVIS_ACTIVE
    with _lock:
        if _triggered:
            return
        _triggered = True
        JARVIS_ACTIVE = False
        callbacks = list(_callbacks)

    audit.log("kill_switch", {"reason": reason})
    print(f"\n[JARVIS] Kill switch triggered: {reason}", flush=True)

    for fn in callbacks:
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            audit.log("kill_switch_callback_error", {"callback": repr(fn), "error": str(exc)})


def reset() -> None:
    """Reset the kill switch for tests or a new server session."""
    global _triggered, JARVIS_ACTIVE
    with _lock:
        _triggered = False
        JARVIS_ACTIVE = True


def is_active() -> bool:
    """Return whether JARVIS should continue processing work."""
    with _lock:
        return JARVIS_ACTIVE


def check_voice(transcript: str) -> bool:
    """Return True and trigger if transcript contains a kill phrase."""
    normalized = transcript.lower().strip()
    if normalized in _VOICE_TRIGGERS or _STOP_WORDS.search(normalized):
        trigger(reason=f"voice: {transcript!r}")
        return True
    return False


def _hotkey_listener() -> None:
    try:
        import keyboard  # type: ignore[import-untyped]

        keyboard.add_hotkey("ctrl+alt+j", lambda: trigger(reason="hotkey Ctrl+Alt+J"))
        keyboard.wait()
    except ImportError:
        audit.log("kill_switch_warning", {"msg": "keyboard package not installed; hotkey disabled"})
    except Exception as exc:
        audit.log("kill_switch_warning", {"msg": f"hotkey listener error: {exc}"})


def start_hotkey_listener() -> None:
    """Start Ctrl+Alt+J listener in a daemon thread."""
    t = threading.Thread(target=_hotkey_listener, daemon=True, name="kill-switch-hotkey")
    t.start()
