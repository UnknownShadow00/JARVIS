"""Dictation output path for speech-to-text transcripts."""
from __future__ import annotations

from app.config import settings
from app.logs.audit import audit

try:
    import pyperclip  # type: ignore[import-untyped]
except ImportError:
    pyperclip = None
    PYPERCLIP_AVAILABLE = False
else:
    PYPERCLIP_AVAILABLE = True

try:
    import pyautogui  # type: ignore[import-untyped]
except Exception:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False
else:
    PYAUTOGUI_AVAILABLE = True


class Dictation:
    """Send STT transcripts to clipboard and optional type-out."""

    def handle_transcript(self, text: str) -> bool:
        """Handle a transcript without sending it through the brain pipeline."""
        transcript = text.strip()
        char_count = len(transcript)
        if not settings.voice.dictation_enabled:
            audit.log("dictation_skipped", {"chars": char_count, "type_out": False, "reason": "disabled"})
            return False
        if not transcript:
            audit.log("dictation_skipped", {"chars": 0, "type_out": False, "reason": "empty"})
            return False

        clipboard_written = self._write_clipboard(transcript)
        type_out = self._type_out(transcript)
        audit.log("dictation_handled", {"chars": char_count, "type_out": type_out})
        return clipboard_written or type_out

    def _write_clipboard(self, transcript: str) -> bool:
        if not PYPERCLIP_AVAILABLE or pyperclip is None:
            audit.log("dictation_unavailable", {"chars": len(transcript), "dependency": "pyperclip"})
            return False

        try:
            pyperclip.copy(transcript)
        except Exception as exc:
            audit.log("dictation_clipboard_error", {"chars": len(transcript), "error": str(exc)})
            return False
        return True

    def _type_out(self, transcript: str) -> bool:
        if not settings.voice.dictation_type_out or settings.safety.dry_run:
            return False
        if not PYAUTOGUI_AVAILABLE or pyautogui is None:
            audit.log("dictation_unavailable", {"chars": len(transcript), "dependency": "pyautogui"})
            return False

        try:
            pyautogui.write(transcript)
        except Exception as exc:
            audit.log("dictation_type_out_error", {"chars": len(transcript), "error": str(exc)})
            return False
        return True


dictation = Dictation()
