"""Voice pipeline control tests."""
from __future__ import annotations

import time

from app.voice.audio_stream import VoicePipeline
from app.voice import audio_stream


def test_voice_pipeline_stop_is_responsive(monkeypatch) -> None:  # noqa: ANN001
    calls: list[float | None] = []

    def fake_listen(timeout: float | None = None) -> bytes:
        calls.append(timeout)
        time.sleep(0.01)
        return b""

    monkeypatch.setattr(audio_stream.wake_word, "listen", fake_listen)
    monkeypatch.setattr(audio_stream.tts, "stop", lambda: None)

    pipeline = VoicePipeline()
    pipeline.listen_timeout_seconds = 0.01

    pipeline.start()
    time.sleep(0.05)
    pipeline.stop()
    assert pipeline._thread is not None
    pipeline._thread.join(timeout=1.0)

    assert calls, "wake_word.listen was not called"
    assert all(timeout == 0.01 for timeout in calls)
    assert not pipeline._thread.is_alive()
