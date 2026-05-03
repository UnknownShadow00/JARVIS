"""Phase 1 STT cleanup test without loading faster-whisper."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice.stt import stt
from app.voice.stt import SpeechToText


def run() -> None:
    cleaned = stt._clean_text("  um, hey JARVIS open VS Code  ")  # type: ignore[attr-defined]
    print(f"Cleaned text: {cleaned}")
    if cleaned != "hey JARVIS open VS Code":
        raise SystemExit("FAIL: filler cleanup did not match expectation")
    print("STT cleanup test passed. Live GPU transcription still requires manual audio validation.")


def test_stt_cleanup() -> None:
    run()


def test_stt_cpu_fallback_after_transcribe_error(monkeypatch) -> None:  # noqa: ANN001
    calls: list[tuple[str | None, str | None, bool]] = []

    class Segment:
        text = " fallback works"

    class FailingModel:
        def transcribe(self, path: str, beam_size: int, vad_filter: bool):  # noqa: ARG002
            raise RuntimeError("Library cublas64_12.dll is not found or cannot be loaded")

    class CpuModel:
        def transcribe(self, path: str, beam_size: int, vad_filter: bool):  # noqa: ARG002
            return [Segment()], None

    subject = SpeechToText()

    def fake_load_model(device=None, compute_type=None, force_reload=False):  # noqa: ANN001
        calls.append((device, compute_type, force_reload))
        if device == "cpu":
            return CpuModel()
        return FailingModel()

    monkeypatch.setattr(subject, "_load_model", fake_load_model)
    assert subject.transcribe(b"fake wav") == "fallback works"
    assert calls == [(None, None, False), ("cpu", "int8", True)]


if __name__ == "__main__":
    run()
