"""Synthetic migration contracts. Execute only in the parent-approved test cage.

All databases/source fixtures live under pytest's tmp_path. No default legacy
location, real application factory, backend, provider or runtime store is opened.
This file is drafted statically; importing/running it awaits parent clearance.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from unittest import mock
from uuid import UUID, uuid4

import pytest

from app.agent.authority import Actor, Authority, AuthorityError
from synthetic_authority import fixture_authority as Authority
from app.agent import migration
from app.agent.migration import MAX_RECORDS, MAX_SOURCE_BYTES, MigrationError, migrate_legacy


@pytest.fixture
def actor():
    return Actor("synthetic-migration")


@pytest.fixture
def authority(tmp_path):
    instance = Authority(tmp_path / "authority.sqlite")
    try:
        yield instance
    finally:
        instance.close()


def sources(tmp_path, *, tasks=None, jobs=None, tasks_raw=None, jobs_raw=None):
    directory = tmp_path / "legacy"
    directory.mkdir(exist_ok=True)
    tasks_path, jobs_path = directory / "tasks.json", directory / "jobs.json"
    tasks_path.write_bytes(json.dumps([] if tasks is None else tasks).encode() if tasks_raw is None else tasks_raw)
    jobs_path.write_bytes(json.dumps([] if jobs is None else jobs).encode() if jobs_raw is None else jobs_raw)
    return tasks_path, jobs_path


def import_sources(authority, actor, paths, request_id=None):
    return migrate_legacy(authority, actor, str(uuid4()) if request_id is None else request_id,
                          tasks_path=paths[0], jobs_path=paths[1])


def assert_sources_unchanged(paths, originals):
    assert tuple(path.read_bytes() for path in paths) == originals


def assert_rejected_before_import(authority, actor, paths, expected_code):
    request_id = str(uuid4())
    originals = tuple(path.read_bytes() for path in paths)
    # Retain a real, empty authority while proving invalid source never reaches
    # the importer, even when a valid record precedes the invalid one.
    with mock.patch.object(Authority, "import_legacy_snapshot", side_effect=AssertionError("must not import")):
        with pytest.raises(MigrationError) as caught:
            import_sources(authority, actor, paths, request_id)
    assert caught.value.code == expected_code
    assert authority.list_tasks(actor) == []
    assert authority.list_schedules(actor) == []
    assert authority.receipt(actor, request_id) is None
    assert_sources_unchanged(paths, originals)


def test_import_preserves_source_hashes_exact_ids_and_returns_core_receipt(authority, actor, tmp_path, monkeypatch):
    tasks_raw = b' [ { "task_id" : " legacy-task ", "goal" : " preserve goal ", "status" : "pending" } ]\n'
    jobs_raw = b'[ {"job_id":" legacy-job ","name":"name","cron_expr":"0 8 * * *","goal":"goal","enabled":true,"last_run":"legacy-time"} ]\n'
    paths = sources(tmp_path, tasks_raw=tasks_raw, jobs_raw=jobs_raw)
    original = Authority.import_legacy_snapshot
    actual_receipts = []

    def capture(self, *args, **kwargs):
        receipt = original(self, *args, **kwargs)
        actual_receipts.append(receipt)
        return receipt

    monkeypatch.setattr(Authority, "import_legacy_snapshot", capture)
    request_id = str(uuid4())
    receipt = import_sources(authority, actor, paths, request_id)
    assert receipt is actual_receipts[0]
    assert receipt["request_id"] == request_id
    assert receipt["scope"] == actor.scope
    assert receipt["state"] == "committed"
    result = receipt["result"]
    assert set(result["task_ids"]) == {" legacy-task "}
    assert set(result["schedule_ids"]) == {" legacy-job "}
    assert result["tasks_imported"] == result["schedules_imported"] == 1
    assert UUID(result["task_ids"][" legacy-task "]).version == 5
    assert UUID(result["schedule_ids"][" legacy-job "]).version == 5
    assert result["evidence"] == {
        "migration_version": 1,
        "tasks_source_sha256": hashlib.sha256(tasks_raw).hexdigest(),
        "jobs_source_sha256": hashlib.sha256(jobs_raw).hexdigest(),
        "tasks_source_bytes": len(tasks_raw), "jobs_source_bytes": len(jobs_raw),
        "tasks_record_count": 1, "jobs_record_count": 1,
    }
    assert_sources_unchanged(paths, (tasks_raw, jobs_raw))


def test_same_request_replays_before_empty_target_check(authority, actor, tmp_path):
    paths = sources(tmp_path, tasks=[{"task_id": "one", "goal": "pending"}],
                    jobs=[{"job_id": "job", "name": "job", "cron_expr": "0 * * * *", "goal": "goal"}])
    originals = tuple(path.read_bytes() for path in paths)
    request_id = str(uuid4())
    first = import_sources(authority, actor, paths, request_id)
    replay = import_sources(authority, actor, paths, request_id)
    assert replay["replayed"] is True
    assert replay["result"] == first["result"]
    assert len(authority.list_tasks(actor)) == 1
    assert len(authority.list_schedules(actor)) == 1
    assert_sources_unchanged(paths, originals)


def test_uuid5_mappings_are_deterministic_across_fresh_authorities(actor, tmp_path):
    paths = sources(tmp_path, tasks=[{"task_id": "shared-old-id", "goal": "goal"}],
                    jobs=[{"job_id": "shared-old-id", "name": "job", "cron_expr": "0 * * * *", "goal": "goal"}])
    results = []
    for name in ("first.sqlite", "second.sqlite"):
        instance = Authority(tmp_path / name)
        try:
            results.append(import_sources(instance, actor, paths)["result"])
        finally:
            instance.close()
    assert results[0]["task_ids"] == results[1]["task_ids"]
    assert results[0]["schedule_ids"] == results[1]["schedule_ids"]
    assert results[0]["task_ids"]["shared-old-id"] != results[0]["schedule_ids"]["shared-old-id"]


def test_pending_is_held_nonpending_is_unknown_and_all_schedules_are_disabled(authority, actor, tmp_path):
    statuses = ("pending", "completed", "in_progress", "done", "failed", "cancelled")
    tasks = [
        {"task_id": status, "goal": f"legacy {status}", "status": status,
         "result": {"historical_only": True}, "error": None, "created_at": "legacy-created"}
        for status in statuses
    ]
    tasks.append({"task_id": "default-pending", "goal": "no explicit old status"})
    jobs = [
        {"job_id": "was-enabled", "name": "enabled old job", "cron_expr": "0 8 * * *",
         "goal": "never dispatch", "enabled": True, "last_run": "legacy-run-time"},
        {"job_id": "was-disabled", "name": "disabled old job", "cron_expr": "0 9 * * *",
         "goal": "never dispatch", "enabled": False, "last_run": None},
    ]
    paths = sources(tmp_path, tasks=tasks, jobs=jobs)
    originals = tuple(path.read_bytes() for path in paths)
    result = import_sources(authority, actor, paths)["result"]
    rows = {row["task_id"]: row for row in authority.list_tasks(actor)}
    assert len(rows) == len(tasks)
    for legacy_id, new_id in result["task_ids"].items():
        expected = ("pending", "held") if legacy_id in {"pending", "default-pending"} else ("unknown", "unknown")
        assert (rows[new_id]["status"], rows[new_id]["outbox_state"]) == expected
    schedules = {row["job_id"]: row for row in authority.list_schedules(actor)}
    assert len(schedules) == 2
    for row in schedules.values():
        assert row["enabled"] is False
        assert row["last_run"] is None
    imported_enabled = schedules[result["schedule_ids"]["was-enabled"]]
    assert imported_enabled["metadata"]["legacy_last_run"] == "legacy-run-time"
    assert_sources_unchanged(paths, originals)


def test_new_request_cannot_import_into_existing_target(authority, actor, tmp_path):
    authority.submit(actor, str(uuid4()), "existing synthetic task")
    before_tasks = authority.list_tasks(actor)
    before_schedules = authority.list_schedules(actor)
    paths = sources(tmp_path, tasks=[{"task_id": "legacy", "goal": "goal"}])
    originals = tuple(path.read_bytes() for path in paths)
    request_id = str(uuid4())
    with pytest.raises(AuthorityError) as caught:
        import_sources(authority, actor, paths, request_id)
    assert caught.value.code == "nonempty_migration_target"
    assert authority.list_tasks(actor) == before_tasks
    assert authority.list_schedules(actor) == before_schedules
    assert authority.receipt(actor, request_id) is None
    assert_sources_unchanged(paths, originals)


def test_replay_binds_source_bytes_even_if_parsed_records_are_unchanged(authority, actor, tmp_path):
    paths = sources(tmp_path, tasks=[{"task_id": "legacy", "goal": "goal"}])
    request_id = str(uuid4())
    first = import_sources(authority, actor, paths, request_id)
    paths[0].write_bytes(b" " + paths[0].read_bytes())
    originals = tuple(path.read_bytes() for path in paths)
    with pytest.raises(AuthorityError) as caught:
        import_sources(authority, actor, paths, request_id)
    assert caught.value.code == "request_conflict"
    assert authority.receipt(actor, request_id)["result"] == first["result"]
    assert len(authority.list_tasks(actor)) == 1
    assert_sources_unchanged(paths, originals)


@pytest.mark.parametrize("kind", ["tasks", "jobs"])
def test_duplicate_legacy_ids_reject_whole_mixed_import(authority, actor, tmp_path, kind):
    task = {"task_id": "duplicate", "goal": "goal"}
    job = {"job_id": "duplicate", "name": "name", "cron_expr": "0 * * * *", "goal": "goal"}
    paths = sources(tmp_path, tasks=[task, dict(task)] if kind == "tasks" else [task],
                    jobs=[job, dict(job)] if kind == "jobs" else [job])
    assert_rejected_before_import(authority, actor, paths, "duplicate_legacy_id")


@pytest.mark.parametrize("kind,invalid,code", [
    ("tasks", None, "record_schema"),
    ("tasks", {"task_id": "bad", "goal": 3}, "record_type"),
    ("tasks", {"task_id": "bad", "goal": "goal", "unexpected": True}, "record_schema"),
    ("tasks", {"task_id": True, "goal": "goal"}, "record_type"),
    ("tasks", {"task_id": "bad", "goal": "goal", "status": False}, "record_type"),
    ("tasks", {"task_id": "bad", "goal": "goal", "created_at": 1}, "record_type"),
    ("tasks", {"task_id": "bad", "goal": "goal", "result": []}, "record_type"),
    ("tasks", {"task_id": "bad", "goal": "goal", "error": False}, "record_type"),
    ("tasks", {"task_id": " ", "goal": "goal"}, "record_value"),
    ("jobs", {"job_id": "bad", "name": "name", "cron_expr": "* * * * *", "goal": "goal", "enabled": 1}, "record_type"),
    ("jobs", {"job_id": "bad", "name": "name", "cron_expr": "* * * * *", "goal": "goal", "last_run": False}, "record_type"),
    ("jobs", {"job_id": "bad", "name": "name", "cron_expr": "* * * * *", "goal": "goal", "unknown": None}, "record_schema"),
    ("jobs", {"job_id": "bad", "name": "name", "goal": "goal"}, "record_schema"),
    ("jobs", {"job_id": "bad", "name": "name", "cron_expr": " ", "goal": "goal"}, "record_value"),
])
def test_invalid_mixed_record_never_imports_valid_prefix(authority, actor, tmp_path, kind, invalid, code):
    tasks = [{"task_id": "valid", "goal": "valid task"}]
    jobs = [{"job_id": "valid", "name": "name", "cron_expr": "* * * * *", "goal": "goal"}]
    (tasks if kind == "tasks" else jobs).append(invalid)
    paths = sources(tmp_path, tasks=tasks, jobs=jobs)
    assert_rejected_before_import(authority, actor, paths, code)


@pytest.mark.parametrize("raw,code", [
    (b'{"not":"a list"}', "root_not_list"),
    (b'false', "root_not_list"),
    (b'{malformed', "invalid_json"),
    (b'\xff[]', "source_encoding"),
    (b'[{"task_id":"a","task_id":"b","goal":"goal"}]', "duplicate_json_key"),
    (b'[{"task_id":"a","goal":"goal","result":{"nested":1,"nested":2}}]', "duplicate_json_key"),
    (b'[{"task_id":"a","goal":"goal","result":{"number":NaN}}]', "nonfinite_json"),
    (b'[{"task_id":"a","goal":"goal","result":{"number":Infinity}}]', "nonfinite_json"),
    (b'[{"task_id":"a","goal":"goal","result":{"number":1e999}}]', "nonfinite_json"),
])
def test_strict_json_rejections_precede_import(authority, actor, tmp_path, raw, code):
    paths = sources(tmp_path, tasks_raw=raw)
    assert_rejected_before_import(authority, actor, paths, code)


def test_explicit_source_byte_cap_rejects_without_import(authority, actor, tmp_path):
    paths = sources(tmp_path, tasks_raw=b" " * (MAX_SOURCE_BYTES + 1))
    assert_rejected_before_import(authority, actor, paths, "source_too_large")


def test_exact_byte_cap_can_import_a_single_record(authority, actor, tmp_path):
    payload = b'[{"task_id":"bounded","goal":"goal"}]'
    raw = payload + b" " * (MAX_SOURCE_BYTES - len(payload))
    paths = sources(tmp_path, tasks_raw=raw)
    receipt = import_sources(authority, actor, paths)
    assert receipt["result"]["tasks_imported"] == 1
    assert receipt["result"]["evidence"]["tasks_source_bytes"] == MAX_SOURCE_BYTES
    assert paths[0].read_bytes() == raw


def test_per_file_record_limit_precedes_import(authority, actor, tmp_path):
    paths = sources(tmp_path, tasks=[{"task_id": str(index), "goal": "goal"} for index in range(MAX_RECORDS + 1)])
    assert_rejected_before_import(authority, actor, paths, "record_limit")


def test_combined_record_limit_precedes_import(authority, actor, tmp_path):
    paths = sources(tmp_path,
                    tasks=[{"task_id": str(index), "goal": "goal"} for index in range(600)],
                    jobs=[{"job_id": str(index), "name": "name", "cron_expr": "* * * * *", "goal": "goal"}
                          for index in range(401)])
    assert_rejected_before_import(authority, actor, paths, "record_limit")


def test_source_file_and_parent_symlinks_are_never_followed(authority, actor, tmp_path):
    paths = sources(tmp_path, tasks=[{"task_id": "one", "goal": "goal"}])
    original = tuple(path.read_bytes() for path in paths)
    link = tmp_path / "tasks-link.json"
    link.symlink_to(paths[0])
    parent_link = tmp_path / "legacy-link"
    parent_link.symlink_to(paths[0].parent, target_is_directory=True)
    with mock.patch.object(Authority, "import_legacy_snapshot", side_effect=AssertionError("must not import")):
        for source in (link, parent_link / "tasks.json", paths[0].parent):
            with pytest.raises(MigrationError):
                import_sources(authority, actor, (source, paths[1]))
    assert authority.list_tasks(actor) == []
    assert authority.list_schedules(actor) == []
    assert_sources_unchanged(paths, original)


@pytest.mark.parametrize("raw,code", [
    (b'{"jobs":[]}', "root_not_list"),
    (b'[{"job_id":"a","name":"n","cron_expr":"* * * * *","goal":"g","enabled":true,"enabled":false}]', "duplicate_json_key"),
    (b'[{"job_id":"a","name":"n","cron_expr":"* * * * *","goal":NaN}]', "nonfinite_json"),
])
def test_invalid_jobs_cannot_partially_import_valid_tasks(authority, actor, tmp_path, raw, code):
    paths = sources(tmp_path, tasks=[{"task_id": "valid", "goal": "goal"}], jobs_raw=raw)
    assert_rejected_before_import(authority, actor, paths, code)
