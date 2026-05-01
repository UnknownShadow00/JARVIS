"""Phase 1 boot sequence unit test with model/audio/network fakes."""
from __future__ import annotations

import asyncio
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import boot


async def run() -> None:
    async def fake_wait_for_ollama(timeout_seconds: float = 30.0) -> None:  # noqa: ARG001
        return None

    async def fake_speak(text: str) -> None:  # noqa: ARG001
        await asyncio.sleep(0.01)

    async def fake_chat(messages):  # noqa: ANN001, ARG001
        return boot.deterministic_report(boot.build_status_context())

    boot.wait_for_ollama = fake_wait_for_ollama  # type: ignore[assignment]
    boot.llm_client.chat = fake_chat  # type: ignore[method-assign]
    boot.tts.speak = fake_speak  # type: ignore[method-assign]
    boot.sounds.play = lambda sound_name: True  # type: ignore[method-assign]

    started_at = time.perf_counter()
    report = await boot.boot_sequence(start_server=False, start_hud=False, start_voice=False)
    elapsed = time.perf_counter() - started_at

    print(report)
    print(f"Boot test completed in {elapsed:.3f}s")

    lower = report.lower()
    if "sir" not in lower or "time" not in lower or "gpu" not in lower:
        raise SystemExit("FAIL: report missing expected status fields")
    if elapsed >= 10:
        raise SystemExit("FAIL: boot sequence exceeded 10s")
    print("Boot sequence test passed.")


if __name__ == "__main__":
    asyncio.run(run())
