from __future__ import annotations

import sys
import threading
import time
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from app.config import settings
from app.voice import tts as tts_module
from app.voice.push_to_talk import PushToTalkManager
from app.voice.wake_word import WakeWordDetector
import app.voice.wake_word as wake_word_module


pytestmark = pytest.mark.unit


class _Stream:
    def __init__(self, callback, frames: list[bytes], after=None, frame_delay: float = 0.0):
        self._callback = callback
        self._frames = frames
        self._after = after
        self._frame_delay = frame_delay

    def __enter__(self):
        def feed() -> None:
            for frame in self._frames:
                self._callback(frame, 1280, None, None)
                if self._frame_delay > 0:
                    time.sleep(self._frame_delay)
            if self._after is not None:
                self._after()

        threading.Thread(target=feed, daemon=True).start()
        return self

    def __exit__(self, *args):
        return False


def _frame(text: str) -> bytes:
    return text.encode("utf-8")


def _model_for_wake_phrase() -> Mock:
    model = Mock()

    def predict(frame: bytes) -> dict[str, float]:
        text = frame.decode("utf-8", errors="ignore").lower()
        return {"hey_jarvis": 0.99 if "hey jarvis" in text else 0.0}

    model.predict.side_effect = predict
    return model


def _listen(
    detector: WakeWordDetector,
    frames: list[bytes],
    *,
    audio: bytes = b"captured-audio",
    after=None,
    frame_delay: float = 0.0,
    timeout: float = 0.15,
):
    sd = SimpleNamespace(RawInputStream=lambda **kw: _Stream(kw["callback"], frames, after, frame_delay))
    np = SimpleNamespace(frombuffer=lambda data, dtype=None: data, int16="int16")
    model = _model_for_wake_phrase()
    with (
        patch.dict(sys.modules, {"sounddevice": sd, "numpy": np}),
        patch.object(WakeWordDetector, "_load_model", return_value=model),
        patch.object(WakeWordDetector, "_push_to_talk_active", return_value=False),
        patch("app.voice.wake_word.sounds.play"),
        patch("app.voice.wake_word.vad.record_until_silence", return_value=audio),
        patch.object(settings.voice, "wake_word_sensitivity", 0.5),
    ):
        result = detector.listen(timeout=timeout)
    return result, model


def test_suppression_flag_exists() -> None:
    assert hasattr(wake_word_module, "is_speaking")
    assert callable(wake_word_module.is_speaking)


def test_suppression_blocks_detection_while_speaking() -> None:
    detector = WakeWordDetector()
    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [_frame("hey jarvis open settings")])

    assert result == b""
    model.predict.assert_not_called()


def test_suppression_allows_detection_when_silent() -> None:
    detector = WakeWordDetector()
    with patch.object(tts_module, "is_speaking", False), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [_frame("hey jarvis open settings")], audio=b"wake-audio")

    assert result == b"wake-audio"
    model.predict.assert_called_once()


def test_short_reply_suppressed() -> None:
    detector = WakeWordDetector()
    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [_frame("jarvis")])

    assert result == b""
    model.predict.assert_not_called()


def test_long_reply_suppressed() -> None:
    detector = WakeWordDetector()
    text = "this is a long spoken reply with more than ten words hey jarvis indeed"
    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [_frame(text)])

    assert result == b""
    model.predict.assert_not_called()


def test_contains_hey_jarvis_suppressed() -> None:
    detector = WakeWordDetector()
    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [_frame("the reply literally says hey jarvis out loud")])

    assert result == b""
    model.predict.assert_not_called()


def test_suppression_resets_after_tts() -> None:
    detector = WakeWordDetector()

    def release_tts() -> None:
        time.sleep(0.02)
        tts_module.is_speaking = False

    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        releaser = threading.Thread(target=release_tts, daemon=True)
        releaser.start()
        result, model = _listen(
            detector,
            [_frame("hey jarvis ignored during speech"), _frame("hey jarvis reenabled after tts")],
            frame_delay=0.05,
            timeout=0.2,
        )
        releaser.join(timeout=1.0)

    assert result == b"captured-audio"
    assert model.predict.call_count == 1


def test_overlap_silence_suppressed() -> None:
    detector = WakeWordDetector()
    with patch.object(tts_module, "is_speaking", True), patch.object(tts_module, "cooldown_until", 0.0):
        result, model = _listen(detector, [b"\x00" * 2560], audio=b"should-not-record")

    assert result == b""
    model.predict.assert_not_called()


def test_concurrent_speaking_and_listening() -> None:
    detector = WakeWordDetector()
    speaker_ready = threading.Event()
    speaker_done = threading.Event()
    result_box: dict[str, bytes] = {}

    def speaker() -> None:
        tts_module.is_speaking = True
        speaker_ready.set()
        time.sleep(0.08)
        tts_module.is_speaking = False
        speaker_done.set()

    def listener() -> None:
        speaker_ready.wait(timeout=1.0)
        result, _ = _listen(detector, [_frame("hey jarvis from another thread")], timeout=0.1)
        result_box["result"] = result

    with patch.object(tts_module, "cooldown_until", 0.0):
        speaker_thread = threading.Thread(target=speaker)
        listener_thread = threading.Thread(target=listener)
        speaker_thread.start()
        listener_thread.start()
        speaker_thread.join()
        listener_thread.join()

    assert speaker_done.is_set()
    assert result_box["result"] == b""


def test_suppression_does_not_affect_push_to_talk() -> None:
    manager = PushToTalkManager()
    with patch("app.voice.push_to_talk.KEYBOARD_AVAILABLE", True):
        manager._active.set()
        with patch.object(tts_module, "is_speaking", True):
            speaking_state = manager.is_active()
        with patch.object(tts_module, "is_speaking", False):
            silent_state = manager.is_active()

    assert speaking_state is True
    assert silent_state is True
