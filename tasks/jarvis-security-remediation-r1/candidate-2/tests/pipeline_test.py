"""Phase 0 pipeline integration test - deterministic text pipeline checks."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain.kill_switch import reset
from app.config import settings
from app.server import _process, llm_client


async def _fake_chat(messages, model=None, stream=False, **kwargs):  # noqa: ANN001, ARG001
    return "Ready, sir."


async def run() -> None:
    print("\nPhase 0 Pipeline Test\n" + "=" * 50)
    reset()
    settings.safety.dry_run = True
    llm_client.chat = _fake_chat  # type: ignore[method-assign]

    cases = [
        ("What time is it, sir?", "respond"),
        ("What is my CPU usage?", "use_tool"),
        ("What was the last project I worked on?", "retrieve_memory"),
        ("Delete everything in downloads.", "confirm_action"),
        ("open VS Code", "use_tool"),
        ("JARVIS stop", "confirm_action"),
    ]

    failures = []
    for message, expected_intent in cases:
        reply, intent = await _process(message)
        print(f"\n[{intent.intent.upper()}] expected={expected_intent}")
        print(f"  Q: {message}")
        print(f"  A: {reply[:160]}")
        print(f"  conf={intent.confidence:.2f}")

        ok = True
        if not reply or not isinstance(reply, str):
            print("  FAIL: empty reply")
            ok = False
        if intent.intent != expected_intent:
            print(f"  FAIL: expected {expected_intent}, got {intent.intent}")
            ok = False
        if message == "open VS Code" and "Dry run mode is active" not in reply:
            print("  FAIL: dry-run launch was not narrated")
            ok = False
        if message == "JARVIS stop" and "Standing by" not in reply:
            print("  FAIL: kill switch response missing")
            ok = False

        if ok:
            print("  PASS")
        else:
            failures.append(message)

    print("\n" + "=" * 50)
    if failures:
        print(f"FAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)
    print(f"All {len(cases)} pipeline tests passed.")


@pytest.mark.asyncio
async def test_text_pipeline() -> None:
    await run()


if __name__ == "__main__":
    asyncio.run(run())
