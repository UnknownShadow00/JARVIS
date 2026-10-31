"""Offline scheduler transactions/admission with source definitions and inert backend."""
from __future__ import annotations

import ast
import asyncio
import contextlib
from dataclasses import asdict
import errno
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SOURCE_OVERRIDES = {}
spec = importlib.util.spec_from_file_location("_scheduler_fixture_helpers", ROOT / "tests/test_task_queue_persistence.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


class BackendRecorder:
    """No timers, threads, service, framework import, network or automatic execution."""
    def __init__(self):
        self.callbacks = {}
        self.started = False
        self.shutdowns = 0

    def add_job(self, callback, *, trigger, args, id, replace_existing):
        self.callbacks[id] = (callback, args)

    def remove_job(self, job_id, *, jobstore):
        self.callbacks.pop(job_id, None)

    def start(self):
        self.started = True

    def shutdown(self, *, wait):
        self.shutdowns += 1
        self.started = False


class TriggerRecorder:
    @staticmethod
    def from_crontab(expression):
        if expression == "bad cron":
            raise ValueError("fixture invalid cron")
        return expression


class ResponseRecorder:
    def __init__(self, *, status_code, content):
        self.status_code, self.content = status_code, content


def api_definitions(owner, module):
    path = SOURCE_OVERRIDES.get("server.py", ROOT / "app/server.py")
    tree = ast.parse(path.read_text(), filename=str(path))
    names = {"create_scheduled_job", "delete_scheduled_job", "list_scheduled_jobs", "_schedule_write_error"}
    nodes = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            nodes.append(node)
    namespace = {"scheduler": owner, "asdict": asdict, "JSONResponse": ResponseRecorder,
                 "SchedulerOperationError": getattr(module, "SchedulerOperationError", type("AbsentSchedulerError", (RuntimeError,), {}))}
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[])), str(path), "exec"), namespace)
    return types.SimpleNamespace(**{key: value for key, value in namespace.items() if not key.startswith("__")})


class SchedulerReliabilityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jarvis-scheduler-r4-")
        self.addCleanup(self.temporary.cleanup)
        self.store = Path(self.temporary.name) / "jobs.json"
        self.audit = helpers.AuditRecorder()
        self.queue_module = helpers.load_definitions(
            ROOT / "app/agent/task_queue.py", injected={"audit": self.audit}, remove_singleton="task_queue",
        )
        self.queue = self.queue_module.TaskQueue(Path(self.temporary.name) / "tasks.json")
        injected = {"audit": self.audit, "task_queue": self.queue}
        for name in ("TaskQueueAuditError", "TaskQueueIdentifierError", "TaskQueuePersistenceError"):
            injected[name] = getattr(self.queue_module, name)
        self.module = helpers.load_definitions(
            SOURCE_OVERRIDES.get("scheduler.py", ROOT / "app/agent/scheduler.py"),
            injected=injected, remove_singleton="scheduler",
        )
        self.module._load_apscheduler = lambda: True
        self.module.AsyncIOScheduler = BackendRecorder
        self.module.CronTrigger = TriggerRecorder
        self.owner = self.module.Scheduler(self.store)

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def seed(self):
        job = self.owner.add_job("original", "* * * * *", "inspect")
        self.audit.events.clear()
        return job

    def start_recording(self):
        self.run_async(self.owner.start())
        return self.owner._scheduler

    def fire(self, callback):
        function, args = callback
        return self.run_async(function(*args))

    @contextlib.contextmanager
    def fault(self, stage):
        failure = OSError(errno.EIO, f"injected {stage}")
        if stage in {"write", "flush"}:
            real = self.module.tempfile.NamedTemporaryFile

            @contextlib.contextmanager
            def opened(*args, **kwargs):
                with real(*args, **kwargs) as file:
                    wrapper = types.SimpleNamespace(name=file.name, write=file.write, flush=file.flush, fileno=file.fileno)
                    setattr(wrapper, stage, mock.Mock(side_effect=failure))
                    yield wrapper

            with mock.patch.object(self.module.tempfile, "NamedTemporaryFile", opened):
                yield
            return
        owner, name = {
            "mkdir": (self.module.Path, "mkdir"), "create": (self.module.tempfile, "NamedTemporaryFile"),
            "file_sync": (self.module.os, "fsync"), "replace": (self.module.os, "replace"),
        }[stage]
        with mock.patch.object(owner, name, side_effect=failure):
            yield

    def test_add_remove_prepublication_faults_preserve_disk_memory_backend(self):
        for operation in ("create", "delete"):
            for stage in ("mkdir", "create", "write", "flush", "file_sync", "replace"):
                with self.subTest(operation=operation, stage=stage):
                    self.owner = self.module.Scheduler(self.store)
                    job = self.seed()
                    backend = self.start_recording()
                    before, jobs, callbacks = self.store.read_bytes(), self.owner.list_jobs(), backend.callbacks.copy()
                    self.audit.events.clear()
                    with self.fault(stage):
                        with self.assertRaises(self.module.SchedulerOperationError) as caught:
                            if operation == "create":
                                self.owner.add_job("new", "* * * * *", "new goal")
                            else:
                                self.owner.remove_job(job.job_id)
                    self.assertFalse(caught.exception.applied)
                    self.assertFalse(caught.exception.published)
                    self.assertEqual(self.store.read_bytes(), before)
                    self.assertEqual(self.owner.list_jobs(), jobs)
                    self.assertEqual(backend.callbacks, callbacks)
                    self.assertNotIn("job_added", [event for event, _ in self.audit.events])
                    self.assertNotIn("job_removed", [event for event, _ in self.audit.events])
                    self.assertEqual(list(self.store.parent.glob(".jobs.json.*.tmp")), [])

    def test_postpublication_failure_retains_state_and_blocks_all_admission(self):
        for operation in ("create", "delete"):
            with self.subTest(operation=operation):
                self.owner = self.module.Scheduler(self.store)
                job = self.seed()
                backend = self.start_recording()
                retained = backend.callbacks[job.job_id]
                with mock.patch.object(self.owner, "_sync_directory", side_effect=OSError("uncertain")):
                    with self.assertRaises(self.module.SchedulerOperationError) as caught:
                        if operation == "create":
                            self.owner.add_job("new", "* * * * *", "new goal")
                        else:
                            self.owner.remove_job(job.job_id)
                self.assertTrue(caught.exception.applied)
                self.assertTrue(caught.exception.published)
                self.assertTrue(caught.exception.uncertain)
                self.assertEqual(json.loads(self.store.read_text()), [asdict(item) for item in self.owner.list_jobs()])
                self.fire(retained)
                self.assertEqual(self.run_async(self.queue.list_tasks()), [])
                with self.assertRaises(self.module.SchedulerOperationError):
                    self.owner.add_job("blocked", "* * * * *", "blocked")
                self.run_async(self.owner.stop())
                with self.assertRaises(self.module.SchedulerOperationError):
                    self.run_async(self.owner.start())

    def test_success_roundtrip_missing_remove_and_exact_fields(self):
        job = self.owner.add_job(" name ", "* * * * *", " inspect ")
        loaded = self.module.Scheduler(self.store).list_jobs()
        self.assertEqual([asdict(item) for item in loaded], [asdict(job)])
        self.assertFalse(self.owner.remove_job("missing"))
        self.assertTrue(self.owner.remove_job(job.job_id))
        self.assertEqual(json.loads(self.store.read_text()), [])

    def test_disabled_job_is_not_registered_and_retained_callback_is_rejected(self):
        job = self.seed()
        job.enabled = False
        self.store.write_text(json.dumps([asdict(job)]))
        self.owner = self.module.Scheduler(self.store)
        job = self.owner.list_jobs()[0]
        self.assertIs(job.enabled, False)
        backend = self.start_recording()
        self.assertEqual(backend.callbacks, {})
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.run_async(self.owner.stop())
        job.enabled = True
        backend = self.start_recording()
        retained = backend.callbacks[job.job_id]
        job.enabled = False
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_removed_callback_cannot_enqueue_even_when_backend_removal_fails(self):
        job = self.seed()
        backend = self.start_recording()
        retained = backend.callbacks[job.job_id]
        with mock.patch.object(backend, "remove_job", side_effect=RuntimeError("backend retained callback")):
            with self.assertRaises(self.module.SchedulerOperationError) as caught:
                self.owner.remove_job(job.job_id)
        self.assertTrue(caught.exception.applied)
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.assertNotIn(job, self.owner.list_jobs())

    def test_removed_callback_rejected_after_successful_remove(self):
        job = self.seed()
        backend = self.start_recording()
        retained = backend.callbacks[job.job_id]
        self.assertTrue(self.owner.remove_job(job.job_id))
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_stop_restart_rejects_prior_generation_and_accepts_current_callback(self):
        job = self.seed()
        first = self.start_recording().callbacks[job.job_id]
        self.run_async(self.owner.stop())
        self.fire(first)
        current = self.start_recording().callbacks[job.job_id]
        self.fire(first)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.fire(current)
        self.assertEqual(len(self.run_async(self.queue.list_tasks())), 1)

    def test_old_object_same_identifier_and_disabled_bare_helper_rejected(self):
        job = self.seed()
        retained = self.start_recording().callbacks[job.job_id]
        self.owner._jobs[job.job_id] = self.module.ScheduledJob(job.job_id, "replacement", "* * * * *", "different")
        self.fire(retained)
        job.enabled = False
        self.run_async(self.module._run_job(job))
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_registration_failure_after_save_is_explicit_and_fail_closed(self):
        original = self.seed()
        backend = self.start_recording()
        retained = backend.callbacks[original.job_id]
        with mock.patch.object(backend, "add_job", side_effect=RuntimeError("registration uncertain")):
            with self.assertRaises(self.module.SchedulerOperationError) as caught:
                self.owner.add_job("new", "* * * * *", "new")
        self.assertTrue(caught.exception.applied)
        self.assertTrue(caught.exception.published)
        self.assertEqual(len(json.loads(self.store.read_text())), 2)
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_invalid_cron_is_rejected_before_snapshot_or_backend_start(self):
        self.seed()
        before = self.store.read_bytes()
        with self.assertRaises(self.module.SchedulerOperationError) as caught:
            self.owner.add_job("bad", "bad cron", "bad")
        self.assertFalse(caught.exception.applied)
        self.assertEqual(caught.exception.phase, "validation")
        self.assertEqual(self.store.read_bytes(), before)
        self.owner._jobs["legacy"] = self.module.ScheduledJob("legacy", "legacy", "bad cron", "legacy")
        with mock.patch.object(self.module, "AsyncIOScheduler") as constructed:
            with self.assertRaises(self.module.SchedulerOperationError):
                self.run_async(self.owner.start())
        constructed.assert_not_called()

    def test_start_registration_or_start_failure_blocks_callbacks_and_reports_failure(self):
        for method in ("add_job", "start"):
            with self.subTest(method=method):
                self.owner = self.module.Scheduler(self.store)
                self.seed()
                with mock.patch.object(BackendRecorder, method, side_effect=RuntimeError("failed backend")):
                    with self.assertRaises(self.module.SchedulerOperationError):
                        self.run_async(self.owner.start())
                self.assertFalse(self.owner._running)
                self.assertNotIn("scheduler_start", [event for event, _ in self.audit.events])

    def test_shutdown_failure_invalidates_callbacks_before_backend_call(self):
        job = self.seed()
        backend = self.start_recording()
        retained = backend.callbacks[job.job_id]
        with mock.patch.object(backend, "shutdown", side_effect=RuntimeError("still running")):
            with self.assertRaises(self.module.SchedulerOperationError):
                self.run_async(self.owner.stop())
        self.assertFalse(self.owner._running)
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_malformed_stores_block_writes_and_start_without_erasing_evidence(self):
        valid = {"job_id": "legacy", "name": "legacy", "cron_expr": "* * * * *", "goal": "legacy"}
        for payload in [b"{invalid", b"\xff", b"{}", b"[null]", json.dumps([valid, None]).encode(),
                        json.dumps([valid, valid]).encode(), json.dumps([{**valid, "enabled": "false"}]).encode(),
                        json.dumps([{**valid, "unknown": "preserve"}]).encode()]:
            with self.subTest(payload=payload[:40]):
                self.store.write_bytes(payload)
                owner = self.module.Scheduler(self.store)
                with self.assertRaises(self.module.SchedulerOperationError):
                    owner.add_job("blocked", "* * * * *", "blocked")
                with self.assertRaises(self.module.SchedulerOperationError):
                    self.run_async(owner.start())
                self.assertEqual(self.store.read_bytes(), payload)

    def test_identifier_collisions_bounded_without_overwrite(self):
        original = self.seed()
        before = self.store.read_bytes()
        with mock.patch.object(self.module.uuid, "uuid4", return_value=original.job_id + "-collision") as generated:
            with self.assertRaises(self.module.SchedulerOperationError):
                self.owner.add_job("collision", "* * * * *", "collision")
        self.assertEqual(generated.call_count, 32)
        self.assertEqual(self.store.read_bytes(), before)

    def test_applied_audit_failure_is_explicit_and_blocks_later_admission(self):
        job = self.seed()
        backend = self.start_recording()
        retained = backend.callbacks[job.job_id]
        with mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit failed")):
            with self.assertRaises(self.module.SchedulerOperationError) as caught:
                self.owner.remove_job(job.job_id)
        self.assertTrue(caught.exception.applied)
        self.assertTrue(caught.exception.published)
        self.assertEqual(caught.exception.phase, "audit")
        self.fire(retained)
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_already_admitted_enqueue_can_finish_after_remove_and_is_not_retried(self):
        job = self.seed()
        retained = self.start_recording().callbacks[job.job_id]
        original = self.queue.add_task

        async def scenario():
            entered, release = asyncio.Event(), asyncio.Event()

            async def waiting(goal):
                entered.set()
                await release.wait()
                return await original(goal)

            with mock.patch.object(self.queue, "add_task", side_effect=waiting) as enqueued:
                callback, args = retained
                admitted = asyncio.create_task(callback(*args))
                await entered.wait()
                self.assertTrue(self.owner.remove_job(job.job_id))
                release.set()
                await admitted
            self.assertEqual(enqueued.call_count, 1)
            self.assertEqual(len(await self.queue.list_tasks()), 1)
            await callback(*args)
            self.assertEqual(len(await self.queue.list_tasks()), 1)

        self.run_async(scenario())
        self.assertEqual(json.loads(self.store.read_text()), [])

    def test_start_audit_failure_cleans_backend_and_blocks_captured_callback(self):
        job = self.seed()
        backend = BackendRecorder()
        original_log = self.audit.log

        def report(event, details):
            if event == "scheduler_start":
                raise RuntimeError("audit unavailable")
            return original_log(event, details)

        with mock.patch.object(self.module, "AsyncIOScheduler", return_value=backend), \
                mock.patch.object(self.audit, "log", side_effect=report):
            with self.assertRaises(self.module.SchedulerOperationError) as caught:
                self.run_async(self.owner.start())
        self.assertTrue(caught.exception.applied)
        self.assertFalse(self.owner._running)
        self.assertEqual(backend.shutdowns, 1)
        self.fire(backend.callbacks[job.job_id])
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])

    def test_unsupported_directory_sync_and_cleanup_reporting_failures(self):
        self.seed()
        real_sync = self.module.os.fsync
        for code in {errno.EINVAL, errno.ENOTSUP, errno.ENOSYS}:
            count = 0

            def sync(descriptor):
                nonlocal count
                count += 1
                if count == 2:
                    raise OSError(code, "unsupported directory sync")
                return real_sync(descriptor)

            with self.subTest(errno=code), mock.patch.object(self.module.os, "fsync", side_effect=sync):
                self.owner.add_job("unsupported sync", "* * * * *", "goal")
            self.assertFalse(self.owner._persistence_uncertain)
        before = self.store.read_bytes()
        with mock.patch.object(self.module.os, "replace", side_effect=OSError("replace failed")), \
                mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit unavailable")), \
                mock.patch.object(self.module.Path, "unlink", side_effect=OSError("cleanup failed")):
            with self.assertRaises(self.module.SchedulerOperationError):
                self.owner.add_job("not saved", "* * * * *", "goal")
        self.assertEqual(self.store.read_bytes(), before)
        self.assertFalse(self.owner._persistence_uncertain)
        self.assertEqual(len(list(self.store.parent.glob(".jobs.json.*.tmp"))), 1)

    def test_load_io_and_nonregular_files_block_missing_delete_and_start(self):
        self.store.write_text("[]")
        with mock.patch.object(self.module.Scheduler, "_read_store", side_effect=PermissionError("denied")):
            owner = self.module.Scheduler(self.store)
        with self.assertRaises(self.module.SchedulerOperationError):
            owner.remove_job("unknown because load failed")
        self.store.unlink()
        self.store.mkdir()
        owner = self.module.Scheduler(self.store)
        with self.assertRaises(self.module.SchedulerOperationError):
            self.run_async(owner.start())

    def test_stub_mode_and_idempotent_start_have_no_actual_backend(self):
        self.module._load_apscheduler = lambda: False
        self.owner.add_job("stored only", "opaque stub cron", "goal")
        self.run_async(self.owner.start())
        generation = self.owner._generation
        self.assertTrue(self.owner._running)
        self.assertIsNone(self.owner._scheduler)
        self.run_async(self.owner.start())
        self.assertEqual(self.owner._generation, generation)
        self.run_async(self.owner.stop())
        self.assertFalse(self.owner._running)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO requires POSIX")
    def test_fifo_store_rejected_with_child_deadline(self):
        os.mkfifo(self.store)
        source = SOURCE_OVERRIDES.get("scheduler.py", ROOT / "app/agent/scheduler.py")
        program = '''import importlib.util,sys
from pathlib import Path
s=importlib.util.spec_from_file_location("fixture_helpers",sys.argv[1])
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
module=m.load_definitions(Path(sys.argv[2]),injected={"audit":m.AuditRecorder()},remove_singleton="scheduler")
owner=module.Scheduler(Path(sys.argv[3]));assert owner._load_error
'''
        subprocess.run([
            sys.executable, "-B", "-c", program, str(ROOT / "tests/test_task_queue_persistence.py"),
            str(source), str(self.store),
        ], timeout=5, check=True, capture_output=True, text=True)

    def test_create_audit_failure_after_registration_does_not_admit_new_callback(self):
        backend = self.start_recording()
        original_log = self.audit.log

        def report(event, details):
            if event == "job_added":
                raise RuntimeError("audit unavailable")
            return original_log(event, details)

        with mock.patch.object(self.audit, "log", side_effect=report):
            with self.assertRaises(self.module.SchedulerOperationError) as caught:
                self.owner.add_job("applied", "* * * * *", "applied")
        self.assertTrue(caught.exception.applied)
        self.assertTrue(caught.exception.published)
        self.assertEqual(caught.exception.phase, "audit")
        self.fire(backend.callbacks[caught.exception.job_id])
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.assertEqual(len(json.loads(self.store.read_text())), 1)

    def test_failed_start_cleanup_preserves_backend_reference_and_rejects_callbacks(self):
        job = self.seed()
        backend = BackendRecorder()
        with mock.patch.object(self.module, "AsyncIOScheduler", return_value=backend), \
                mock.patch.object(backend, "start", side_effect=RuntimeError("start failed")), \
                mock.patch.object(backend, "shutdown", side_effect=RuntimeError("cleanup failed")):
            with self.assertRaises(self.module.SchedulerOperationError):
                self.run_async(self.owner.start())
        self.assertIs(self.owner._scheduler, backend)
        self.fire(backend.callbacks[job.job_id])
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.run_async(self.owner.stop())
        self.assertIsNone(self.owner._scheduler)
        with self.assertRaises(self.module.SchedulerOperationError):
            self.run_async(self.owner.start())

    def test_scheduler_api_returns_sanitized_failure_outcomes_and_success_compatibility(self):
        api = api_definitions(self.owner, self.module)
        request = types.SimpleNamespace(name="new", cron_expr="* * * * *", goal="inspect")
        with mock.patch.object(self.module.os, "replace", side_effect=OSError("private path")):
            response = self.run_async(api.create_scheduled_job(request))
        self.assertIsInstance(response, ResponseRecorder)
        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.content["automatic_retry"])
        self.assertFalse(response.content["state_applied"])
        self.assertNotIn("private path", json.dumps(response.content))
        job = self.run_async(api.create_scheduled_job(request))
        with mock.patch.object(self.owner, "_sync_directory", side_effect=OSError("uncertain")):
            response = self.run_async(api.delete_scheduled_job(job["job_id"]))
        self.assertEqual(response.status_code, 409)
        self.assertTrue(response.content["state_applied"])
        self.assertEqual(response.content["publication"], "published_durability_unknown")

    def test_atomic_publication_sync_order_and_invalid_new_records(self):
        self.seed()
        previous = self.store.read_bytes()
        replace = self.module.os.replace
        fsync = self.module.os.fsync
        order = []

        def synced(descriptor):
            order.append("sync")
            return fsync(descriptor)

        def replaced(source, target):
            self.assertEqual(Path(source).parent, self.store.parent)
            self.assertEqual(self.store.read_bytes(), previous)
            self.assertEqual(len(json.loads(Path(source).read_text())), 2)
            order.append("replace")
            return replace(source, target)

        with mock.patch.object(self.module.os, "fsync", side_effect=synced), mock.patch.object(self.module.os, "replace", side_effect=replaced):
            self.owner.add_job("second", "* * * * *", "second")
        self.assertEqual(order, ["sync", "replace", "sync"] if os.name == "posix" else ["sync", "replace"])
        before = self.store.read_bytes()
        with self.assertRaises(self.module.SchedulerOperationError):
            self.owner.add_job("", "* * * * *", "blank")
        self.assertEqual(self.store.read_bytes(), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
