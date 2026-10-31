#!/usr/bin/env python3
"""Capture bounded public hashes/retained receipts/git metadata; never run payloads/tests."""
from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
PINS = {
    "proxmox-automation-phase2": "3f1f49e116a6e4c7850488ff9cf8f00b38444be0a4be5e01a9bedfd5f8bac8b2",
    "proxmox-automation-phase3": "26821c235814dce44ed853776fd53a3ca57d4fd0b8b66a43042e9c2fc6dd33b6",
    "proxmox-automation-phase3-review-r1": "5d95dba590fdc2e13caf0bc7b70d1eadc81a2212b02aed9e99cf5a72c81f38a3",
    "jarvis-v2-taskqueue-reliability-r1": "76a5297d931db90570249a5c30a6ebb5d28ace8a0875ce3b3d997d0c29bba4f7",
    "jarvis-v2-taskqueue-reliability-r2": "d78cc922f55568e2f1867979c14e3cc81d8b6986e6352422c781e96a631abbad",
    "jarvis-v2-taskqueue-callers-r3": "ef995b6d456fee0651821fb6a754fdeeac34a030af6acbce5cd7d02ba0feca39",
    "jarvis-v2-scheduler-reliability-r4": "3a281fa83aaccb5a986bb39986b9fdb24b6ffa523648780c16359c60f4ddc4a9",
    "jarvis-offline-provenance-r1": "85637a307d48615233471efb342c0e6faad55ef8efa146c5ed6850eb44f11da4",
}
RECEIPTS = {
    "broker_r1": "tasks/proxmox-automation-phase3-review-r1/evidence/offline-tests.json",
    "queue_r1": "tasks/jarvis-v2-taskqueue-reliability-r1/evidence-20261030T213725199478Z.txt",
    "queue_r2": "tasks/jarvis-v2-taskqueue-reliability-r2/evidence-20261030T222357610970Z.txt",
    "queue_r3": "tasks/jarvis-v2-taskqueue-callers-r3/evidence-20261030T223312529709Z.txt",
    "scheduler_r4": "tasks/jarvis-v2-scheduler-reliability-r4/evidence-20261030T224808335328Z.txt",
}


def read(relative: str) -> bytes:
    name = PurePosixPath(relative)
    if name.is_absolute() or not name.parts or any(part in {"", ".", ".."} for part in name.parts):
        raise ValueError("Unsafe public relative path")
    path = ROOT
    for part in name.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError("Symbolic link not accepted")
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > 16 * 1024 * 1024:
            raise ValueError("Public artifact type/size limit exceeded")
        with os.fdopen(descriptor, "rb", closefd=False) as handle:
            data = handle.read(16 * 1024 * 1024 + 1)
        after = os.fstat(descriptor)
        signature = lambda value: (value.st_dev, value.st_ino, value.st_size, value.st_mtime_ns, value.st_ctime_ns)
        if len(data) > 16 * 1024 * 1024 or signature(before) != signature(after):
            raise ValueError("Artifact changed during bounded read")
        return data
    finally:
        os.close(descriptor)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments], cwd=ROOT)


def main():
    sys.dont_write_bytecode = True
    started = datetime.now(UTC).isoformat()
    preservation = {}
    for name, expected in PINS.items():
        base = f"tasks/{name}"
        manifest = read(f"{base}/SHA256SUMS")
        if digest(manifest) != expected:
            raise ValueError(f"Manifest identity mismatch: {name}")
        seen = set()
        for line in manifest.decode().splitlines():
            expected_file, relative = line.split("  ", 1)
            if relative in seen or digest(read(f"{base}/{relative}")) != expected_file:
                raise ValueError(f"Member identity mismatch: {name}/{relative}")
            seen.add(relative)
        preservation[name] = {"manifest_sha256": expected, "members_verified": len(seen), "match": True}
    r4 = json.loads(read("tasks/jarvis-v2-scheduler-reliability-r4/SOURCE-IDENTITY.json"))
    source_names = list(r4["current_sha256"])
    source_names.append("tests/test_task_queue_store_safety.py")
    source_hashes = {name: digest(read(name)) for name in source_names}
    for name, expected in r4["current_sha256"].items():
        if source_hashes[name] != expected:
            raise ValueError(f"R4 source drift: {name}")
    expected_safety = "b5ae3964a75a8b20f60a64e20f654a888c9353cc0fabff6c80be30414c60e52d"
    if source_hashes["tests/test_task_queue_store_safety.py"] != expected_safety:
        raise ValueError("R2 safety test source drift")
    receipts = {}
    for name, relative in RECEIPTS.items():
        raw = read(relative)
        metadata = json.JSONDecoder().raw_decode(raw.decode())[0]
        if not metadata.get("success", metadata.get("successful", False)):
            raise ValueError(f"Retained positive receipt is not passing: {name}")
        receipts[name] = {
            "path": relative, "sha256": digest(raw),
            "methods": metadata.get("tests_run", metadata.get("methods")),
            "subtests": metadata.get("subtests"),
            "existing_subtests_if_separately_reported": metadata.get("existing_regressions_run_as_subtests"),
            "observed_at": metadata.get("timestamp_utc", metadata.get("at_utc")),
            "executed_during_consolidation": False,
        }
    release = json.loads(read("tasks/proxmox-automation-phase3-review-r1/RELEASE.json"))
    provenance = json.loads(read("tasks/jarvis-offline-provenance-r1/evidence-20261030T222449706209Z.json"))
    comparison = {}
    for row in provenance["workspace_comparison"]:
        name = row["relative_path"]
        if name in {"app/agent/task_queue.py", "app/agent/scheduler.py", "app/server.py"}:
            comparison[name] = {
                "gate6k_sha256": row["gate6k_sha256"],
                "provenance_observation_sha256": row["sha256"],
                "current_sha256": source_hashes[name],
                "matches_gate6k": source_hashes[name] == row["gate6k_sha256"],
            }
    app_paths = ["app/agent/task_queue.py", "app/agent/scheduler.py", "app/server.py"]
    patch = git("diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD", "--", *app_paths)
    patch_name = f"source-diff-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}.patch"
    with (PACKET / patch_name).open("xb") as handle:
        handle.write(patch)
    metadata = {
        "started_at": started, "finished_at": datetime.now(UTC).isoformat(),
        "scope": "public artifact hashes, retained receipts and bounded git/source metadata only; no tests or payload imports",
        "repository": str(ROOT), "profile": "workspace-write",
        "head": git("rev-parse", "HEAD").decode().strip(),
        "branch": git("branch", "--show-current").decode().strip(),
        "working_tree_status_porcelain": git("status", "--porcelain=v1").decode(),
        "tracked_diff_sha256": digest(git("diff", "--no-ext-diff", "--no-textconv", "--binary", "HEAD", "--")),
        "staged_diff_sha256": digest(git("diff", "--cached", "--no-ext-diff", "--no-textconv", "--binary", "--")),
        "source_diff": {"file": patch_name, "sha256": digest(patch), "paths": app_paths},
        "head_public_source_sha256": {name: digest(git("show", f"HEAD:{name}")) for name in app_paths},
        "current_source_sha256": source_hashes,
        "preserved_packets": preservation, "retained_receipts": receipts,
        "broker": {key: release[key] for key in ["source_manifest_sha256", "source_file_count", "archive", "archive_sha256", "status"]},
        "broker_archive_members_listed": len(release["archive_member_sha256"]),
        "gate6k_current_three_file_comparison": comparison,
        "older_full_scan": {"started_at": provenance["started_at"], "finished_at": provenance["finished_at"], "counts": provenance["workspace_comparison_counts"], "repeated_now": False},
        "dependencies_discovered_without_import": {name: importlib.util.find_spec(name) is not None for name in ["fastapi", "pydantic", "pytest", "apscheduler"]},
        "python": sys.version,
        "new_tests_run": 0, "new_live_or_privileged_operations": 0,
        "authorization_status": "No action denied; privileged setup/bootstrap/activation remain pending and unattempted.",
        "dirty_snapshot_limit": "Temporal checkout observation; metadata pointer/log appends can follow. Code source hashes must remain stable. No atomic whole-tree snapshot claimed.",
    }
    target = PACKET / f"verification-{datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')}.json"
    with target.open("x", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"evidence": str(target.relative_to(ROOT)), "preserved_packets": len(preservation), "verified_members": sum(row["members_verified"] for row in preservation.values()), "new_tests_run": 0, "current_source_sha256": {name: source_hashes[name] for name in app_paths}}, indent=2))


if __name__ == "__main__":
    main()
