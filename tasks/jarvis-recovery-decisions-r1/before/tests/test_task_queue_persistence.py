"""Offline source-level checks; deliberately not full application integration.

Load the real definitions with only audit/default-singleton wiring isolated. Never
import app configuration, start audit threads, or touch the real data directory.
Run with the packet's run_checks.py using the Python standard library only.
"""
from __future__ import annotations

import ast
import asyncio
import contextlib
import errno
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock
import uuid

ROOT = Path(__file__).resolve().parents[1]


class AuditRecorder:
    def __init__(self):
        self.events = []

    def log(self, event, details):
        self.events.append((event, details))


def load_definitions(path, *, injected=None, remove_singleton=None):
    """Keep actual definitions, strip only explicit dependency/singleton wiring."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    body = []
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module in {
            "app.logs.audit", "app.agent.task_queue", "app.agent.scheduler",
        }:
            continue
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == remove_singleton
            for target in node.targets
        ):
            continue
        body.append(node)
    tree.body = body
    name = f"_jarvis_offline_{uuid.uuid4().hex}"
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__.update(injected or {})
    sys.modules[name] = module
    try:
        exec(compile(tree, str(path), "exec"), module.__dict__)
    finally:
        del sys.modules[name]
    return module


class TaskQueuePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jarvis-taskqueue-test-")
        self.addCleanup(self.temporary.cleanup)
        self.store = Path(self.temporary.name) / "tasks.json"
        self.audit = AuditRecorder()
        self.module = load_definitions(
            ROOT / "app/agent/task_queue.py", injected={"audit": self.audit},
            remove_singleton="task_queue",
        )
        self.queue = self.module.TaskQueue(self.store)

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def seed(self):
        task = self.run_async(self.queue.add_task("original"))
        self.audit.events.clear()
        return task

    def assert_no_temporary_files(self):
        self.assertEqual(list(self.store.parent.glob(".tasks.json.*.tmp")), [])

    def test_success_add_update_delete_reload_and_audit(self):
        task = self.run_async(self.queue.add_task("persist"))
        self.assertTrue(self.run_async(self.queue.update_status(
            task.task_id, "done", result={"ok": True}, error="detail",
        )))
        self.assertIs(self.run_async(self.queue.get_task(task.task_id)), task)
        self.assertEqual(task.status, "done")
        reloaded = self.module.TaskQueue(self.store)
        loaded = self.run_async(reloaded.get_task(task.task_id))
        self.assertEqual(loaded.result, {"ok": True})
        self.assertEqual(loaded.error, "detail")
        self.assertTrue(self.run_async(self.queue.delete_task(task.task_id)))
        self.assertEqual(json.loads(self.store.read_text()), [])
        self.assertEqual(self.run_async(self.module.TaskQueue(self.store).list_tasks()), [])
        self.assertEqual([event for event, _ in self.audit.events], [
            "task_queued", "task_status_update", "task_deleted",
        ])
        self.assertFalse(self.run_async(self.queue.delete_task("missing")))
        self.assertFalse(self.run_async(self.queue.update_status("missing", "done")))
        self.assert_no_temporary_files()

    def test_unpersisted_queue_does_not_serialize(self):
        queue = self.module.TaskQueue()
        task = self.run_async(queue.add_task("memory only"))
        result = {"opaque": object()}
        self.assertTrue(self.run_async(queue.update_status(task.task_id, "done", result)))
        self.assertIs(task.result, result)
        self.assertTrue(self.run_async(queue.delete_task(task.task_id)))
        self.assertFalse(self.store.exists())

    def test_failed_first_write_does_not_create_final_file(self):
        with mock.patch.object(self.module.os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                self.run_async(self.queue.add_task("new"))
        self.assertFalse(caught.exception.published)
        self.assertFalse(self.store.exists())
        self.assertEqual(self.run_async(self.queue.list_tasks()), [])
        self.assert_no_temporary_files()

    def test_prepublication_failures_restore_add_update_delete(self):
        for operation in ("add", "update", "delete"):
            for fault in ("mkdir", "create", "write", "flush", "file_sync", "replace"):
                with self.subTest(operation=operation, fault=fault):
                    self.queue = self.module.TaskQueue(self.store)
                    task = self.seed()
                    before = self.store.read_bytes()
                    original_tasks = self.run_async(self.queue.list_tasks())
                    self.audit.events.clear()
                    with self.inject_fault(fault):
                        with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                            self.mutate(operation, task)
                    self.assertFalse(caught.exception.published)
                    self.assertFalse(self.queue._persistence_uncertain)
                    self.assertEqual(self.store.read_bytes(), before)
                    self.assertEqual(self.run_async(self.queue.list_tasks()), original_tasks)
                    self.assertIs(self.run_async(self.queue.get_task(task.task_id)), task)
                    self.assertEqual((task.status, task.result, task.error), ("pending", None, None))
                    self.assertEqual([event for event, _ in self.audit.events], ["task_queue_save_error"])
                    self.assert_no_temporary_files()
                    # A failed attempt does not poison a retry before publication.
                    self.assertTrue(self.run_async(self.queue.update_status(task.task_id, "retry")))

    @contextlib.contextmanager
    def inject_fault(self, fault):
        error = OSError(errno.EIO, f"injected {fault}")
        if fault in {"write", "flush"}:
            original = self.module.tempfile.NamedTemporaryFile

            @contextlib.contextmanager
            def failing_file(*args, **kwargs):
                with original(*args, **kwargs) as opened:
                    wrapper = types.SimpleNamespace(
                        name=opened.name, write=opened.write, flush=opened.flush,
                        fileno=opened.fileno,
                    )
                    setattr(wrapper, fault, mock.Mock(side_effect=error))
                    yield wrapper

            with mock.patch.object(self.module.tempfile, "NamedTemporaryFile", failing_file):
                yield
            return
        targets = {
            "mkdir": (self.module.Path, "mkdir"),
            "create": (self.module.tempfile, "NamedTemporaryFile"),
            "file_sync": (self.module.os, "fsync"),
            "replace": (self.module.os, "replace"),
        }
        owner, name = targets[fault]
        with mock.patch.object(owner, name, side_effect=error):
            yield

    def mutate(self, operation, task):
        if operation == "add":
            return self.run_async(self.queue.add_task("new"))
        if operation == "update":
            return self.run_async(self.queue.update_status(
                task.task_id, "done", result={"changed": True}, error="changed",
            ))
        return self.run_async(self.queue.delete_task(task.task_id))

    def test_serialization_errors_restore_state_before_any_file_operation(self):
        task = self.seed()
        before = self.store.read_bytes()
        circular = {}
        circular["self"] = circular
        for value in (object(), circular):
            with self.subTest(value=type(value).__name__):
                self.audit.events.clear()
                with mock.patch.object(self.module.tempfile, "NamedTemporaryFile") as opened:
                    with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                        self.run_async(self.queue.update_status(task.task_id, "done", {"bad": value}))
                self.assertFalse(caught.exception.published)
                opened.assert_not_called()
                self.assertEqual(self.store.read_bytes(), before)
                self.assertEqual((task.status, task.result, task.error), ("pending", None, None))
                self.assertEqual([event for event, _ in self.audit.events], ["task_queue_save_error"])
                self.assert_no_temporary_files()

    def test_replace_receives_complete_synced_file_in_same_directory(self):
        self.seed()
        old = self.store.read_bytes()
        real_replace = self.module.os.replace
        real_fsync = self.module.os.fsync
        stages = []

        def synced(descriptor):
            stages.append("sync")
            return real_fsync(descriptor)

        def replace(source, destination):
            self.assertEqual(Path(source).parent, self.store.parent)
            self.assertEqual(Path(destination), self.store)
            self.assertEqual(self.store.read_bytes(), old)
            self.assertEqual(len(json.loads(Path(source).read_text())), 2)
            self.assertEqual(stages, ["sync"])
            stages.append("replace")
            return real_replace(source, destination)

        with mock.patch.object(self.module.os, "replace", side_effect=replace), \
                mock.patch.object(self.module.os, "fsync", side_effect=synced):
            self.run_async(self.queue.add_task("second"))
        expected = ["sync", "replace", "sync"] if os.name == "posix" else ["sync", "replace"]
        self.assertEqual(stages, expected)
        self.assert_no_temporary_files()

    def test_postpublication_failure_retains_visible_state_and_blocks_all_writes(self):
        for operation in ("add", "update", "delete"):
            with self.subTest(operation=operation):
                self.queue = self.module.TaskQueue(self.store)
                task = self.seed()
                with mock.patch.object(self.queue, "_sync_directory", side_effect=OSError(errno.EIO, "dir sync")):
                    with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                        self.mutate(operation, task)
                self.assertTrue(caught.exception.published)
                self.assertTrue(self.queue._persistence_uncertain)
                published = self.store.read_bytes()
                memory = [self.module.asdict(item) for item in self.run_async(self.queue.list_tasks())]
                self.assertEqual(json.loads(published), memory)
                self.assertEqual([event for event, _ in self.audit.events], ["task_queue_save_error"])
                self.assertTrue(self.audit.events[0][1]["durability_uncertain"])
                self.assert_no_temporary_files()
                if operation == "delete":
                    self.assertNotIn(task.task_id, self.queue._tasks)
                elif operation == "update":
                    self.assertEqual(task.status, "done")
                for blocked in ("add", "update", "delete"):
                    existing = next(iter(self.queue._tasks.values()), None)
                    if blocked != "add" and existing is None:
                        continue
                    with mock.patch.object(self.module.os, "replace") as replacement:
                        with self.assertRaises(self.module.TaskQueuePersistenceError) as refused:
                            self.mutate(blocked, existing)
                    self.assertFalse(refused.exception.published)
                    replacement.assert_not_called()
                    self.assertEqual(self.store.read_bytes(), published)
                    self.assertEqual([self.module.asdict(item) for item in self.queue._tasks.values()], memory)
                reviewed = self.module.TaskQueue(self.store)
                self.assertFalse(reviewed._persistence_uncertain)
                self.run_async(reviewed.add_task("after explicit reload"))

    @unittest.skipUnless(os.name == "posix", "directory sync is POSIX only")
    def test_directory_sync_distinguishes_unsupported_from_io_failure(self):
        task = self.seed()
        real_fsync = self.module.os.fsync
        for code in (errno.EINVAL, errno.ENOTSUP, errno.ENOSYS):
            calls = 0

            def sync(descriptor):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError(code, "unsupported directory sync")
                return real_fsync(descriptor)

            with self.subTest(errno=code), mock.patch.object(self.module.os, "fsync", side_effect=sync):
                self.assertTrue(self.run_async(self.queue.update_status(task.task_id, "done")))
            self.assertFalse(self.queue._persistence_uncertain)
            self.assertEqual(calls, 2)
        with mock.patch.object(self.module.os, "open", side_effect=OSError(errno.EIO, "open dir")):
            with self.assertRaises(OSError):
                self.queue._sync_directory()

    def test_audit_failure_cannot_mask_persistence_error_or_prevent_rollback(self):
        task = self.seed()
        before = self.store.read_bytes()
        with mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit unavailable")), \
                mock.patch.object(self.module.os, "replace", side_effect=OSError("replace")):
            with self.assertRaises(self.module.TaskQueuePersistenceError):
                self.mutate("update", task)
        self.assertEqual(task.status, "pending")
        self.assertEqual(self.store.read_bytes(), before)
        self.assert_no_temporary_files()

    def test_cleanup_failure_keeps_original_persistence_error(self):
        self.seed()
        with mock.patch.object(self.module.os, "replace", side_effect=OSError("original error")), \
                mock.patch.object(self.module.Path, "unlink", side_effect=OSError("cleanup error")):
            with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                self.run_async(self.queue.add_task("failed"))
        self.assertIn("original error", str(caught.exception))
        self.assertFalse(caught.exception.published)
        leftovers = list(self.store.parent.glob(".tasks.json.*.tmp"))
        self.assertEqual(len(leftovers), 1)
        for leftover in leftovers:
            leftover.unlink()

    def test_invalid_store_behavior_remains_unchanged_without_automatic_repair(self):
        for payload in ('{"bad": "shape"}', '{invalid', '[null, {}, {"goal": "missing ID"}]'):
            self.store.write_text(payload)
            queue = self.module.TaskQueue(self.store)
            self.assertEqual(self.run_async(queue.list_tasks()), [])
            self.assertEqual(self.store.read_text(), payload)

    def test_concurrent_local_mutations_remain_serialized_and_reloadable(self):
        async def work():
            tasks = await asyncio.gather(*(self.queue.add_task(f"task {i}") for i in range(40)))
            await asyncio.gather(*(
                self.queue.update_status(task.task_id, "done", {"number": i})
                for i, task in enumerate(tasks)
            ))
            await asyncio.gather(*(self.queue.delete_task(task.task_id) for task in tasks[::2]))
            return tasks

        tasks = self.run_async(work())
        reloaded = self.module.TaskQueue(self.store)
        remaining = self.run_async(reloaded.list_tasks("done"))
        self.assertEqual(len(remaining), 20)
        self.assertEqual({task.task_id for task in remaining}, {task.task_id for task in tasks[1::2]})
        self.assert_no_temporary_files()

    def test_existing_agent_stub_regressions_in_exclusive_temporary_cwd(self):
        scheduler = load_definitions(
            ROOT / "app/agent/scheduler.py",
            injected={"audit": self.audit, "task_queue": self.module.TaskQueue()},
            remove_singleton="scheduler",
        )
        existing = load_definitions(
            ROOT / "tests/test_agent_stubs.py", injected={
                "TaskQueue": self.module.TaskQueue, "AgentTask": self.module.AgentTask,
                "task_queue": self.module.TaskQueue(),
                "Scheduler": scheduler.Scheduler, "ScheduledJob": scheduler.ScheduledJob,
            },
        )
        functions = sorted(
            (name, value) for name, value in vars(existing).items()
            if name.startswith("test_") and callable(value)
        )
        self.assertEqual(len(functions), 10)
        previous = Path.cwd()
        try:
            os.chdir(self.temporary.name)
            for name, function in functions:
                with self.subTest(existing=name):
                    function()
        finally:
            os.chdir(previous)


if __name__ == "__main__":
    unittest.main(verbosity=2)
