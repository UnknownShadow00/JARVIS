"""Offline collision/quarantine regressions; no live application imports."""
from __future__ import annotations

import asyncio
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "_taskqueue_isolated_helpers", ROOT / "tests/test_task_queue_persistence.py",
)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


class TaskQueueStoreSafetyTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jarvis-queue-safety-")
        self.addCleanup(self.temporary.cleanup)
        self.store = Path(self.temporary.name) / "tasks.json"
        self.audit = helpers.AuditRecorder()
        self.module = helpers.load_definitions(
            ROOT / "app/agent/task_queue.py", injected={"audit": self.audit},
            remove_singleton="task_queue",
        )

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def seed(self):
        queue = self.module.TaskQueue(self.store)
        with mock.patch.object(self.module.uuid, "uuid4", return_value="aaaaaaaa-uuid"):
            task = self.run_async(queue.add_task("original"))
        self.audit.events.clear()
        return queue, task

    def test_collision_retries_without_overwriting_original(self):
        queue, original = self.seed()
        with mock.patch.object(self.module.uuid, "uuid4", side_effect=[
            "aaaaaaaa-collision", "aaaaaaaa-again", "bbbbbbbb-new",
        ]) as generated:
            added = self.run_async(queue.add_task("second"))
        self.assertEqual(generated.call_count, 3)
        self.assertEqual(added.task_id, "bbbbbbbb")
        self.assertIs(self.run_async(queue.get_task(original.task_id)), original)
        self.assertEqual(len(json.loads(self.store.read_text())), 2)

    def test_exhausted_collisions_are_bounded_and_preserve_all_state(self):
        queue, original = self.seed()
        before = self.store.read_bytes()
        with mock.patch.object(self.module.uuid, "uuid4", return_value="aaaaaaaa-collision") as generated:
            with self.assertRaises(RuntimeError) as caught:
                self.run_async(queue.add_task("must not replace"))
        self.assertEqual(type(caught.exception).__name__, "TaskQueueIdentifierError")
        self.assertEqual(generated.call_count, 32)
        self.assertEqual(self.store.read_bytes(), before)
        self.assertEqual(self.run_async(queue.list_tasks()), [original])
        self.assertEqual(self.audit.events, [])
        self.assertEqual(list(self.store.parent.glob(".tasks.json.*.tmp")), [])

    def test_last_allowed_identifier_attempt_can_succeed(self):
        queue, original = self.seed()
        with mock.patch.object(self.module.uuid, "uuid4", side_effect=[
            *(["aaaaaaaa-collision"] * 31), "bbbbbbbb-new",
        ]) as generated:
            added = self.run_async(queue.add_task("last try"))
        self.assertEqual(generated.call_count, 32)
        self.assertEqual(added.task_id, "bbbbbbbb")
        self.assertIs(self.run_async(queue.get_task("aaaaaaaa")), original)

    def test_concurrent_collisions_keep_all_accepted_tasks(self):
        queue, _ = self.seed()

        async def work():
            return await asyncio.gather(queue.add_task("second"), queue.add_task("third"))

        with mock.patch.object(self.module.uuid, "uuid4", side_effect=[
            "aaaaaaaa-existing", "bbbbbbbb-second", "bbbbbbbb-collision", "cccccccc-third",
        ]):
            added = self.run_async(work())
        self.assertEqual([task.task_id for task in added], ["bbbbbbbb", "cccccccc"])
        self.assertEqual(len(json.loads(self.store.read_text())), 3)

    def test_malformed_stores_block_add_without_replacing_evidence(self):
        valid = {"task_id": "aaaaaaaa", "goal": "retain"}
        cases = [
            b"{invalid", b'{"bad":"shape"}', b"[null]", b"[{}]", b"\xff",
            json.dumps([valid, {"goal": "missing ID"}]).encode(),
            json.dumps([valid, {**valid, "goal": "duplicate ID"}]).encode(),
            json.dumps([{**valid, "result": ["discarded"]}]).encode(),
            json.dumps([{**valid, "error": {"discarded": True}}]).encode(),
            json.dumps([{**valid, "extra": "discarded"}]).encode(),
            json.dumps([{**valid, "status": 42}]).encode(),
            json.dumps([{**valid, "created_at": 42}]).encode(),
            json.dumps([{**valid, "task_id": 123}]).encode(),
            json.dumps([{**valid, "goal": " "}]).encode(),
            b'[{"task_id":"aaaaaaaa","goal":"old","goal":"new"}]',
            b'[{"task_id":"aaaaaaaa","goal":"retain","result":{"x":NaN}}]',
        ]
        for index, payload in enumerate(cases):
            with self.subTest(index=index):
                self.store.write_bytes(payload)
                queue = self.module.TaskQueue(self.store)
                self.audit.events.clear()
                before_tasks = self.run_async(queue.list_tasks())
                with mock.patch.object(self.module.tempfile, "NamedTemporaryFile") as opened:
                    with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                        self.run_async(queue.add_task("must not replace evidence"))
                self.assertFalse(caught.exception.published)
                opened.assert_not_called()
                self.assertEqual(self.store.read_bytes(), payload)
                self.assertEqual(self.run_async(queue.list_tasks()), before_tasks)
                self.assertNotIn("task_queued", [event for event, _ in self.audit.events])

    def test_partial_store_blocks_update_and_delete_and_restores_object(self):
        payload = b'[{"task_id":"aaaaaaaa","goal":"retain"},null]'
        self.store.write_bytes(payload)
        queue = self.module.TaskQueue(self.store)
        task = self.run_async(queue.get_task("aaaaaaaa"))
        for operation in ("update", "delete"):
            with self.subTest(operation=operation):
                with self.assertRaises(self.module.TaskQueuePersistenceError):
                    if operation == "update":
                        self.run_async(queue.update_status(task.task_id, "done", {"changed": True}))
                    else:
                        self.run_async(queue.delete_task(task.task_id))
                self.assertEqual(self.store.read_bytes(), payload)
                self.assertIs(self.run_async(queue.get_task(task.task_id)), task)
                self.assertEqual((task.status, task.result, task.error), ("pending", None, None))

    def test_load_io_failure_cannot_be_hidden_by_next_write(self):
        self.store.write_text("[]")
        for fault in (PermissionError("denied"), OSError("I/O failed")):
            with self.subTest(fault=type(fault).__name__):
                with mock.patch.object(self.module.TaskQueue, "_read_store", side_effect=fault):
                    queue = self.module.TaskQueue(self.store)
                with self.assertRaises(self.module.TaskQueuePersistenceError):
                    self.run_async(queue.add_task("must not overwrite unread store"))
                self.assertEqual(self.store.read_text(), "[]")

    def test_nonfile_store_is_blocked_before_temporary_creation(self):
        self.store.mkdir()
        queue = self.module.TaskQueue(self.store)
        with mock.patch.object(self.module.tempfile, "NamedTemporaryFile") as opened:
            with self.assertRaises(self.module.TaskQueuePersistenceError):
                self.run_async(queue.add_task("must not write"))
        opened.assert_not_called()
        self.assertTrue(self.store.is_dir())

    def test_load_error_reporting_failure_still_blocks_writes(self):
        payload = "{invalid"
        self.store.write_text(payload)
        with mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit unavailable")):
            queue = self.module.TaskQueue(self.store)
        with self.assertRaises(self.module.TaskQueuePersistenceError):
            self.run_async(queue.add_task("must not write"))
        self.assertEqual(self.store.read_text(), payload)

    def test_compatible_minimal_store_and_empty_and_absent_stores_accept_writes(self):
        for payload in (None, "[]", '[{"task_id":"legacy-id","goal":"legacy"}]'):
            with self.subTest(payload=payload):
                self.store.unlink(missing_ok=True)
                if payload is not None:
                    self.store.write_text(payload)
                queue = self.module.TaskQueue(self.store)
                self.run_async(queue.add_task("new"))
                self.assertEqual(len(json.loads(self.store.read_text())), 2 if "legacy" in (payload or "") else 1)

    def test_whitespace_goals_and_empty_status_roundtrip_with_legacy_record(self):
        self.store.write_text('[{"task_id":"legacy","goal":" legacy "}]')
        queue = self.module.TaskQueue(self.store)
        task = self.run_async(queue.add_task(" retain "))
        self.run_async(queue.update_status(task.task_id, "", {"nested": {"number": 1.5}}))
        reloaded = self.module.TaskQueue(self.store)
        original = self.run_async(reloaded.get_task(task.task_id))
        self.assertEqual((original.goal, original.status), (" retain ", ""))
        self.assertEqual(self.run_async(reloaded.get_task("legacy")).goal, " legacy ")
        self.assertTrue(self.run_async(reloaded.update_status(task.task_id, "done")))
        self.assertIsNone(reloaded._load_error)

    def test_nonfinite_result_rejected_before_publication_with_rollback(self):
        queue, task = self.seed()
        before = self.store.read_bytes()
        for value in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(value=str(value)):
                with mock.patch.object(self.module.tempfile, "NamedTemporaryFile") as opened:
                    with self.assertRaises(self.module.TaskQueuePersistenceError) as caught:
                        self.run_async(queue.update_status(task.task_id, "done", {"nested": [value]}))
                self.assertFalse(caught.exception.published)
                opened.assert_not_called()
                self.assertEqual((task.status, task.result), ("pending", None))
                self.assertEqual(self.store.read_bytes(), before)
        self.run_async(queue.update_status(task.task_id, "done", {"finite": 1.5}))
        reloaded = self.module.TaskQueue(self.store)
        self.assertIsNone(reloaded._load_error)
        self.assertEqual(self.run_async(reloaded.get_task(task.task_id)).result, {"finite": 1.5})
        self.assertTrue(self.run_async(reloaded.update_status(task.task_id, "pending")))

    def test_unreloadable_new_task_rejected_before_publication(self):
        queue, original = self.seed()
        before = self.store.read_bytes()
        for goal in ("", "  ", 123):
            with self.subTest(goal=goal):
                with self.assertRaises(self.module.TaskQueuePersistenceError):
                    self.run_async(queue.add_task(goal))
                self.assertEqual(self.store.read_bytes(), before)
                self.assertEqual(self.run_async(queue.list_tasks()), [original])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "FIFO requires POSIX")
    def test_fifo_is_rejected_without_blocking(self):
        os.mkfifo(self.store)
        # A subprocess deadline bounds the regression even if a future loader
        # mistakenly replaces the descriptor checks with a blocking read.
        program = '''import importlib.util,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("helpers",sys.argv[1])
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
q=m.load_definitions(Path(sys.argv[2]),injected={"audit":m.AuditRecorder()},remove_singleton="task_queue")
queue=q.TaskQueue(Path(sys.argv[3])); assert queue._load_error
'''
        subprocess.run([
            sys.executable, "-B", "-c", program, str(ROOT / "tests/test_task_queue_persistence.py"),
            self.module.__file__, str(self.store),
        ], check=True, timeout=5, capture_output=True, text=True)

    def test_path_swap_to_fifo_is_rejected_using_open_descriptor(self):
        self.store.write_text("[]")
        fifo = self.store.with_suffix(".fifo")
        os.mkfifo(fifo)
        real_open = self.module.os.open

        def swap(path, flags, *args, **kwargs):
            if Path(path) == self.store:
                os.replace(fifo, self.store)
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(self.module.os, "open", side_effect=swap):
            queue = self.module.TaskQueue(self.store)
        self.assertIsNotNone(queue._load_error)
        with self.assertRaises(self.module.TaskQueuePersistenceError):
            self.run_async(queue.add_task("must not write"))

    def test_store_repair_requires_explicit_new_instance(self):
        self.store.write_text("{invalid")
        blocked = self.module.TaskQueue(self.store)
        # Simulate an explicit operator repair in this disposable fixture only.
        self.store.write_text("[]")
        with self.assertRaises(self.module.TaskQueuePersistenceError):
            self.run_async(blocked.add_task("old instance stays blocked"))
        self.assertEqual(self.store.read_text(), "[]")
        reviewed = self.module.TaskQueue(self.store)
        self.run_async(reviewed.add_task("explicit reload"))
        self.assertEqual(len(json.loads(self.store.read_text())), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
