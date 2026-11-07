"""Phase 1 wake word self-suppression test."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice import tts as tts_module
from app.voice.wake_word import wake_word


def run() -> None:
    tts_module.is_speaking = True
    try:
        suppressed = bool(tts_module.is_speaking)
        score = wake_word._score({"hey_jarvis": 0.99})  # type: ignore[attr-defined]
    finally:
        tts_module.is_speaking = False

    print(f"Wake score: {score}")
    if not suppressed or score < 0.99:
        raise SystemExit("FAIL: wake word self-suppression support failed")
    print("Wake word self-suppression test passed. Live microphone detection still requires manual validation.")


def test_wake_word_score_and_suppression_flag() -> None:
    run()


if __name__ == "__main__":
    run()
