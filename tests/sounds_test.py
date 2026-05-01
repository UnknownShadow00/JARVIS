"""Phase 1 sound placeholder test."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice.sounds import SOUND_FILES, sounds


def run() -> None:
    missing = [name for name in SOUND_FILES if sounds.sound_path(name) is None]
    if missing:
        raise SystemExit(f"FAIL: missing placeholder sounds: {missing}")

    print(f"Found {len(SOUND_FILES)} sound placeholders.")
    if not sounds.play("done"):
        raise SystemExit("FAIL: done sound did not dispatch")
    print("Sound placeholder test passed.")


if __name__ == "__main__":
    run()
