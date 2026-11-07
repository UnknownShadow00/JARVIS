"""Explicit, bounded legacy JSON import; never discover or rewrite runtime stores.

Both paths must be supplied by the caller. Validate all captured source bytes
before invoking the authority's one atomic empty-target import transaction. Source
files are retained untouched; the durable receipt carries their identities and
core-owned deterministic legacy-ID mappings. Operators must quiesce old writers;
this reader does not create a cross-file snapshot or migrate on application start.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import stat
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.agent.authority import Actor, Authority

MAX_SOURCE_BYTES = 1024 * 1024
MAX_RECORDS = 1000  # Combined task and schedule records in this explicit import.
MIGRATION_VERSION = 1


class MigrationError(ValueError):
    """A source was rejected before authority import; no source values are exposed."""

    def __init__(self, code: str, source: str) -> None:
        super().__init__(f"{source}:{code}")
        self.code = code
        self.source = source


def _identity(metadata: os.stat_result) -> tuple[int, ...]:
    return (metadata.st_dev, metadata.st_ino, metadata.st_mode, metadata.st_size,
            metadata.st_mtime_ns, metadata.st_ctime_ns)


def _read_source(value: str | Path, source: str) -> bytes:
    try:
        path = Path(value)
    except (TypeError, ValueError):
        raise MigrationError("source_path", source) from None
    if ".." in path.parts:
        raise MigrationError("source_path", source)
    path = path.absolute()  # Explicit relative paths are anchored; never resolve links.
    descriptor = -1
    try:
        descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
        parts = path.parts[1:]
        if not parts:
            raise MigrationError("source_not_regular", source)
        for index, part in enumerate(parts):
            last = index == len(parts) - 1
            flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK
            if not last:
                flags |= os.O_DIRECTORY
            else:
                entry = os.stat(part, dir_fd=descriptor, follow_symlinks=False)
                if not stat.S_ISREG(entry.st_mode):
                    raise MigrationError("source_not_regular", source)
            opened = os.open(part, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = opened
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise MigrationError("source_not_regular", source)
        if before.st_size > MAX_SOURCE_BYTES:
            raise MigrationError("source_too_large", source)
        captured = bytearray()
        while len(captured) <= MAX_SOURCE_BYTES:
            chunk = os.read(descriptor, min(65536, MAX_SOURCE_BYTES + 1 - len(captured)))
            if not chunk:
                break
            captured.extend(chunk)
        if len(captured) > MAX_SOURCE_BYTES:
            raise MigrationError("source_too_large", source)
        after = os.fstat(descriptor)
        if _identity(before) != _identity(after) or len(captured) != before.st_size:
            raise MigrationError("source_changed", source)
        return bytes(captured)
    except MigrationError:
        raise
    except (OSError, ValueError):
        raise MigrationError("source_unavailable", source) from None
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _records(raw: bytes, source: str) -> list[dict[str, Any]]:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise MigrationError("duplicate_json_key", source)
            value[key] = item
        return value

    def reject_constant(value: str) -> None:
        raise MigrationError("nonfinite_json", source)

    def finite_float(text: str) -> float:
        value = float(text)
        if not math.isfinite(value):
            raise MigrationError("nonfinite_json", source)
        return value

    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise MigrationError("source_encoding", source) from None
    try:
        value = json.loads(text, object_pairs_hook=unique, parse_constant=reject_constant,
                           parse_float=finite_float)
    except MigrationError:
        raise
    except (ValueError, RecursionError):
        raise MigrationError("invalid_json", source) from None
    if type(value) is not list:
        raise MigrationError("root_not_list", source)
    if len(value) > MAX_RECORDS:
        raise MigrationError("record_limit", source)
    if source == "tasks":
        required = {"task_id", "goal"}
        optional = {"status", "created_at", "result", "error"}
        strings = required | {"status", "created_at"}
        identifier = "task_id"
    else:
        required = {"job_id", "name", "cron_expr", "goal"}
        optional = {"enabled", "last_run"}
        strings = required
        identifier = "job_id"
    identifiers: set[str] = set()
    for item in value:
        if (type(item) is not dict or not required <= item.keys()
                or item.keys() - required - optional):
            raise MigrationError("record_schema", source)
        if any(type(item[key]) is not str for key in strings if key in item):
            raise MigrationError("record_type", source)
        if any(not item[key].strip() for key in required):
            raise MigrationError("record_value", source)
        if source == "tasks":
            if item.get("result") is not None and type(item["result"]) is not dict:
                raise MigrationError("record_type", source)
            if item.get("error") is not None and type(item["error"]) is not str:
                raise MigrationError("record_type", source)
        else:
            if "enabled" in item and type(item["enabled"]) is not bool:
                raise MigrationError("record_type", source)
            if item.get("last_run") is not None and type(item["last_run"]) is not str:
                raise MigrationError("record_type", source)
        if item[identifier] in identifiers:
            raise MigrationError("duplicate_legacy_id", source)
        identifiers.add(item[identifier])  # Preserve exact IDs, including surrounding whitespace.
    return value


def migrate_legacy(
    authority: Authority,
    actor: Actor,
    request_id: str,
    *,
    tasks_path: str | Path,
    jobs_path: str | Path,
) -> dict[str, Any]:
    """Import explicit source files atomically; return the core receipt unchanged.

    Parse/schema errors raise MigrationError before any import call. AuthorityError
    conflicts and storage failures propagate unchanged from the authority. No
    legacy path is inferred, source overwritten, or real dispatch enabled here.
    """
    tasks_raw = _read_source(tasks_path, "tasks")
    tasks = _records(tasks_raw, "tasks")
    jobs_raw = _read_source(jobs_path, "jobs")
    schedules = _records(jobs_raw, "jobs")
    if len(tasks) + len(schedules) > MAX_RECORDS:
        raise MigrationError("record_limit", "combined")
    evidence = {
        "migration_version": MIGRATION_VERSION,
        "tasks_source_sha256": hashlib.sha256(tasks_raw).hexdigest(),
        "jobs_source_sha256": hashlib.sha256(jobs_raw).hexdigest(),
        "tasks_source_bytes": len(tasks_raw),
        "jobs_source_bytes": len(jobs_raw),
        "tasks_record_count": len(tasks),
        "jobs_record_count": len(schedules),
    }
    return authority.import_legacy_snapshot(
        actor, request_id, tasks=tasks, schedules=schedules, evidence=evidence,
    )
