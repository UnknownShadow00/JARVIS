"""Real SQLite authority contracts using private disposable fixture directories."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
import os
import sqlite3
import threading
import uuid

import pytest

from app.agent.authority import Actor, Authority, AuthorityError
from app.agent.simulation import Simulator

A = Actor("test")
def rid(): return str(uuid.uuid4())


@pytest.fixture
def a(tmp_path):
    a = Authority(tmp_path / "store.sqlite", allow_simulation=True)
    yield a
    a.close()


def job(a):
    nominal = "2035-01-01T12:00:00+00:00"
    row = a.add_schedule(A, rid(), "name", "* * * * *", "inspect only", nominal)["result"]
    epoch = a.scheduler_control(A, rid(), True)["result"]["epoch"]
    return row, epoch, nominal, "2035-01-01T12:01:00+00:00"


def test_durable_replay_conflict_scope_detached_reads(a, tmp_path):
    key = rid()
    first = a.submit(A, key, "hello")
    first["result"]["goal"] = "changed returned data"
    assert a.submit(A, key, "hello")["result"]["goal"] == "hello"
    assert a.submit(A, key, "hello")["replayed"]
    for actor, goal in [(A, "different"), (Actor("other"), "hello")]:
        with pytest.raises(AuthorityError, match="request_conflict"):
            a.submit(actor, key, goal)
    assert a.receipt(Actor("other"), key) is None
    a.close()
    b = Authority(tmp_path / "store.sqlite")
    try:
        assert b.submit(A, key, "hello")["replayed"]
        assert len(b.list_tasks(A)) == 1
        assert not b.readiness()["execution_enabled"]
    finally: b.close()


@pytest.mark.parametrize("key", [True, 123, "abc", "00000000-0000-0000-0000-000000000000", str(uuid.uuid4()).upper()])
def test_invalid_ids(a, key):
    with pytest.raises(AuthorityError, match="invalid_identifier"):
        a.submit(A, key, "goal")
    assert a.list_tasks(A) == []


def test_concurrent_same_id_one_transaction(a):
    key = rid()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: a.submit(A, key, "same"), range(8)))
    assert sum(not r["replayed"] for r in results) == 1
    assert len(a.list_tasks(A)) == 1


def test_occurrence_atomic_replay_and_changed_next_conflict(a):
    row, epoch, nominal, following = job(a)
    first = a.admit_occurrence(A, row["job_id"], 1, nominal, epoch, following)
    second = a.admit_occurrence(A, row["job_id"], 1, nominal, epoch + 9, following)
    assert second["replayed"] and first["result"] == second["result"]
    assert a.list_schedules(A)[0]["last_run"] == nominal
    assert len(a.list_tasks(A)) == 1
    with pytest.raises(AuthorityError, match="request_conflict"):
        a.admit_occurrence(A, row["job_id"], 1, nominal, epoch, "2035-01-01T12:02:00+00:00")


@pytest.mark.parametrize("action", ["stop", "remove", "disable"])
def test_cancellation_before_and_after_admission(a, action):
    row, epoch, nominal, following = job(a)
    task = a.admit_occurrence(A, row["job_id"], 1, nominal, epoch, following)["result"]
    sim = Simulator(a)
    claim = sim.claim(A, rid(), task["task_id"])["result"]
    if action == "stop": a.scheduler_control(A, rid(), False)
    else: a.set_schedule(A, rid(), row["job_id"], removed=action == "remove")
    current = a.list_tasks(A)[0]
    assert current["status"] == "simulating" and current["cancel_requested"]
    result = sim.apply(A, rid(), **claim)["result"]
    assert not result["effect_applied"]
    assert a.list_tasks(A)[0]["status"] == "cancelled"
    with pytest.raises(AuthorityError, match="stale_occurrence"):
        a.admit_occurrence(A, row["job_id"], 1, following, epoch, "2035-01-01T12:02:00+00:00")


def test_effect_then_cancel_never_false_cancelled(a):
    task = a.submit(A, rid(), "goal")["result"]
    sim = Simulator(a)
    claim = sim.claim(A, rid(), task["task_id"])["result"]
    sim.apply(A, rid(), **claim)
    a.cancel(A, rid(), task["task_id"])
    with pytest.raises(AuthorityError, match="effect_already_applied"):
        sim.apply(A, rid(), **claim)
    result = sim.acknowledge(A, rid(), **claim)["result"]
    assert result == {"status": "simulated_completed", "cancel_requested": True}


def test_legacy_unknown_is_not_synthetic_reconciliation(a):
    receipt = a.import_legacy_snapshot(A, rid(), tasks=[{"task_id": "old", "goal": "goal", "status": "completed"}], schedules=[], evidence={})
    task_id = receipt["result"]["task_ids"]["old"]
    with pytest.raises(AuthorityError, match="not_unknown"):
        Simulator(a).reconcile(A, rid(), task_id)
    assert a.list_tasks(A)[0]["status"] == "unknown"


def test_simulation_disabled_by_default(tmp_path):
    a = Authority(tmp_path / "db")
    try:
        with pytest.raises(AuthorityError, match="simulation_disabled"): Simulator(a)
    finally: a.close()


def test_close_waits_for_active_transaction(a):
    inside, release, closed = threading.Event(), threading.Event(), threading.Event()
    def fault(stage):
        if stage == "after_effect_sql":
            inside.set()
            assert release.wait(2)
    a._fault = fault
    errors = []
    def submit():
        try: a.submit(A, rid(), "goal")
        except BaseException as e: errors.append(e)
    worker = threading.Thread(target=submit)
    closer = threading.Thread(target=lambda: (a.close(), closed.set()))
    worker.start()
    assert inside.wait(2)
    closer.start()
    assert not closed.wait(0.05)
    release.set()
    worker.join(2); closer.join(2)
    assert closed.is_set() and not errors


@pytest.mark.parametrize("state", ["absent", "empty", "unsupported"])
def test_legacy_guard_and_unsupported_bytes_preserved(tmp_path, state):
    path = tmp_path / "db"
    legacy = tmp_path / "legacy.json"
    legacy.write_text('[{"task_id":"old","goal":"old"}]')
    if state == "empty": path.touch(mode=0o600)
    if state == "unsupported":
        connection = sqlite3.connect(path)
        connection.execute("CREATE TABLE unrelated(x)")
        connection.close()
        path.chmod(0o600)
    before = path.read_bytes() if path.exists() else None
    with pytest.raises(AuthorityError, match="legacy_migration_required|unsupported_schema"):
        Authority(path, legacy_paths=[legacy])
    assert (path.read_bytes() if path.exists() else None) == before


def test_store_replaced_and_fork_fence(a):
    a.path.rename(a.path.with_suffix(".preserved"))
    a.path.touch(mode=0o600)
    with pytest.raises(AuthorityError, match="store_replaced"):
        a.submit(A, rid(), "blocked")


def test_sql_metacharacters_are_data(a):
    goal = "';DROP TABLE receipts;-- $(touch /work/NEVER) <script>"
    assert a.submit(A, rid(), goal)["result"]["goal"] == goal
    assert not os.path.exists("/work/NEVER")


def test_pending_cancel_keeps_evidence(a):
    row = a.submit(A, rid(), "goal")["result"]
    a.cancel(A, rid(), row["task_id"])
    assert a.list_tasks(A)[0]["outbox_state"] == "cancelled"
    assert a._conn.execute("SELECT COUNT(*) FROM events WHERE request_id<>?", (a.owner_id,)).fetchone()[0] == 2


@pytest.mark.parametrize("first", ["stop", "admit"])
def test_stop_admission_thread_race_is_serialized(a, first):
    row, epoch, nominal, following = job(a)
    entered, release = threading.Event(), threading.Event()
    results = []
    active = [True]
    def hook(stage):
        if stage == "after_effect_sql" and active[0]:
            active[0] = False
            entered.set()
            assert release.wait(2)
    a._fault = hook
    def operation(which):
        try:
            if which == "stop": results.append((which, a.scheduler_control(A, rid(), False)))
            else: results.append((which, a.admit_occurrence(A, row['job_id'], 1, nominal, epoch, following)))
        except AuthorityError as e:results.append((which, e.code))
    one = threading.Thread(target=operation, args=(first,))
    two = threading.Thread(target=operation, args=("admit" if first == "stop" else "stop",))
    one.start(); assert entered.wait(2)
    two.start(); release.set()
    one.join(2);two.join(2)
    assert not one.is_alive() and not two.is_alive()
    tasks = a.list_tasks(A)
    if first == "stop":
        assert tasks == [] and ("admit", "stale_occurrence") in results
    else:
        assert len(tasks) == 1 and tasks[0]['status'] == 'cancelled'
