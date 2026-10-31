#!/usr/bin/env python3
"""Offline source-level regressions and an explicitly unresolved stale-writer probe."""
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
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
FORBIDDEN = {"app.config", "app.logs.audit", "app.agent.task_queue", "app.agent.scheduler"}


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


def stale_writer_probe(helpers):
    """Demonstrate the known limitation; NOT part of passing test assertions."""
    import asyncio

    module = helpers.load_definitions(
        ROOT / "app/agent/task_queue.py", injected={"audit": helpers.AuditRecorder()},
        remove_singleton="task_queue",
    )
    with tempfile.TemporaryDirectory(prefix="jarvis-stale-writer-") as temporary:
        store = Path(temporary) / "tasks.json"
        first, stale = module.TaskQueue(store), module.TaskQueue(store)
        with mock.patch.object(module.uuid, "uuid4", return_value="aaaaaaaa-first"):
            asyncio.run(first.add_task("first writer"))
        first_bytes = store.read_bytes()
        with mock.patch.object(module.uuid, "uuid4", return_value="bbbbbbbb-stale"):
            asyncio.run(stale.add_task("stale writer"))
        return {
            "scope": "two independent instances, sequential writes, fresh disposable store",
            "status": "KNOWN LIMITATION DEMONSTRATED; no locking/lost-update fix claimed",
            "first_snapshot_sha256": hashlib.sha256(first_bytes).hexdigest(),
            "final_snapshot_sha256": hashlib.sha256(store.read_bytes()).hexdigest(),
            "final_ids": [record["task_id"] for record in json.loads(store.read_text())],
            "first_task_lost_from_disk": "aaaaaaaa" not in store.read_text(),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", action="store_true", help="New tests against frozen R1 source; expect failure")
    parser.add_argument("--save-evidence", action="store_true")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    network_attempts = []

    def network_guard(event, arguments):
        prohibited = event in {"socket.connect", "socket.bind", "socket.getaddrinfo", "socket.gethostbyname"}
        if event == "socket.__new__" and len(arguments) > 1:
            prohibited = arguments[1] in {socket.AF_INET, socket.AF_INET6}
        if prohibited:
            network_attempts.append(event)
            raise RuntimeError("Network operations prohibited in offline fixtures")

    sys.addaudithook(network_guard)
    old = load("offline_persistence", ROOT / "tests/test_task_queue_persistence.py")
    new = load("offline_store_safety", ROOT / "tests/test_task_queue_store_safety.py")
    suite = unittest.TestSuite()
    if args.baseline:
        original_loader = new.helpers.load_definitions

        def frozen_loader(path, **kwargs):
            if Path(path) == ROOT / "app/agent/task_queue.py":
                path = PACKET / "task_queue.before.py"
            return original_loader(path, **kwargs)

        new.helpers.load_definitions = frozen_loader
    else:
        suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(old))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(new))
    output = io.StringIO()
    result = unittest.TextTestRunner(
        stream=output, verbosity=2, resultclass=CountedResult,
    ).run(suite)
    stale = stale_writer_probe(old) if not args.baseline else None
    forbidden = sorted(FORBIDDEN.intersection(sys.modules))
    paths = [
        ROOT / "app/agent/task_queue.py", ROOT / "app/agent/scheduler.py",
        ROOT / "tests/test_agent_stubs.py", ROOT / "tests/test_task_queue_persistence.py",
        ROOT / "tests/test_task_queue_store_safety.py", PACKET / "task_queue.before.py",
        Path(__file__).resolve(),
    ]
    metadata = {
        "timestamp_utc": datetime.now(UTC).isoformat(), "python": sys.version,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "baseline": args.baseline, "expected_baseline_failures": args.baseline,
        "scope": "isolated actual definitions with in-memory audit; not app/live isolation validation",
        "tests_run": result.testsRun, "subtests": result.subtests,
        "failures": len(result.failures), "errors": len(result.errors), "skipped": len(result.skipped),
        "success": result.wasSuccessful() and not forbidden and not network_attempts,
        "forbidden_imports": forbidden, "blocked_network_attempts": network_attempts,
        "sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        "known_stale_writer_limitation": stale,
    }
    evidence = json.dumps(metadata, indent=2) + "\n\n" + output.getvalue()
    print(evidence, end="")
    if args.save_evidence:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        path = PACKET / f"{'baseline' if args.baseline else 'evidence'}-{stamp}.txt"
        with path.open("x", encoding="utf-8") as handle:
            handle.write(evidence)
        print(f"Saved {path.relative_to(ROOT)}")
    return 0 if metadata["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
