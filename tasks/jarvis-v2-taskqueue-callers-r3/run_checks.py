#!/usr/bin/env python3
"""Standard-library source-level caller tests; no application/runtime imports."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import socket
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
FORBIDDEN = {"app.config", "app.logs.audit", "app.agent.task_queue", "app.agent.scheduler", "app.server"}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CountedResult(unittest.TextTestResult):
    subtests = 0

    def addSubTest(self, test, subtest, error):
        self.subtests += 1
        super().addSubTest(test, subtest, error)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="Expect failures against frozen R2 caller sources")
    parser.add_argument("--save-evidence", action="store_true")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    attempts = []

    def guard(event, arguments):
        prohibited = event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.gethostbyname"}
        if event == "socket.__new__" and len(arguments) > 1:
            prohibited = arguments[1] in {socket.AF_INET, socket.AF_INET6}
        if prohibited:
            attempts.append(event)
            raise RuntimeError("Offline fixtures prohibit network operations")

    sys.addaudithook(guard)
    callers = load("offline_callers", ROOT / "tests/test_task_queue_callers.py")
    suite = unittest.TestSuite()
    if args.baseline:
        callers.SOURCE_OVERRIDES.update({
            "agent/task_queue.py": PACKET / "task_queue.before.py",
            "agent/scheduler.py": PACKET / "scheduler.before.py",
            "server.py": PACKET / "server.before.py",
        })
    else:
        for name in ("test_task_queue_persistence", "test_task_queue_store_safety"):
            suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(load(name, ROOT / f"tests/{name}.py")))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(callers))
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=CountedResult).run(suite)
    forbidden = sorted(FORBIDDEN.intersection(sys.modules))
    files = [
        ROOT / "app/agent/task_queue.py", ROOT / "app/agent/scheduler.py", ROOT / "app/server.py",
        ROOT / "tests/test_agent_stubs.py", ROOT / "tests/test_task_queue_persistence.py",
        ROOT / "tests/test_task_queue_store_safety.py", ROOT / "tests/test_task_queue_callers.py",
        PACKET / "task_queue.before.py", PACKET / "scheduler.before.py", PACKET / "server.before.py",
        Path(__file__).resolve(),
    ]
    metadata = {
        "timestamp_utc": datetime.now(UTC).isoformat(), "python": sys.version,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "scope": "real isolated definitions + fresh files + audit/HTTP response recorders; not FastAPI/ASGI integration",
        "baseline": args.baseline, "expected_baseline_failures": args.baseline,
        "tests_run": result.testsRun, "subtests": result.subtests,
        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
        "success": result.wasSuccessful() and not forbidden and not attempts,
        "forbidden_modules_imported": forbidden, "blocked_parent_network_attempts": attempts,
        "sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    }
    report = json.dumps(metadata, indent=2) + "\n\n" + stream.getvalue()
    print(report, end="")
    if args.save_evidence:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        path = PACKET / f"{'baseline' if args.baseline else 'evidence'}-{stamp}.txt"
        with path.open("x", encoding="utf-8") as handle:
            handle.write(report)
        print(f"Saved {path.relative_to(ROOT)}")
    return 0 if metadata["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
