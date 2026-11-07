"""Actual caller definitions and actual queue in fresh files, no application import."""
from __future__ import annotations

import ast
import asyncio
from dataclasses import asdict
from datetime import UTC, datetime
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "app"
SOURCE_OVERRIDES = {}
spec = importlib.util.spec_from_file_location("_queue_call_helpers", ROOT / "tests/test_task_queue_persistence.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


class ResponseRecorder:
    def __init__(self, *, status_code, content):
        self.status_code = status_code
        self.content = content


def server_definitions(queue, queue_module):
    names = {"create_task", "list_tasks", "get_task", "update_task", "delete_task", "_task_write_error"}
    path = SOURCE_OVERRIDES.get("server.py", SOURCE_ROOT / "server.py")
    parsed = ast.parse(path.read_text(), filename=str(path))
    selected = []
    for node in parsed.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            node.decorator_list = []
            selected.append(node)
    tree = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0), *selected], type_ignores=[])
    module = types.ModuleType("offline_task_api")
    module.__dict__.update({
        "task_queue": queue, "asdict": asdict, "JSONResponse": ResponseRecorder,
        "TaskQueuePersistenceError": queue_module.TaskQueuePersistenceError,
        "TaskQueueIdentifierError": queue_module.TaskQueueIdentifierError,
        "TaskQueueAuditError": getattr(queue_module, "TaskQueueAuditError", type("AbsentAuditError", (RuntimeError,), {})),
    })
    exec(compile(ast.fix_missing_locations(tree), str(path), "exec"), module.__dict__)
    return module


class TaskQueueCallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="jarvis-queue-callers-")
        self.addCleanup(self.temporary.cleanup)
        self.store = Path(self.temporary.name) / "tasks.json"
        self.audit = helpers.AuditRecorder()
        self.queue_module = helpers.load_definitions(
            SOURCE_OVERRIDES.get("agent/task_queue.py", SOURCE_ROOT / "agent/task_queue.py"), injected={"audit": self.audit},
            remove_singleton="task_queue",
        )
        self.queue = self.queue_module.TaskQueue(self.store)
        self.api = server_definitions(self.queue, self.queue_module)
        self.scheduler = helpers.load_definitions(
            SOURCE_OVERRIDES.get("agent/scheduler.py", SOURCE_ROOT / "agent/scheduler.py"), injected={
                "audit": self.audit, "task_queue": self.queue,
                "TaskQueuePersistenceError": self.queue_module.TaskQueuePersistenceError,
                "TaskQueueIdentifierError": self.queue_module.TaskQueueIdentifierError,
                "TaskQueueAuditError": getattr(self.queue_module, "TaskQueueAuditError", type("AbsentAuditError", (RuntimeError,), {})),
            }, remove_singleton="scheduler",
        )

    def run_async(self, coroutine):
        return asyncio.run(coroutine)

    def seed(self):
        task = self.run_async(self.queue.add_task("original"))
        self.audit.events.clear()
        return task

    def api_mutation(self, operation, task=None):
        if operation == "create":
            return self.run_async(self.api.create_task(types.SimpleNamespace(goal="new task")))
        if operation == "update":
            return self.run_async(self.api.update_task(task.task_id, types.SimpleNamespace(
                status="done", result={"ok": True}, error=None,
            )))
        return self.run_async(self.api.delete_task(task.task_id))

    def assert_failure_response(self, response, *, published, operation, task_id):
        self.assertIsInstance(response, ResponseRecorder)
        self.assertEqual(response.status_code, 409 if published else 503)
        self.assertEqual(response.content, {
            "error": "task_queue_write_uncertain" if published else "task_queue_write_failed",
            "operation": operation, "task_id": task_id,
            "publication": "published_durability_unknown" if published else "not_published",
            "automatic_retry": False, "reconcile_required": published,
        })
        self.assertNotIn(str(self.store), json.dumps(response.content))

    def test_api_prepublication_failures_return_explicit_outcomes_without_retry(self):
        for operation in ("create", "update", "delete"):
            with self.subTest(operation=operation):
                self.queue = self.queue_module.TaskQueue(self.store)
                self.api.task_queue = self.queue
                task = self.seed()
                before = self.store.read_bytes()
                with mock.patch.object(self.queue_module.os, "replace", side_effect=OSError("private path detail")) as replaced:
                    response = self.api_mutation(operation, task)
                self.assertEqual(replaced.call_count, 1)
                task_id = response.content["task_id"]
                self.assertEqual(len(task_id), 8)
                if operation != "create":
                    self.assertEqual(task_id, task.task_id)
                self.assert_failure_response(response, published=False, operation=operation, task_id=task_id)
                self.assertEqual(self.store.read_bytes(), before)
                self.assertFalse(any(event in {"task_queued", "task_status_update", "task_deleted"} for event, _ in self.audit.events))

    def test_api_postpublication_uncertainty_returns_reconciliation_id_and_no_retry(self):
        for operation in ("create", "update", "delete"):
            with self.subTest(operation=operation):
                self.queue = self.queue_module.TaskQueue(self.store)
                self.api.task_queue = self.queue
                task = self.seed()
                with mock.patch.object(self.queue, "_sync_directory", side_effect=OSError("uncertain")) as synced:
                    response = self.api_mutation(operation, task)
                self.assertEqual(synced.call_count, 1)
                task_id = response.content["task_id"]
                self.assert_failure_response(response, published=True, operation=operation, task_id=task_id)
                records = {record["task_id"]: record for record in json.loads(self.store.read_text())}
                if operation == "delete":
                    self.assertNotIn(task_id, records)
                else:
                    self.assertIn(task_id, records)
                before = self.store.read_bytes()
                repeated = self.api_mutation(operation, task)
                if operation == "delete":
                    self.assertEqual(repeated, {"deleted": False})
                else:
                    self.assert_failure_response(repeated, published=False, operation=operation, task_id=repeated.content["task_id"])
                self.assertEqual(self.store.read_bytes(), before)

    def test_queue_errors_bind_operation_and_identifier(self):
        task = self.seed()
        calls = {
            "create": lambda: self.queue.add_task("new"),
            "update": lambda: self.queue.update_status(task.task_id, "done"),
            "delete": lambda: self.queue.delete_task(task.task_id),
        }
        for operation, invoke in calls.items():
            with self.subTest(operation=operation):
                with mock.patch.object(self.queue, "_save", side_effect=self.queue_module.TaskQueuePersistenceError("failure")):
                    with self.assertRaises(self.queue_module.TaskQueuePersistenceError) as caught:
                        self.run_async(invoke())
                self.assertEqual(caught.exception.operation, operation)
                self.assertEqual(len(caught.exception.task_id), 8)
                if operation != "create":
                    self.assertEqual(caught.exception.task_id, task.task_id)

    def test_api_identifier_exhaustion_is_explicit_and_keeps_original(self):
        task = self.seed()
        before = self.store.read_bytes()
        with mock.patch.object(self.queue_module.uuid, "uuid4", return_value=task.task_id + "-collision"):
            response = self.api_mutation("create")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.content["error"], "task_queue_identifier_exhausted")
        self.assertFalse(response.content["automatic_retry"])
        self.assertEqual(self.store.read_bytes(), before)

    def test_api_quarantined_load_is_not_reported_as_success(self):
        damaged = b'{invalid'
        self.store.write_bytes(damaged)
        self.queue = self.queue_module.TaskQueue(self.store)
        self.api.task_queue = self.queue
        response = self.api_mutation("create")
        self.assert_failure_response(response, published=False, operation="create", task_id=response.content["task_id"])
        self.assertEqual(self.store.read_bytes(), damaged)

    def test_successful_api_and_missing_task_responses_remain_compatible(self):
        created = self.api_mutation("create")
        task = self.run_async(self.queue.get_task(created["task_id"]))
        self.assertEqual(created, asdict(task))
        self.assertEqual(self.api_mutation("update", task)["status"], "done")
        self.assertEqual(self.api_mutation("delete", task), {"deleted": True})
        self.assertEqual(self.api_mutation("delete", task), {"deleted": False})
        self.assertEqual(self.api_mutation("update", task).status_code, 404)

    def test_scheduler_failed_enqueue_never_updates_last_run_or_emits_success(self):
        for published in (False, True):
            with self.subTest(published=published):
                queue = self.queue_module.TaskQueue(self.store)
                self.scheduler.task_queue = queue
                job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal", last_run="previous success")
                self.audit.events.clear()
                owner, name = (queue, "_sync_directory") if published else (self.queue_module.os, "replace")
                with mock.patch.object(owner, name, side_effect=OSError("injected")) as failed:
                    with self.assertRaises(self.queue_module.TaskQueuePersistenceError):
                        self.run_async(self.scheduler._run_job(job))
                self.assertEqual(failed.call_count, 1)
                self.assertEqual(job.last_run, "previous success")
                events = [event for event, _ in self.audit.events]
                self.assertNotIn("job_executed", events)
                self.assertIn("job_enqueue_failed", events)
                failure = next(details for event, details in self.audit.events if event == "job_enqueue_failed")
                self.assertEqual(failure["published"], published)
                self.assertFalse(failure["automatic_retry"])
                self.assertEqual(len(failure["task_id"]), 8)

    def test_scheduler_success_marks_enqueue_only_after_return(self):
        job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal")
        original_add = self.queue.add_task

        async def checked(goal):
            self.assertIsNone(job.last_run)
            return await original_add(goal)

        with mock.patch.object(self.queue, "add_task", side_effect=checked) as added:
            self.run_async(self.scheduler._run_job(job))
        self.assertEqual(added.call_count, 1)
        datetime.fromisoformat(job.last_run)
        event = next(details for event, details in self.audit.events if event == "job_executed")
        self.assertEqual(event["outcome"], "enqueued_only")
        self.assertEqual(len(event["task_id"]), 8)

    def test_scheduler_identifier_exhaustion_does_not_update_success_or_retry(self):
        task = self.seed()
        job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal", last_run="previous")
        before = self.store.read_bytes()
        with mock.patch.object(self.queue_module.uuid, "uuid4", return_value=task.task_id + "-collision") as generated:
            with self.assertRaises(self.queue_module.TaskQueueIdentifierError):
                self.run_async(self.scheduler._run_job(job))
        self.assertEqual(generated.call_count, 32)
        self.assertEqual(job.last_run, "previous")
        self.assertEqual(self.store.read_bytes(), before)
        self.assertNotIn("job_executed", [event for event, _ in self.audit.events])

    def test_scheduler_failure_audit_cannot_mask_original_queue_error(self):
        job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal")
        original = self.queue_module.TaskQueuePersistenceError("original failure")
        original.task_id = "aaaaaaaa"
        with mock.patch.object(self.queue, "add_task", side_effect=original) as added, \
                mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit failure")):
            with self.assertRaises(self.queue_module.TaskQueuePersistenceError) as caught:
                self.run_async(self.scheduler._run_job(job))
        self.assertIs(caught.exception, original)
        self.assertEqual(added.call_count, 1)
        self.assertIsNone(job.last_run)

    def test_api_postcommit_audit_failures_report_applied_state_without_repeating(self):
        for persistent in (False, True):
            for operation in ("create", "update", "delete"):
                with self.subTest(persistent=persistent, operation=operation):
                    self.queue = self.queue_module.TaskQueue(self.store if persistent else None)
                    self.api.task_queue = self.queue
                    task = self.seed()
                    with mock.patch.object(self.audit, "log", side_effect=RuntimeError("private audit detail")) as reporting:
                        response = self.api_mutation(operation, task)
                    self.assertEqual(reporting.call_count, 1)
                    self.assertEqual(response.status_code, 409)
                    self.assertEqual(response.content["error"], "task_queue_audit_failed")
                    self.assertEqual(response.content["publication"], "published_audit_failed" if persistent else "memory_applied_audit_failed")
                    self.assertTrue(response.content["reconcile_required"])
                    self.assertFalse(response.content["automatic_retry"])
                    identifier = response.content["task_id"]
                    self.assertEqual(len(identifier), 8)
                    present = self.run_async(self.queue.get_task(identifier))
                    if operation == "delete":
                        self.assertIsNone(present)
                    else:
                        self.assertIsNotNone(present)
                    self.assertNotIn("private audit detail", json.dumps(response.content))
                    if persistent:
                        records = {r["task_id"]: r for r in json.loads(self.store.read_text())}
                        self.assertEqual(identifier in records, operation != "delete")

    def test_scheduler_postcommit_audit_failure_retains_enqueue_and_original_timestamp(self):
        job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal", last_run="previous")
        with mock.patch.object(self.audit, "log", side_effect=RuntimeError("audit unavailable")), \
                mock.patch.object(self.queue, "add_task", wraps=self.queue.add_task) as added:
            with self.assertRaises(self.queue_module.TaskQueueAuditError) as caught:
                self.run_async(self.scheduler._run_job(job))
        self.assertEqual(added.call_count, 1)
        self.assertEqual(job.last_run, "previous")
        records = json.loads(self.store.read_text())
        self.assertEqual([r["task_id"] for r in records], [caught.exception.task_id])
        self.assertTrue(caught.exception.published)

    def test_scheduler_success_event_audit_failure_carries_reconciliation_id(self):
        job = self.scheduler.ScheduledJob("job", "inspection", "* * * * *", "goal")
        real_log = self.audit.log

        def reporting(event, details):
            if event == "job_executed":
                raise RuntimeError("job audit failed")
            return real_log(event, details)

        with mock.patch.object(self.audit, "log", side_effect=reporting), \
                mock.patch.object(self.queue, "add_task", wraps=self.queue.add_task) as added:
            with self.assertRaises(self.queue_module.TaskQueueAuditError) as caught:
                self.run_async(self.scheduler._run_job(job))
        self.assertEqual(added.call_count, 1)
        self.assertIsNotNone(job.last_run)
        self.assertIn(caught.exception.task_id, str(caught.exception))
        records = json.loads(self.store.read_text())
        self.assertEqual([r["task_id"] for r in records], [caught.exception.task_id])


if __name__ == "__main__":
    unittest.main(verbosity=2)
