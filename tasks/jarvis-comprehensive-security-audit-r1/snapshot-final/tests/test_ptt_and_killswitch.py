from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from app.brain import kill_switch
from app.voice.wake_word import wake_word


def _reset_kill_switch() -> None:
    kill_switch.reset()
    kill_switch._callbacks.clear()


def test_ptt_bypasses_model() -> None:
    with patch.dict(sys.modules, {"keyboard": MagicMock()}):
        with patch("keyboard.is_pressed", return_value=True), patch(
            "app.voice.vad.vad.record_until_silence", return_value=b"pttaudio"
        ), patch("app.voice.wake_word.sounds.play"), patch.object(
            wake_word, "_load_model", side_effect=AssertionError("_load_model should not be called")
        ):
            assert wake_word.listen() == b"pttaudio"


def test_ptt_plays_listening_sound() -> None:
    with patch.dict(sys.modules, {"keyboard": MagicMock()}):
        with patch("keyboard.is_pressed", return_value=True), patch(
            "app.voice.vad.vad.record_until_silence", return_value=b"pttaudio"
        ), patch("app.voice.wake_word.sounds.play") as mock_play, patch.object(wake_word, "_load_model"):
            wake_word.listen()
    mock_play.assert_called_once_with("listening")


def test_ptt_during_listen_window_records_audio() -> None:
    detector = wake_word.__class__()
    stream = MagicMock()
    stream.__enter__.return_value = stream
    stream.__exit__.return_value = False
    sd = MagicMock(RawInputStream=MagicMock(return_value=stream))
    np = MagicMock()
    model = MagicMock()

    with patch.dict(sys.modules, {"sounddevice": sd, "numpy": np}):
        with patch.object(detector, "_load_model", return_value=model), patch.object(
            detector, "_push_to_talk_active", side_effect=[False, True]
        ), patch("app.voice.vad.vad.record_until_silence", return_value=b"pttaudio"), patch(
            "app.voice.wake_word.sounds.play"
        ):
            assert detector.listen(timeout=0.2) == b"pttaudio"

    model.predict.assert_not_called()


def test_trigger_sets_inactive() -> None:
    _reset_kill_switch()
    kill_switch.trigger()
    assert kill_switch.JARVIS_ACTIVE is False


def test_trigger_fires_callbacks() -> None:
    _reset_kill_switch()
    mock_fn = MagicMock()
    kill_switch.register_callback(mock_fn)
    kill_switch.trigger()
    mock_fn.assert_called_once_with()


def test_reset_restores_active() -> None:
    _reset_kill_switch()
    kill_switch.trigger()
    kill_switch.reset()
    assert kill_switch.JARVIS_ACTIVE is True


def test_double_trigger_idempotent() -> None:
    _reset_kill_switch()
    kill_switch.trigger()
    kill_switch.trigger()
    assert kill_switch.JARVIS_ACTIVE is False
