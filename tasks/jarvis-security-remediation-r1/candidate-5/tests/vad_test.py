"""Phase 1 VAD WAV packaging test."""
from __future__ import annotations

import sys
import wave
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice.vad import vad


def run() -> None:
    wav_bytes = vad._to_wav_bytes([b"\x00\x00" * 160])  # type: ignore[attr-defined]
    with wave.open(BytesIO(wav_bytes), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getframerate() == 16000
        assert wav.getsampwidth() == 2
    print("VAD WAV packaging test passed.")


def test_vad_wav_packaging() -> None:
    run()


if __name__ == "__main__":
    run()
