from __future__ import annotations

from pathlib import Path
import tempfile

import pytest

from app.voice import tts as tts_module


class _FakeTensor:
    def numpy(self) -> list[float]:
        return [0.0, 0.1, -0.1]


def _temp_wav_path() -> Path:
    temp_dir = Path.cwd() / "tasks"
    temp_dir.mkdir(parents=True, exist_ok=True)
    handle = tempfile.NamedTemporaryFile(dir=temp_dir, suffix=".wav", delete=False)
    handle.close()
    return Path(handle.name)


@pytest.mark.asyncio
async def test_chatterbox_unavailable_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = tts_module.TTSEngine()
    events: list[tuple[str, dict]] = []
    fallback_calls: list[str] = []

    def fake_log(event: str, data: dict) -> None:
        events.append((event, data))

    def fake_piper(sentence: str) -> Path:
        fallback_calls.append(sentence)
        output = _temp_wav_path()
        output.write_bytes(b"wav")
        return output

    async def fake_play(_: Path) -> None:
        return None

    monkeypatch.setattr(tts_module.audit, "log", fake_log)
    monkeypatch.setattr(tts_module, "CHATTERBOX_AVAILABLE", False)
    monkeypatch.setattr(tts_module.settings.voice, "tts_engine", "chatterbox")
    monkeypatch.setattr(engine, "_synthesize_piper", fake_piper)
    monkeypatch.setattr(engine, "_play_audio_file", fake_play)
    monkeypatch.setattr(engine, "_cleanup_audio", lambda _: None)
    monkeypatch.setattr(tts_module.sounds, "play", lambda _: True)

    await engine.speak("Fallback test.")

    assert fallback_calls == ["Fallback test."]
    assert ("tts_unavailable", {"engine": "chatterbox", "reason": "import_error_fallback_to_piper"}) in events


@pytest.mark.asyncio
async def test_chatterbox_available_generates(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = tts_module.TTSEngine()
    events: list[tuple[str, dict]] = []
    generated: list[str] = []

    class FakeModel:
        def generate(self, text: str, **_: object) -> _FakeTensor:
            generated.append(text)
            return _FakeTensor()

    class FakeChatterboxTTS:
        @staticmethod
        def from_pretrained(*, device: str, **_: object) -> FakeModel:
            assert device == "cuda"
            return FakeModel()

    def fake_log(event: str, data: dict) -> None:
        events.append((event, data))

    def fake_write(path: Path, wav: object) -> None:
        assert isinstance(wav, _FakeTensor)
        path.write_bytes(b"wav")

    async def fake_play(_: Path) -> None:
        return None

    monkeypatch.setattr(tts_module.audit, "log", fake_log)
    monkeypatch.setattr(tts_module, "CHATTERBOX_AVAILABLE", True)
    monkeypatch.setattr(tts_module, "_ChatterboxTTS", FakeChatterboxTTS)
    monkeypatch.setattr(tts_module.settings.voice, "tts_engine", "chatterbox")
    monkeypatch.setattr(tts_module.settings.voice, "voice_clone_path", "")
    monkeypatch.setattr(engine, "_write_wav_file", fake_write)
    monkeypatch.setattr(engine, "_play_audio_file", fake_play)
    monkeypatch.setattr(engine, "_cleanup_audio", lambda _: None)
    monkeypatch.setattr(tts_module.sounds, "play", lambda _: True)

    await engine.speak("Generate this.")

    assert generated == ["Generate this."]
    assert ("tts_chatterbox", {"text_length": len("Generate this.")}) in events


def test_get_chatterbox_caches_model(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = tts_module.TTSEngine()
    calls: list[str] = []
    model = object()

    class FakeChatterboxTTS:
        @staticmethod
        def from_pretrained(*, device: str, **_: object) -> object:
            calls.append(device)
            return model

    monkeypatch.setattr(tts_module, "CHATTERBOX_AVAILABLE", True)
    monkeypatch.setattr(tts_module, "_ChatterboxTTS", FakeChatterboxTTS)
    monkeypatch.setattr(tts_module.settings.voice, "voice_clone_path", "")

    first = engine._get_chatterbox()
    second = engine._get_chatterbox()

    assert first is model
    assert second is model
    assert calls == ["cuda"]
