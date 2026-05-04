from __future__ import annotations

import queue
import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import Mock, patch

from app.config import settings
from app.voice import tts as tts_module
from app.voice.wake_word import WakeWordDetector


class _Stream:
    def __init__(self, callback, frames: int, after=None):
        self.callback = callback
        self.frames = frames
        self.after = after

    def __enter__(self):
        def feed():
            for _ in range(self.frames):
                self.callback(b"\0" * 2560, 1280, None, None)
            if self.after:
                self.after()

        threading.Thread(target=feed, daemon=True).start()
        return self

    def __exit__(self, *args):
        return False


def _listen(detector: WakeWordDetector, frames: int, after=None, **patches):
    sd = SimpleNamespace(RawInputStream=lambda **kw: _Stream(kw["callback"], frames, after))
    np = SimpleNamespace(frombuffer=lambda data, dtype=None: data, int16="int16")
    with (
        patch.dict(sys.modules, {"sounddevice": sd, "numpy": np}),
        patch.object(WakeWordDetector, "_load_model", return_value=patches["model"]),
        patch.object(WakeWordDetector, "_push_to_talk_active", return_value=False),
        patch("app.voice.wake_word.sounds.play"),
        patch("app.voice.wake_word.vad.record_until_silence", return_value=patches.get("audio", b"")),
        patch.object(settings.voice, "wake_word_sensitivity", patches.get("sensitivity", 0.5)),
    ):
        return detector.listen(timeout=0.3)


def test_suppressed_during_speaking() -> None:
    detector = WakeWordDetector()
    model = Mock()
    model.predict.return_value = {"hey_jarvis": 0.99}

    def release():
        time.sleep(0.05)
        tts_module.is_speaking = False

    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        assert _listen(detector, 20, release, model=model) == b""
    model.predict.assert_not_called()


def test_suppressed_during_cooldown() -> None:
    detector = WakeWordDetector()
    model = Mock()
    model.predict.return_value = {"hey_jarvis": 0.99}
    with (
        patch.object(tts_module, "is_speaking", False),
        patch.object(tts_module, "cooldown_until", time.monotonic() + 10.0),
    ):
        assert _listen(detector, 20, model=model) == b""
    model.predict.assert_not_called()


def test_resumes_after_cooldown() -> None:
    detector = WakeWordDetector()
    detector._last_detection_at = 0.0
    model = Mock()
    model.predict.return_value = {"hey_jarvis": 0.99}
    with (
        patch.object(tts_module, "is_speaking", False),
        patch.object(tts_module, "cooldown_until", time.monotonic() - 1.0),
    ):
        assert _listen(detector, 1, model=model, audio=b"fakeaudio") == b"fakeaudio"
    model.predict.assert_called_once()
