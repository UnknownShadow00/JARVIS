"""Global push-to-talk hotkey listener."""
from __future__ import annotations

import threading
from collections.abc import Callable

from app.config import settings
from app.logs.audit import audit

try:
    import keyboard  # type: ignore[import-untyped]
except ImportError:
    keyboard = None
    KEYBOARD_AVAILABLE = False
else:
    KEYBOARD_AVAILABLE = True


class PushToTalkManager:
    """Manage global push-to-talk and dictation hotkey lifecycles."""

    def __init__(self, hotkey: str | None = None, dictation_hotkey: str | None = None) -> None:
        configured_key = (hotkey or settings.voice.push_to_talk_key or "ctrl+space").strip()
        configured_dictation_key = (
            dictation_hotkey or settings.voice.dictation_hotkey or "ctrl+shift+space"
        ).strip()
        self._hotkey = configured_key or "ctrl+space"
        self._dictation_hotkey = configured_dictation_key or "ctrl+shift+space"
        self._active = threading.Event()
        self._dictation_active = threading.Event()
        self._press_callback: Callable[[], None] | None = None
        self._release_callback: Callable[[], None] | None = None
        self._dictation_press_callback: Callable[[], None] | None = None
        self._dictation_release_callback: Callable[[], None] | None = None
        self._press_hook = None
        self._release_hook = None
        self._dictation_press_hook = None
        self._dictation_release_hook = None
        self._started = False
        self._lock = threading.Lock()
        self._warning_logged = False

    def start(self) -> None:
        """Register press and release handlers for the configured hotkey."""
        if not KEYBOARD_AVAILABLE or keyboard is None:
            self._log_unavailable_warning()
            return

        with self._lock:
            if self._started:
                return

            self._press_hook = keyboard.on_press_key(self._hotkey, self._handle_press)
            self._release_hook = keyboard.on_release_key(self._hotkey, self._handle_release)
            if settings.voice.dictation_enabled:
                self._dictation_press_hook = keyboard.on_press_key(
                    self._dictation_hotkey,
                    self._handle_dictation_press,
                )
                self._dictation_release_hook = keyboard.on_release_key(
                    self._dictation_hotkey,
                    self._handle_dictation_release,
                )
            self._started = True

    def stop(self) -> None:
        """Unregister any active hotkey handlers and clear active state."""
        if not KEYBOARD_AVAILABLE or keyboard is None:
            self._active.clear()
            self._dictation_active.clear()
            return

        with self._lock:
            if self._press_hook is not None:
                keyboard.unhook(self._press_hook)
                self._press_hook = None
            if self._release_hook is not None:
                keyboard.unhook(self._release_hook)
                self._release_hook = None
            if self._dictation_press_hook is not None:
                keyboard.unhook(self._dictation_press_hook)
                self._dictation_press_hook = None
            if self._dictation_release_hook is not None:
                keyboard.unhook(self._dictation_release_hook)
                self._dictation_release_hook = None
            self._started = False

        self._active.clear()
        self._dictation_active.clear()

    def on_press(self, callback: Callable[[], None]) -> None:
        """Store the callback fired while the push-to-talk key is pressed."""
        self._press_callback = callback

    def on_release(self, callback: Callable[[], None]) -> None:
        """Store the callback fired when the push-to-talk key is released."""
        self._release_callback = callback

    def on_dictation_press(self, callback: Callable[[], None]) -> None:
        """Store the callback fired while the dictation key is pressed."""
        self._dictation_press_callback = callback

    def on_dictation_release(self, callback: Callable[[], None]) -> None:
        """Store the callback fired when the dictation key is released."""
        self._dictation_release_callback = callback

    def is_active(self) -> bool:
        """Return whether the push-to-talk key is currently held."""
        if not KEYBOARD_AVAILABLE:
            return False
        return self._active.is_set()

    def is_dictation_active(self) -> bool:
        """Return whether the dictation hotkey is currently held."""
        if not KEYBOARD_AVAILABLE:
            return False
        return self._dictation_active.is_set()

    def _handle_press(self, _event) -> None:  # noqa: ANN001
        self._active.set()
        if self._press_callback is not None:
            self._press_callback()

    def _handle_release(self, _event) -> None:  # noqa: ANN001
        self._active.clear()
        if self._release_callback is not None:
            self._release_callback()

    def _handle_dictation_press(self, _event) -> None:  # noqa: ANN001
        self._dictation_active.set()
        if self._dictation_press_callback is not None:
            self._dictation_press_callback()

    def _handle_dictation_release(self, _event) -> None:  # noqa: ANN001
        self._dictation_active.clear()
        if self._dictation_release_callback is not None:
            self._dictation_release_callback()

    def _log_unavailable_warning(self) -> None:
        if self._warning_logged:
            return
        self._warning_logged = True
        audit.log("push_to_talk_warning", {"msg": "keyboard package not installed; push-to-talk disabled"})
