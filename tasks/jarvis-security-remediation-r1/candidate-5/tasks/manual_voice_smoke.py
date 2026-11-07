from __future__ import annotations

import argparse
import asyncio
from collections.abc import AsyncIterator
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Literal

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain.router import RouterResult
from app.config_check import check_startup
from app.server import _process, _process_stream
from app.voice import audio_stream
from app.voice.stt import stt
from app.voice.tts import tts
from app.voice.wake_word import wake_word


Status = Literal["pass", "fail", "skip"]


@dataclass
class StepResult:
    name: str
    status: Status
    detail: str


def _format_result(result: StepResult) -> str:
    return f"{result.status.upper():4} {result.name}: {result.detail}"


async def _run_text_path(text: str, *, speak: bool) -> list[StepResult]:
    results: list[StepResult] = []

    try:
        stream_result = await _process_stream(text)
    except Exception as exc:
        stream_result = None
        results.append(StepResult("router/stream", "fail", f"{type(exc).__name__}: {exc}"))
    else:
        results.append(
            StepResult(
                "router/stream",
                "pass" if stream_result is not None else "skip",
                "streaming path available" if stream_result is not None else "fell back to non-streaming response",
            )
        )

    if stream_result is not None:
        token_stream, intent = stream_result
        chunks: list[str] = []

        async def tee_tokens() -> AsyncIterator[str]:
            async for chunk in token_stream:
                chunks.append(chunk)
                yield chunk

        try:
            if speak:
                await tts.speak_stream(tee_tokens())
            else:
                async for _chunk in tee_tokens():
                    pass
        except Exception as exc:
            results.append(
                StepResult(
                    "response",
                    "fail",
                    f"{type(exc).__name__}: streaming response failed; check Ollama/model availability",
                )
            )
            return results

        reply = "".join(chunks).strip()
        results.append(StepResult("response", "pass" if reply else "fail", f"{intent.intent}: {reply[:120]}"))
        return results

    try:
        reply, intent = await _process(text)
    except Exception as exc:
        results.append(StepResult("response", "fail", f"{type(exc).__name__}: {exc}"))
        return results

    results.append(StepResult("response", "pass" if reply else "fail", f"{intent.intent}: {reply[:120]}"))
    if speak:
        await tts.speak(reply)
        results.append(StepResult("tts", "pass", "speak() returned without raising"))
    else:
        results.append(StepResult("tts", "skip", "use --speak to play synthesized audio"))
    return results


async def _run_live_path(args: argparse.Namespace) -> list[StepResult]:
    results: list[StepResult] = []
    startup = check_startup()
    for name in ("piper_binary", "piper_model", "wake_model", "ollama_reachable"):
        ok = startup[name]
        results.append(StepResult(f"startup/{name}", "pass" if ok else "fail", str(ok)))

    print("Listening once. Use the wake word or hold the configured push-to-talk key.")
    audio = await asyncio.to_thread(wake_word.listen, timeout=args.listen_timeout)
    if not audio:
        results.append(
            StepResult(
                "wake_or_ptt",
                "fail",
                "no audio captured; check microphone, openwakeword model, push-to-talk key, or VAD",
            )
        )
        return results

    results.append(StepResult("wake_or_ptt", "pass", f"captured {len(audio)} bytes"))
    text = await asyncio.to_thread(stt.transcribe, audio)
    if not text:
        results.append(StepResult("stt", "fail", "empty transcript; check faster-whisper model/device/assets"))
        return results

    results.append(StepResult("stt", "pass", text))
    results.extend(await _run_text_path(text, speak=True))
    return results


async def _run_pipeline_mock(args: argparse.Namespace) -> list[StepResult]:
    original_listen = audio_stream.wake_word.listen
    original_transcribe = audio_stream.stt.transcribe
    original_stream = audio_stream._process_stream
    original_process = audio_stream._process
    original_speak_stream = audio_stream.tts.speak_stream
    original_speak = audio_stream.tts.speak

    events: list[str] = []

    def fake_listen(timeout: float | None = None) -> bytes:
        events.append(f"listen:{timeout}")
        audio_stream.voice_pipeline.stop()
        return b"mock-wav"

    def fake_transcribe(audio: bytes) -> str:
        events.append(f"stt:{len(audio)}")
        return args.text

    async def fake_stream(text: str):
        events.append(f"stream:{text}")

        async def tokens() -> AsyncIterator[str]:
            yield "Ready, sir."

        return tokens(), RouterResult("respond", 1.0, "", "manual smoke")

    async def fake_process(text: str):
        events.append(f"process:{text}")
        return "Ready, sir.", RouterResult("respond", 1.0, "", "manual smoke")

    async def fake_speak_stream(tokens: AsyncIterator[str]) -> None:
        async for token in tokens:
            events.append(f"tts_stream:{token}")

    async def fake_speak(text: str) -> None:
        events.append(f"tts:{text}")

    audio_stream.wake_word.listen = fake_listen
    audio_stream.stt.transcribe = fake_transcribe
    audio_stream._process_stream = fake_stream
    audio_stream._process = fake_process
    audio_stream.tts.speak_stream = fake_speak_stream
    audio_stream.tts.speak = fake_speak
    audio_stream.voice_pipeline.listen_timeout_seconds = 0.01

    try:
        await audio_stream.voice_pipeline.run()
    finally:
        audio_stream.wake_word.listen = original_listen
        audio_stream.stt.transcribe = original_transcribe
        audio_stream._process_stream = original_stream
        audio_stream._process = original_process
        audio_stream.tts.speak_stream = original_speak_stream
        audio_stream.tts.speak = original_speak

    expected = ["listen:", "stt:", "stream:", "tts_stream:"]
    missing = [prefix for prefix in expected if not any(event.startswith(prefix) for event in events)]
    return [
        StepResult(
            "pipeline_order",
            "pass" if not missing else "fail",
            " -> ".join(events) if events else f"missing {missing}",
        )
    ]


async def main() -> int:
    parser = argparse.ArgumentParser(description="Manual MVP voice-loop smoke test.")
    parser.add_argument("--live", action="store_true", help="Capture one wake-word or push-to-talk interaction.")
    parser.add_argument("--mock-pipeline", action="store_true", help="Run the pipeline order without hardware/models.")
    parser.add_argument("--text", default="hello jarvis", help="Text to send through router/response/TTS.")
    parser.add_argument("--speak", action="store_true", help="Play TTS for the text path.")
    parser.add_argument("--listen-timeout", type=float, default=15.0, help="Seconds to wait for wake/PTT in live mode.")
    args = parser.parse_args()

    if args.live:
        results = await _run_live_path(args)
    elif args.mock_pipeline:
        results = await _run_pipeline_mock(args)
    else:
        results = await _run_text_path(args.text, speak=args.speak)

    for result in results:
        print(_format_result(result))

    return 1 if any(result.status == "fail" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
