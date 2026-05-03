"""Task 0.6 acceptance test - IntentRouter, 20 queries, all 5 intents."""
from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain.router import RouterResult, router

QUERIES: list[tuple[str, str]] = [
    ("What time is it?", "respond"),
    ("Tell me a joke.", "respond"),
    ("What is the capital of France?", "respond"),
    ("How are you doing today?", "respond"),
    ("What is my CPU usage right now?", "use_tool"),
    ("Search the web for the latest RTX 5090 benchmarks.", "use_tool"),
    ("Open Visual Studio Code.", "use_tool"),
    ("Show me the files in my downloads folder.", "use_tool"),
    ("What is the weather like in Dallas today?", "use_tool"),
    ("What was the last project I worked on?", "retrieve_memory"),
    ("Do you remember what I asked you yesterday?", "retrieve_memory"),
    ("What tasks do I have pending?", "retrieve_memory"),
    ("What did I tell you about my hardware setup?", "retrieve_memory"),
    ("What do you see on my screen right now?", "vision"),
    ("Take a screenshot and describe it.", "use_tool"),
    ("Look at my webcam and tell me what you see.", "vision"),
    ("Delete all files in my downloads folder.", "confirm_action"),
    ("Send a Discord message to my team saying the build is done.", "confirm_action"),
    ("Install all the packages in requirements.txt.", "confirm_action"),
    ("Commit and push everything to GitHub.", "confirm_action"),
]

VALID_INTENTS = {"respond", "use_tool", "retrieve_memory", "vision", "confirm_action"}
MAX_MS = 1000


def run() -> None:
    print(f"\nTesting IntentRouter - {len(QUERIES)} queries\n{'=' * 60}")

    seen_intents: set[str] = set()
    failures: list[str] = []

    for query, expected in QUERIES:
        t0 = time.perf_counter()
        result: RouterResult = router.classify(query)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        seen_intents.add(result.intent)

        checks = [
            elapsed_ms < MAX_MS,
            result.intent in VALID_INTENTS,
            0.0 <= result.confidence <= 1.0,
            result.intent == expected,
        ]
        status = "PASS" if all(checks) else "FAIL"

        print(
            f"[{status}] {elapsed_ms:6.0f}ms | got={result.intent:<16} expected={expected}\n"
            f"       conf={result.confidence:.2f} | tool={result.suggested_tool or '-'} | q={query[:60]}"
        )

        if not all(checks):
            failures.append(query)

    print(f"\n{'=' * 60}")
    print(f"Intents seen: {sorted(seen_intents)}")

    missing = VALID_INTENTS - seen_intents
    if missing:
        failures.append(f"Missing intents: {sorted(missing)}")

    if failures:
        print(f"\nFAILED ({len(failures)}):")
        for f in failures:
            print(f"  - {f}")
        raise SystemExit(1)

    print(f"\nAll {len(QUERIES)} queries passed.")


def test_router_classifies_known_queries() -> None:
    run()


def test_routes_shell() -> None:
    result = router.classify("run npm install")
    assert result.intent == "use_tool"
    assert result.suggested_tool == "shell"


def test_routes_calendar() -> None:
    result = router.classify("what do I have on my calendar today")
    assert result.intent == "use_tool"
    assert result.suggested_tool == "calendar"


def test_routes_browser() -> None:
    result = router.classify("go to youtube.com")
    assert result.intent == "use_tool"
    assert result.suggested_tool == "browser"


def test_routes_screenshot_tool() -> None:
    result = router.classify("take a screenshot")
    assert result.intent == "use_tool"
    assert result.suggested_tool == "screenshot"


def test_routes_webcam_vision() -> None:
    result = router.classify("look at my webcam")
    assert result.intent == "vision"


if __name__ == "__main__":
    run()
