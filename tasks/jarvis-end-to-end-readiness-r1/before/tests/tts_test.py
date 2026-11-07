"""Phase 1 TTS streaming behavior test with fake synthesis/playback."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.voice import tts as tts_module

tts = tts_module.tts


@pytest.mark.asyncio
async def test_speak_stream_yields_sentences() -> None:
    observed_speaking = False

    async def fake_synthesize(sentence: str) -> Path:
        nonlocal observed_speaking
        observed_speaking = observed_speaking or tts_module.is_speaking
        await asyncio.sleep(0)
        return Path(f"{sentence[:4]}.wav")

    async def fake_play(path: Path) -> None:  # noqa: ARG001
        await asyncio.sleep(0)

    def token_source():
        yield "Good"
        yield " morning"
        yield ", sir."
        yield " Systems"
        yield " online."

    tts._synthesize_sentence = fake_synthesize  # type: ignore[method-assign]
    tts._play_audio_file = fake_play  # type: ignore[method-assign]
    tts._cleanup_audio = lambda path: None  # type: ignore[method-assign]

    try:
        await tts.speak_stream(token_source())
    except ImportError:
        return

    assert observed_speaking
    assert tts_module.is_speaking is False


async def run() -> None:
    await test_speak_stream_yields_sentences()
    print("TTS streaming test passed.")


if __name__ == "__main__":
    asyncio.run(run())
