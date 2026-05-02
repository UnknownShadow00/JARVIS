"""Phase 1 STT cleanup test without loading faster-whisper."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice.stt import stt


def run() -> None:
    cleaned = stt._clean_text("  um, hey JARVIS open VS Code  ")  # type: ignore[attr-defined]
    print(f"Cleaned text: {cleaned}")
    if cleaned != "hey JARVIS open VS Code":
        raise SystemExit("FAIL: filler cleanup did not match expectation")
    print("STT cleanup test passed. Live GPU transcription still requires manual audio validation.")


def test_stt_cleanup() -> None:
    run()


if __name__ == "__main__":
    run()
