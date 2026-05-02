"""Manual smoke tests — require real audio hardware. Run with: pytest -m manual"""
from __future__ import annotations

import asyncio
import time
from pathlib import Path

import pytest


@pytest.mark.manual
def test_tts_speaks() -> None:
    try:
        from app.voice.tts import tts
        import app.voice.tts as tts_mod
    except ImportError as exc:
        pytest.skip(f"tts unavailable: {exc}")

    asyncio.run(tts.speak("Testing, sir."))
    assert tts_mod.is_speaking is False


@pytest.mark.manual
def test_sfx_plays() -> None:
    try:
        from app.voice.sounds import sounds
    except ImportError as exc:
        pytest.skip(f"sounds unavailable: {exc}")

    sounds.play("done")


@pytest.mark.manual
def test_vad_records() -> None:
    try:
        from app.voice.vad import record_until_silence
    except ImportError as exc:
        pytest.skip(f"vad unavailable: {exc}")

    result = record_until_silence(timeout=3.0)
    assert isinstance(result, bytes)


@pytest.mark.manual
def test_stt_transcribes() -> None:
    try:
        from app.voice.stt import transcribe
    except ImportError as exc:
        pytest.skip(f"stt unavailable: {exc}")

    fixture = Path(__file__).parent / "fixtures" / "test_audio.wav"
    if not fixture.is_file():
        assert transcribe(b"") == ""
        return

    result = transcribe(fixture.read_bytes())
    assert isinstance(result, str) and len(result) > 0


@pytest.mark.manual
def test_wake_word_listens() -> None:
    try:
        from app.voice.wake_word import WakeWordDetector
    except ImportError as exc:
        pytest.skip(f"wake_word unavailable: {exc}")

    detector = WakeWordDetector()
    result = detector.listen(timeout=10.0)
    assert isinstance(result, bytes)


@pytest.mark.manual
def test_self_suppression() -> None:
    try:
        from app.voice.wake_word import WakeWordDetector
        import app.voice.tts as tts_mod
    except ImportError as exc:
        pytest.skip(f"dependencies unavailable: {exc}")

    original = tts_mod.is_speaking
    tts_mod.is_speaking = True
    try:
        detector = WakeWordDetector()
        start = time.monotonic()
        result = detector.listen(timeout=2.0)
        elapsed = time.monotonic() - start
        assert isinstance(result, bytes)
        assert result == b""
        assert elapsed < 3.0, f"self-suppression took {elapsed:.2f}s; expected timeout to be honored"
        assert tts_mod.is_speaking is True
    finally:
        tts_mod.is_speaking = original
