"""Phase 0 deterministic direct response tests."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain.direct_responder import try_direct_reply


def run() -> None:
    print("\nDirect Responder Test\n" + "=" * 50)

    cases = {
        "what is 2+2": "4, sir.",
        "Jarvis, calculate (10 - 2) / 4": "2, sir.",
        "explain power supplies": None,
        "__import__('os').system('whoami')": None,
    }

    failures = []
    for message, expected in cases.items():
        actual = try_direct_reply(message)
        print(f"{message!r} -> {actual!r}")
        if actual != expected:
            failures.append((message, expected, actual))

    if failures:
        for message, expected, actual in failures:
            print(f"FAIL: {message!r}: expected {expected!r}, got {actual!r}")
        raise SystemExit(1)

    print(f"All {len(cases)} direct responder tests passed.")


if __name__ == "__main__":
    run()
