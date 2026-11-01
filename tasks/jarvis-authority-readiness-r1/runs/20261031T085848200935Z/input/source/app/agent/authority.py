"""Single-writer transactional task authority. There is deliberately no executor.

Local code controlling this process/database is trusted. Actor is a server-owned
namespace, not a replacement for the application's authentication policy.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import stat
import threading
import uuid


class AuthorityError(RuntimeError):
    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class Actor:
    scope: str


def canonical(value):
    try:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError, RecursionError) as exc:
        raise AuthorityError("invalid_payload") from exc
    if len(encoded) > 1_048_576:
        raise AuthorityError("payload_too_large")
    return encoded


def identifier(value):
    if type(value) is not str:
        raise AuthorityError("invalid_identifier")
    try:
        parsed = uuid.UUID(value)
    except ValueError as exc:
        raise AuthorityError("invalid_identifier") from exc
    if str(parsed) != value or parsed.int == 0:
        raise AuthorityError("invalid_identifier")
    return value


def text(value, limit=8192):
    if type(value) is not str or not value.strip() or len(value) > limit or "\x00" in value:
        raise AuthorityError("invalid_text")
    return value


def instant(value):
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None or dt.utcoffset() is None:
            raise ValueError()
        return dt.astimezone(UTC).isoformat()
    except (ValueError, TypeError, AttributeError) as exc:
        raise AuthorityError("invalid_time") from exc


class Authority:
    """Lifetime flock plus durable generations fence every transaction.

    Never unlink the lock file, including at shutdown. No automatic JSON import.
    A lost commit acknowledgement is reconciled with the original request ID.
    Storage exceptions poison this instance; reopening is an explicit action.
    """
    def __init__(self, path, *, allow_simulation=False, busy_ms=100, fault_hook=None, legacy_paths=()):
        self.path = Path(path).absolute()
        self._closed = False
        self._poisoned = False
        self._mutex = threading.RLock()
        self.allow_simulation = allow_simulation is True
        self._fault = fault_hook or (lambda stage: None)
        self._pid = os.getpid()
        self._conn = None
        self._lockfd = None
        if type(busy_ms) is not int or not 1 <= busy_ms <= 1000:
            raise AuthorityError("invalid_busy_timeout")
        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        for parent in [self.path.parent, *self.path.parent.parents]:
            if parent.is_symlink():
                raise AuthorityError("unsafe_store_path")
        if self.path.parent.stat().st_mode & 0o077:
            raise AuthorityError("store_directory_not_private")
        # Existing legacy state requires explicit migration; never silently start
        # an empty authority beside a populated JSON store.
        legacy_present = any(Path(p).exists() or Path(p).is_symlink() for p in legacy_paths)
        lockpath = self.path.with_suffix(self.path.suffix + ".writer.lock")
        try:
            self._lockfd = os.open(lockpath, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
            self._check_file(self._lockfd)
            try:
                fcntl.flock(self._lockfd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise AuthorityError("owner_busy") from exc
            self._lock_identity = self._identity(os.fstat(self._lockfd))
            self._lockpath = lockpath
            initialized = False
            if self.path.exists() and self.path.stat().st_size:
                # Inspect existing evidence read-only BEFORE journal/DDL changes.
                fd = os.open(self.path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
                try: self._check_file(fd)
                finally: os.close(fd)
                probe = sqlite3.connect(self.path.as_uri() + "?mode=ro", uri=True, isolation_level=None)
                try:
                    versions = probe.execute("SELECT version FROM meta").fetchall()
                    if versions != [(1,)]:
                        raise AuthorityError("unsupported_schema")
                    expected = {"meta", "ownership", "control", "records", "receipts", "events", "outbox", "simulation_effects", "sqlite_sequence"}
                    actual = {r[0] for r in probe.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                    if actual != expected or not probe.execute("SELECT 1 FROM ownership WHERE id=1").fetchone():
                        raise AuthorityError("unsupported_schema")
                    initialized = True
                    if legacy_present and not probe.execute("SELECT 1 FROM receipts WHERE operation='import_legacy_snapshot' LIMIT 1").fetchone():
                        raise AuthorityError("legacy_migration_required")
                except sqlite3.Error as exc:
                    raise AuthorityError("unsupported_schema") from exc
                finally:
                    probe.close()
            if legacy_present and not initialized:
                raise AuthorityError("legacy_migration_required")
            fd = os.open(self.path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
            try:
                self._check_file(fd)
                self._db_identity = self._identity(os.fstat(fd))
            finally:
                os.close(fd)
            self._conn = sqlite3.connect(self.path, timeout=busy_ms / 1000, isolation_level=None, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=FULL")
            self._conn.execute(f"PRAGMA busy_timeout={busy_ms}")
            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS meta(version INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS ownership(id INTEGER PRIMARY KEY CHECK(id=1), generation INTEGER NOT NULL, owner TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS control(id INTEGER PRIMARY KEY CHECK(id=1), enabled INTEGER NOT NULL, epoch INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS records(kind TEXT NOT NULL, id TEXT NOT NULL, scope TEXT NOT NULL, data TEXT NOT NULL, PRIMARY KEY(kind,id));
                CREATE TABLE IF NOT EXISTS receipts(request_id TEXT PRIMARY KEY, scope TEXT NOT NULL, operation TEXT NOT NULL, payload_hash TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL, data TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS outbox(task_id TEXT PRIMARY KEY, state TEXT NOT NULL, claim_id TEXT, generation INTEGER);
                CREATE TABLE IF NOT EXISTS simulation_effects(task_id TEXT PRIMARY KEY, claim_id TEXT NOT NULL);
            """)
            self._conn.execute("BEGIN IMMEDIATE")
            versions = self._conn.execute("SELECT version FROM meta").fetchall()
            if not versions:
                self._conn.execute("INSERT INTO meta VALUES(1)")
            elif len(versions) != 1 or versions[0][0] != 1:
                raise AuthorityError("unsupported_schema")
            row = self._conn.execute("SELECT generation FROM ownership WHERE id=1").fetchone()
            self.generation = row[0] + 1 if row else 1
            self.owner_id = str(uuid.uuid4())
            self._conn.execute("INSERT OR REPLACE INTO ownership VALUES(1,?,?)", (self.generation, self.owner_id))
            self._conn.execute("INSERT OR IGNORE INTO control VALUES(1,0,0)")
            self._conn.execute("UPDATE control SET enabled=0,epoch=epoch+1")
            # Admission never implies execution. A killed simulator may have
            # applied its synthetic effect; retain ambiguity across takeover.
            for row in self._conn.execute("SELECT task_id FROM outbox WHERE state='simulating'").fetchall():
                task = self._get("task", row[0])
                task["status"] = "unknown"
                self._put("task", task["task_id"], task["scope"], task)
            self._conn.execute("UPDATE outbox SET state='unknown' WHERE state='simulating'")
            self._conn.execute("COMMIT")
            directory = os.open(self.path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try: os.fsync(directory)
            finally: os.close(directory)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def _identity(st):
        return st.st_dev, st.st_ino

    @staticmethod
    def _check_file(fd):
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != os.getuid() or st.st_mode & 0o077:
            raise AuthorityError("unsafe_store_file")

    def _fence(self):
        if self._closed or self._poisoned or os.getpid() != self._pid:
            raise AuthorityError("authority_unavailable")
        if self._identity(self.path.stat(follow_symlinks=False)) != self._db_identity or self._identity(self._lockpath.stat(follow_symlinks=False)) != self._lock_identity:
            self._poisoned = True
            raise AuthorityError("store_replaced")
        row = self._conn.execute("SELECT generation,owner FROM ownership WHERE id=1").fetchone()
        if tuple(row) != (self.generation, self.owner_id):
            self._poisoned = True
            raise AuthorityError("owner_fenced")

    @contextmanager
    def _transaction(self):
        with self._mutex:
            self._fence()
            try:
                self._conn.execute("BEGIN IMMEDIATE")
                self._fence()
                yield
                self._fault("before_commit")
                self._conn.execute("COMMIT")
            except BaseException as exc:
                try:
                    if self._conn.in_transaction:
                        self._conn.execute("ROLLBACK")
                except sqlite3.Error:
                    self._poisoned = True
                if isinstance(exc, sqlite3.Error):
                    self._poisoned = True
                    raise AuthorityError("storage_unknown_reconcile") from exc
                raise

    @staticmethod
    def _scope(actor):
        if type(actor) is not Actor:
            raise AuthorityError("invalid_actor")
        return text(actor.scope, 128)

    def _mutate(self, actor, request_id, operation, payload, effect):
        scope = self._scope(actor)
        identifier(request_id)
        digest = hashlib.sha256(canonical([scope, operation, payload]).encode()).hexdigest()
        self._fault("before_begin")
        with self._transaction():
            row = self._conn.execute("SELECT * FROM receipts WHERE request_id=?", (request_id,)).fetchone()
            if row:
                if (row["scope"], row["operation"], row["payload_hash"]) != (scope, operation, digest):
                    raise AuthorityError("request_conflict")
                receipt = json.loads(row["data"])
                replayed = True
            else:
                result = effect(scope)
                self._fault("after_effect_sql")
                receipt = {"request_id": request_id, "scope": scope, "operation": operation, "payload_hash": digest, "state": "committed", "result": result}
                self._conn.execute("INSERT INTO receipts VALUES(?,?,?,?,?)", (request_id, scope, operation, digest, canonical(receipt)))
                self._conn.execute("INSERT INTO events(request_id,data) VALUES(?,?)", (request_id, canonical(receipt)))
                replayed = False
        self._fault("after_commit_before_ack")
        return {**receipt, "replayed": replayed}

    def _get(self, kind, ident, scope=None):
        row = self._conn.execute("SELECT scope,data FROM records WHERE kind=? AND id=?", (kind, ident)).fetchone()
        if not row or scope is not None and row["scope"] != scope:
            raise AuthorityError("not_found")
        return json.loads(row["data"])

    def _put(self, kind, ident, scope, value):
        self._conn.execute("INSERT INTO records VALUES(?,?,?,?) ON CONFLICT(kind,id) DO UPDATE SET scope=excluded.scope,data=excluded.data", (kind, ident, scope, canonical(value)))

    def _new_task(self, scope, task_id, goal, *, status="pending", metadata=None, occurrence_id=None):
        task = {"task_id": task_id, "scope": scope, "goal": goal, "status": status, "created_at": datetime.now(UTC).isoformat(), "result": None, "error": None, "cancel_requested": False, "metadata": metadata or {}, "occurrence_id": occurrence_id}
        self._put("task", task_id, scope, task)
        self._conn.execute("INSERT INTO outbox(task_id,state) VALUES(?,?)", (task_id, "held" if status == "pending" else "unknown"))
        return task

    def submit(self, actor, request_id, goal):
        text(goal)
        return self._mutate(actor, request_id, "submit", {"goal": goal}, lambda scope: self._new_task(scope, str(uuid.uuid4()), goal))

    def receipt(self, actor, request_id):
        scope = self._scope(actor)
        identifier(request_id)
        with self._mutex:
            self._fence()
            row = self._conn.execute("SELECT data FROM receipts WHERE request_id=? AND scope=?", (request_id, scope)).fetchone()
            return json.loads(row[0]) if row else None

    def _list(self, kind, actor):
        scope = self._scope(actor)
        with self._mutex:
            self._fence()
            return [json.loads(row[0]) for row in self._conn.execute("SELECT data FROM records WHERE kind=? AND scope=? ORDER BY rowid", (kind, scope))]

    def list_tasks(self, actor):
        with self._mutex:
            result = self._list("task", actor)
            for row in result:
                row["outbox_state"] = self._conn.execute("SELECT state FROM outbox WHERE task_id=?", (row["task_id"],)).fetchone()[0]
            return result

    def list_schedules(self, actor, include_removed=False):
        return [j for j in self._list("schedule", actor) if include_removed or not j["removed"]]

    def _cancel(self, task):
        state = self._conn.execute("SELECT state FROM outbox WHERE task_id=?", (task["task_id"],)).fetchone()[0]
        task["cancel_requested"] = True
        if state == "held":
            task["status"] = "cancelled"
            self._conn.execute("UPDATE outbox SET state='cancelled' WHERE task_id=?", (task["task_id"],))
        self._put("task", task["task_id"], task["scope"], task)
        return task

    def cancel(self, actor, request_id, task_id):
        identifier(task_id)
        return self._mutate(actor, request_id, "cancel", {"task_id": task_id}, lambda scope: self._cancel(self._get("task", task_id, scope)))

    def add_schedule(self, actor, request_id, name, cron_expr, goal, next_run_at):
        text(name, 256); text(cron_expr, 256); text(goal)
        next_run_at = instant(next_run_at)
        def effect(scope):
            job_id = str(uuid.uuid4())
            job = dict(job_id=job_id, scope=scope, name=name, cron_expr=cron_expr, goal=goal, enabled=True, removed=False, revision=1, last_run=None, next_run_at=next_run_at, metadata={})
            self._put("schedule", job_id, scope, job)
            return job
        return self._mutate(actor, request_id, "add_schedule", dict(name=name, cron_expr=cron_expr, goal=goal, next_run_at=next_run_at), effect)

    def set_schedule(self, actor, request_id, job_id, *, enabled=False, removed=False):
        identifier(job_id)
        if type(enabled) is not bool or type(removed) is not bool:
            raise AuthorityError("invalid_payload")
        def effect(scope):
            job = self._get("schedule", job_id, scope)
            if job["removed"] or enabled:
                # Re-enabling requires an independently chosen next nominal,
                # not replay of overdue callbacks. No implicit catch-up.
                raise AuthorityError("schedule_recreation_required")
            job.update(enabled=False, removed=removed, revision=job["revision"] + 1)
            self._put("schedule", job_id, scope, job)
            for task in self._list("task", actor):
                if task["metadata"].get("job_id") == job_id:
                    self._cancel(task)
            return job
        return self._mutate(actor, request_id, "set_schedule", dict(job_id=job_id, enabled=enabled, removed=removed), effect)

    def scheduler_control(self, actor, request_id, enabled):
        if type(enabled) is not bool:
            raise AuthorityError("invalid_payload")
        def effect(scope):
            self._conn.execute("UPDATE control SET enabled=?,epoch=epoch+1", (int(enabled),))
            if not enabled:
                # This is the single application-wide authority; stop cancels
                # every pending scheduled occurrence across its namespaces.
                for row in self._conn.execute("SELECT data FROM records WHERE kind='task'").fetchall():
                    task = json.loads(row[0])
                    if task["occurrence_id"]:
                        self._cancel(task)
            return dict(self._conn.execute("SELECT enabled,epoch FROM control").fetchone())
        return self._mutate(actor, request_id, "scheduler_control", {"enabled": enabled}, effect)

    def admit_occurrence(self, actor, job_id, revision, nominal, epoch, next_run_at):
        identifier(job_id)
        nominal, next_run_at = instant(nominal), instant(next_run_at)
        if type(revision) is not int or type(epoch) is not int or revision < 1 or next_run_at <= nominal:
            raise AuthorityError("invalid_occurrence")
        occurrence_id = str(uuid.uuid5(uuid.UUID(job_id), f"{revision}:{nominal}"))
        def effect(scope):
            job = self._get("schedule", job_id, scope)
            control = self._conn.execute("SELECT enabled,epoch FROM control").fetchone()
            if not control["enabled"] or control["epoch"] != epoch or not job["enabled"] or job["removed"] or job["revision"] != revision or job["next_run_at"] != nominal:
                raise AuthorityError("stale_occurrence")
            task = self._new_task(scope, str(uuid.uuid5(uuid.UUID(occurrence_id), "task")), job["goal"], metadata={"job_id": job_id, "revision": revision, "nominal": nominal}, occurrence_id=occurrence_id)
            self._put("occurrence", occurrence_id, scope, {"occurrence_id": occurrence_id, "task_id": task["task_id"], "nominal": nominal})
            job.update(last_run=nominal, next_run_at=next_run_at)
            self._put("schedule", job_id, scope, job)
            return task
        return self._mutate(actor, occurrence_id, "occurrence", dict(job_id=job_id, revision=revision, nominal=nominal, next_run_at=next_run_at), effect)

    def import_legacy_snapshot(self, actor, request_id, *, tasks, schedules, evidence):
        def effect(scope):
            if self._conn.execute("SELECT 1 FROM records LIMIT 1").fetchone():
                raise AuthorityError("nonempty_migration_target")
            mapping = {"task_ids": {}, "schedule_ids": {}, "tasks_imported": len(tasks), "schedules_imported": len(schedules), "evidence": evidence}
            for old in tasks:
                new_id = str(uuid.uuid5(uuid.NAMESPACE_URL, canonical([scope, "legacy-task", old["task_id"]])))
                mapping["task_ids"][old["task_id"]] = new_id
                self._new_task(scope, new_id, old["goal"], status="pending" if old.get("status", "pending") == "pending" else "unknown", metadata={"legacy": old})
            for old in schedules:
                new_id = str(uuid.uuid5(uuid.NAMESPACE_URL, canonical([scope, "legacy-schedule", old["job_id"]])))
                mapping["schedule_ids"][old["job_id"]] = new_id
                self._put("schedule", new_id, scope, dict(job_id=new_id, scope=scope, name=old["name"], cron_expr=old["cron_expr"], goal=old["goal"], enabled=False, removed=False, revision=1, last_run=None, next_run_at=None, metadata={"legacy": old, "legacy_last_run": old.get("last_run")}))
            return mapping
        return self._mutate(actor, request_id, "import_legacy_snapshot", dict(tasks=tasks, schedules=schedules, evidence=evidence), effect)

    def readiness(self):
        with self._mutex:
            self._fence()
            return {"storage_ready": True, "owner_generation": self.generation, "execution_enabled": False, "reconciliation_required": self._conn.execute("SELECT COUNT(*) FROM outbox WHERE state='unknown'").fetchone()[0]}

    def close(self):
        with self._mutex:
            if self._closed:
                return
            self._closed = True
            try:
                if self._conn is not None:
                    self._conn.close()
            finally:
                if self._lockfd is not None:
                    os.close(self._lockfd)
