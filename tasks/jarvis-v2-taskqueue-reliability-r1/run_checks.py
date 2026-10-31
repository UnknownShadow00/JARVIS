#!/usr/bin/env python3
"""Run offline unittest checks and optionally save a new, exclusive evidence file."""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
FORBIDDEN_IMPORTS = {"app.config", "app.logs.audit", "app.agent.task_queue", "app.agent.scheduler"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-evidence", action="store_true")
    args = parser.parse_args()
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(
        "offline_task_queue_persistence", ROOT / "tests/test_task_queue_persistence.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=2).run(suite)
    report = output.getvalue()
    imported = sorted(FORBIDDEN_IMPORTS.intersection(sys.modules))
    sources = [
        "app/agent/task_queue.py", "app/agent/scheduler.py", "tests/test_agent_stubs.py",
        "tests/test_task_queue_persistence.py",
        "tasks/jarvis-v2-taskqueue-reliability-r1/run_checks.py",
    ]
    metadata = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "scope": "offline source-level isolated definitions; not full application integration",
        "python": sys.version,
        "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "tests_run": result.testsRun,
        "existing_regressions_run_as_subtests": 10,
        "success": result.wasSuccessful() and not imported,
        "forbidden_modules_imported": imported,
        "sha256": {source: hashlib.sha256((ROOT / source).read_bytes()).hexdigest() for source in sources},
    }
    evidence = json.dumps(metadata, indent=2) + "\n\n" + report
    print(evidence, end="")
    if args.save_evidence:
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        path = PACKET / f"evidence-{stamp}.txt"
        with path.open("x", encoding="utf-8") as handle:
            handle.write(evidence)
        print(f"Evidence saved: {path.relative_to(ROOT)}")
    return 0 if metadata["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
