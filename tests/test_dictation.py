from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.config import load_settings, settings
from app.voice import audio_stream
from app.voice import dictation as dictation_module
from app.voice.dictation import Dictation
from app.voice.push_to_talk import PushToTalkManager


pytestmark = pytest.mark.unit


def _contains_text(value, needle: str) -> bool:  # noqa: ANN001
    if isinstance(value, str):
        return needle in value
    if isinstance(value, dict):
        return any(_contains_text(item, needle) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_text(item, needle) for item in value)
    return False


def test_dictation_writes_clipboard_without_raw_audit(monkeypatch) -> None:
    secret = "private wiring note"
    copied: list[str] = []
    events: list[tuple[str, dict]] = []

    monkeypatch.setattr(settings.voice, "dictation_enabled", True)
    monkeypatch.setattr(settings.voice, "dictation_type_out", False)
    monkeypatch.setattr(dictation_module, "PYPERCLIP_AVAILABLE", True)
    monkeypatch.setattr(dictation_module, "pyperclip", SimpleNamespace(copy=copied.append))
    monkeypatch.setattr(dictation_module.audit, "log", lambda event, data: events.append((event, data)))

    assert Dictation().handle_transcript(f"  {secret}  ") is True

    assert copied == [secret]
    assert events[-1] == ("dictation_handled", {"chars": len(secret), "type_out": False})
    assert not any(_contains_text(data, secret) for _event, data in events)


def test_dictation_type_out_requires_flag_and_live_mode(monkeypatch) -> None:
    typed: list[str] = []

    monkeypatch.setattr(settings.voice, "dictation_enabled", True)
    monkeypatch.setattr(settings.voice, "dictation_type_out", True)
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(dictation_module, "PYPERCLIP_AVAILABLE", True)
    monkeypatch.setattr(dictation_module, "PYAUTOGUI_AVAILABLE", True)
    monkeypatch.setattr(dictation_module, "pyperclip", SimpleNamespace(copy=lambda _text: None))
    monkeypatch.setattr(dictation_module, "pyautogui", SimpleNamespace(write=typed.append))
    monkeypatch.setattr(dictation_module.audit, "log", lambda *_args, **_kwargs: None)

    assert Dictation().handle_transcript("type this") is True
    assert typed == ["type this"]

    typed.clear()
    monkeypatch.setattr(settings.safety, "dry_run", True)

    assert Dictation().handle_transcript("do not type this") is True
    assert typed == []


def test_dictation_gracefully_degrades_without_optional_dependencies(monkeypatch) -> None:
    events: list[tuple[str, dict]] = []

    monkeypatch.setattr(settings.voice, "dictation_enabled", True)
    monkeypatch.setattr(settings.voice, "dictation_type_out", False)
    monkeypatch.setattr(dictation_module, "PYPERCLIP_AVAILABLE", False)
    monkeypatch.setattr(dictation_module, "pyperclip", None)
    monkeypatch.setattr(dictation_module.audit, "log", lambda event, data: events.append((event, data)))

    assert Dictation().handle_transcript("clipboard unavailable") is False
    assert ("dictation_unavailable", {"chars": 21, "dependency": "pyperclip"}) in events


def test_push_to_talk_manager_tracks_dictation_hotkey(monkeypatch) -> None:
    calls: list[tuple[str, str]] = []
    unhooked: list[str] = []
    keyboard = SimpleNamespace(
        on_press_key=lambda key, callback: calls.append(("press", key)) or f"press:{key}",
        on_release_key=lambda key, callback: calls.append(("release", key)) or f"release:{key}",
        unhook=unhooked.append,
    )
    dictation_presses: list[str] = []
    dictation_releases: list[str] = []

    monkeypatch.setattr(settings.voice, "dictation_enabled", True)
    monkeypatch.setattr("app.voice.push_to_talk.KEYBOARD_AVAILABLE", True)
    monkeypatch.setattr("app.voice.push_to_talk.keyboard", keyboard)

    manager = PushToTalkManager(hotkey="ctrl+space", dictation_hotkey="ctrl+shift+space")
    manager.on_dictation_press(lambda: dictation_presses.append("down"))
    manager.on_dictation_release(lambda: dictation_releases.append("up"))
    manager.start()

    assert calls == [
        ("press", "ctrl+space"),
        ("release", "ctrl+space"),
        ("press", "ctrl+shift+space"),
        ("release", "ctrl+shift+space"),
    ]

    manager._handle_dictation_press(None)
    assert manager.is_dictation_active() is True
    manager._handle_dictation_release(None)
    assert manager.is_dictation_active() is False
    assert dictation_presses == ["down"]
    assert dictation_releases == ["up"]

    manager.stop()
    assert unhooked == [
        "press:ctrl+space",
        "release:ctrl+space",
        "press:ctrl+shift+space",
        "release:ctrl+shift+space",
    ]


@pytest.mark.asyncio
async def test_voice_pipeline_dictation_skips_brain_and_tts(monkeypatch) -> None:
    pipeline = audio_stream.VoicePipeline()
    handled: list[str] = []

    def fake_listen(timeout: float | None = None) -> bytes:
        audio_stream.wake_word.last_trigger = "dictation"
        pipeline.stop()
        return b"mock-wav"

    monkeypatch.setattr(audio_stream.wake_word, "listen", fake_listen)
    monkeypatch.setattr(audio_stream.stt, "transcribe", lambda _audio: "private transcript")
    monkeypatch.setattr(audio_stream.dictation, "handle_transcript", handled.append)
    monkeypatch.setattr(audio_stream, "_process_stream", AsyncMock(side_effect=AssertionError("LLM should not run")))
    monkeypatch.setattr(audio_stream, "_process", AsyncMock(side_effect=AssertionError("LLM should not run")))
    monkeypatch.setattr(audio_stream.tts, "speak_stream", AsyncMock(side_effect=AssertionError("TTS should not run")))
    monkeypatch.setattr(audio_stream.tts, "speak", AsyncMock(side_effect=AssertionError("TTS should not run")))

    await pipeline.run()

    assert handled == ["private transcript"]


def test_dictation_config_defaults_present() -> None:
    loaded = load_settings()

    assert loaded.voice.dictation_enabled is True
    assert loaded.voice.dictation_hotkey == "ctrl+shift+space"
    assert loaded.voice.dictation_type_out is False
