#!/usr/bin/env python3
"""Demonstrate two defects in frozen predecessor source, in disposable fixtures only."""
from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent


def main():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("offline_scheduler_tests", ROOT / "tests/test_scheduler_reliability.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.SOURCE_OVERRIDES["scheduler.py"] = PACKET / "scheduler.before.py"
    fixture = module.SchedulerReliabilityTests()
    fixture.setUp()
    try:
        job = fixture.seed()
        before = fixture.store.read_bytes()
        real_write = fixture.module.Path.write_text

        def interrupted(path, content, **kwargs):
            if path == fixture.store:
                with path.open("w", encoding="utf-8") as handle:
                    handle.write("[")
                raise OSError("synthetic interruption after final-path truncation")
            return real_write(path, content, **kwargs)

        with mock.patch.object(fixture.module.Path, "write_text", interrupted):
            result = fixture.owner.add_job("reported success", "* * * * *", "goal")
        damaged = fixture.store.read_bytes()
        events = [event for event, _ in fixture.audit.events]
        backend = fixture.start_recording()
        retained = backend.callbacks[job.job_id]
        fixture.owner.remove_job(job.job_id)
        fixture.fire(retained)
        report = {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "scope": "frozen R3 definitions, disposable files/inert backend/in-memory audit; no live framework",
            "scheduler_before_sha256": hashlib.sha256((PACKET / "scheduler.before.py").read_bytes()).hexdigest(),
            "interrupted_final_write": {
                "before_sha256": hashlib.sha256(before).hexdigest(),
                "after_bytes_hex": damaged.hex(), "add_returned_job": result.job_id,
                "success_event_despite_save_error": "scheduler_save_error" in events and "job_added" in events,
            },
            "removed_callback": {
                "removed_job_id": job.job_id,
                "tasks_enqueued_after_successful_remove": len(fixture.run_async(fixture.queue.list_tasks())),
            },
        }
        assert damaged == b"[" and report["interrupted_final_write"]["success_event_despite_save_error"]
        assert report["removed_callback"]["tasks_enqueued_after_successful_remove"] == 1
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        target = PACKET / f"predecessor-defects-{stamp}.json"
        with target.open("x", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2)
            handle.write("\n")
        print(json.dumps(report, indent=2))
    finally:
        fixture.doCleanups()


if __name__ == "__main__":
    main()
