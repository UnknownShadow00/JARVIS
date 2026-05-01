"""Phase 1 TTS streaming behavior test with fake synthesis/playback."""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice.tts import tts


async def run() -> None:
    first_play_at = None

    async def fake_synthesize(sentence: str) -> Path:
        await asyncio.sleep(0.05)
        return Path(f"{sentence[:4]}.wav")

    async def fake_play(path: Path) -> None:  # noqa: ARG001
        nonlocal first_play_at
        if first_play_at is None:
            first_play_at = time.perf_counter()
        await asyncio.sleep(0.05)

    tts._synthesize_sentence = fake_synthesize  # type: ignore[method-assign]
    tts._play_audio_file = fake_play  # type: ignore[method-assign]
    tts._cleanup_audio = lambda path: None  # type: ignore[method-assign]

    started_at = time.perf_counter()
    await tts.speak("Good morning sir. All systems are operational.")

    assert first_play_at is not None
    elapsed = first_play_at - started_at
    print(f"First audio chunk started in {elapsed:.3f}s")
    if elapsed >= 0.5:
        raise SystemExit("FAIL: first audio chunk did not start within 0.5s")
    print("TTS streaming test passed.")


if __name__ == "__main__":
    asyncio.run(run())
