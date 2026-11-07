"""Dictation output path for speech-to-text transcripts."""
from __future__ import annotations

from app.config import settings
from app.logs.audit import audit

pyperclip = None
pyautogui = None
PYPERCLIP_AVAILABLE = False
PYAUTOGUI_AVAILABLE = False


class Dictation:
    """Send STT transcripts to clipboard and optional type-out."""

    def handle_transcript(self, text: str) -> bool:
        """No clipboard/typing effects without an independently authorized adapter."""
        audit.log("dictation_blocked", {"reason":"independent_authorization_required","type_out":False})
        return False

    def _write_clipboard(self, transcript: str) -> bool:
        return False

    def _type_out(self, transcript: str) -> bool:
        return False


dictation = Dictation()
