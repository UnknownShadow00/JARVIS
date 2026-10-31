from __future__ import annotations

import asyncio
import errno
import json
import os
import stat
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_STORE = PROJECT_ROOT / "data" / "agent_tasks.json"
TASK_ID_ATTEMPTS = 32


class TaskQueueIdentifierError(RuntimeError):
    """No unused task identifier was generated within the bounded retry budget."""


class TaskQueueAuditError(RuntimeError):
    """The mutation completed, but its success audit could not be submitted."""

    def __init__(self, *, operation: str, task_id: str, published: bool) -> None:
        super().__init__(f"Task {task_id} {operation} applied but success audit reporting failed; reconcile before retry.")
        self.operation = operation
        self.task_id = task_id
        self.published = published


class TaskQueuePersistenceError(RuntimeError):
    """A write failed; ``published`` means the replacement may already be visible."""

    def __init__(self, message: str, *, published: bool = False) -> None:
        super().__init__(message)
        self.published = published
        self.operation: str | None = None
        self.task_id: str | None = None


@dataclass
class AgentTask:
    task_id: str
    goal: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    result: dict | None = None
    error: str | None = None


class TaskQueue:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._tasks: dict[str, AgentTask] = {}
        self._lock: asyncio.Lock | None = None
        self._storage_path = Path(storage_path) if storage_path is not None else None
        self._persistence_uncertain = False
        self._load_error: str | None = None
        self._load()

    async def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def add_task(self, goal: str) -> AgentTask:
        lock = await self._get_lock()
        async with lock:
            for _ in range(TASK_ID_ATTEMPTS):
                task_id = str(uuid.uuid4())[:8]
                if task_id not in self._tasks:
                    break
            else:
                raise TaskQueueIdentifierError(
                    f"No unused task identifier after {TASK_ID_ATTEMPTS} attempts."
                )
            task = AgentTask(task_id=task_id, goal=goal)
            previous = self._tasks.copy()
            self._tasks[task_id] = task
            try:
                self._save()
            except TaskQueuePersistenceError as exc:
                exc.operation, exc.task_id = "create", task_id
                if not exc.published:
                    self._tasks = previous
                raise
        self._audit_mutation("create", "task_queued", {"task_id": task_id, "goal": goal})
        return task

    async def get_task(self, task_id: str) -> AgentTask | None:
        lock = await self._get_lock()
        async with lock:
            return self._tasks.get(task_id)

    async def list_tasks(self, status: str | None = None) -> list[AgentTask]:
        lock = await self._get_lock()
        async with lock:
            tasks = list(self._tasks.values())
        if status is None:
            return tasks
        return [task for task in tasks if task.status == status]

    async def update_status(
        self,
        task_id: str,
        status: str,
        result: dict | None = None,
        error: str | None = None,
    ) -> bool:
        lock = await self._get_lock()
        async with lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            previous = (task.status, task.result, task.error)
            task.status = status
            task.result = result
            task.error = error
            try:
                self._save()
            except TaskQueuePersistenceError as exc:
                exc.operation, exc.task_id = "update", task_id
                if not exc.published:
                    task.status, task.result, task.error = previous
                raise
        self._audit_mutation("update", "task_status_update", {"task_id": task_id, "status": status})
        return True

    async def delete_task(self, task_id: str) -> bool:
        lock = await self._get_lock()
        async with lock:
            if task_id not in self._tasks:
                return False
            previous = self._tasks.copy()
            del self._tasks[task_id]
            try:
                self._save()
            except TaskQueuePersistenceError as exc:
                exc.operation, exc.task_id = "delete", task_id
                if not exc.published:
                    self._tasks = previous
                raise
        self._audit_mutation("delete", "task_deleted", {"task_id": task_id})
        return True

    def _audit_mutation(self, operation: str, event: str, details: dict[str, Any]) -> None:
        try:
            audit.log(event, details)
        except Exception as exc:
            # Publication already completed. Never roll back or issue it again.
            raise TaskQueueAuditError(
                operation=operation, task_id=details["task_id"],
                published=self._storage_path is not None,
            ) from exc

    def _load(self) -> None:
        if self._storage_path is None:
            return
        try:
            raw = json.loads(
                self._read_store(),
                object_pairs_hook=self._unique_object,
                parse_constant=self._reject_constant,
            )
        except FileNotFoundError:
            # A dangling link is an existing invalid store, not a new queue.
            if self._storage_path.is_symlink():
                self._block_loaded_store("Store is a dangling symbolic link.")
            return
        except (OSError, ValueError) as exc:
            self._block_loaded_store(f"Store could not be loaded ({type(exc).__name__}).")
            return
        if not isinstance(raw, list):
            self._block_loaded_store("Store is not a task list.")
            return
        tasks: dict[str, AgentTask] = {}
        for item in raw:
            if not isinstance(item, dict):
                self._block_loaded_store("Store contains a non-object record.")
                continue
            task = self._task_from_dict(item)
            if task is None:
                self._block_loaded_store("Store contains an incomplete record.")
                continue
            if task.task_id in tasks or not self._record_is_lossless(item):
                self._block_loaded_store("Store contains a duplicate or lossy record.")
            tasks[task.task_id] = task
        self._tasks = tasks

    def _read_store(self) -> str:
        # Check before opening devices, and recheck the opened descriptor against
        # a concurrent path replacement. O_NONBLOCK prevents a FIFO swap hanging.
        if not stat.S_ISREG(self._storage_path.stat().st_mode):
            raise ValueError("Store is not a regular file.")
        descriptor = os.open(self._storage_path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("Store changed to a non-regular file.")
            with os.fdopen(descriptor, "r", encoding="utf-8", closefd=False) as opened:
                return opened.read()
        finally:
            os.close(descriptor)

    def _block_loaded_store(self, reason: str) -> None:
        """Retain diagnostic reads but never automatically repair/overwrite evidence."""
        if self._load_error is not None:
            return
        self._load_error = reason
        try:
            audit.log("task_queue_load_error", {"path": str(self._storage_path), "error": reason})
        except Exception:
            pass  # A reporting failure must not remove the write block.

    @staticmethod
    def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        record: dict[str, Any] = {}
        for key, value in pairs:
            if key in record:
                raise ValueError("Duplicate JSON object key.")
            record[key] = value
        return record

    @staticmethod
    def _reject_constant(value: str) -> None:
        raise ValueError("Non-finite JSON constant.")

    @staticmethod
    def _record_is_lossless(item: dict[str, Any]) -> bool:
        if item.keys() - {"task_id", "goal", "status", "created_at", "result", "error"}:
            return False
        for name in ("task_id", "goal"):
            value = item.get(name)
            if not isinstance(value, str) or not value.strip():
                return False
        for name in ("status", "created_at"):
            if name in item and not isinstance(item[name], str):
                return False
        return (
            (item.get("result") is None or isinstance(item["result"], dict))
            and (item.get("error") is None or isinstance(item["error"], str))
        )

    def _save(self) -> None:
        if self._storage_path is None:
            return
        if self._load_error is not None:
            raise TaskQueuePersistenceError(
                "Task queue writes are blocked after a load error; preserve and "
                "review the original store before explicitly loading a repaired copy."
            )
        if self._persistence_uncertain:
            raise TaskQueuePersistenceError(
                "Task queue writes are blocked after an uncertain publication; "
                "review the store and create a new TaskQueue instance."
            )
        temporary_path: Path | None = None
        published = False
        try:
            payload = [asdict(task) for task in self._tasks.values()]
            if any(not self._record_is_lossless(record) for record in payload):
                raise ValueError("Task record cannot be reloaded without data loss.")
            serialized = json.dumps(payload, indent=2, allow_nan=False)
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self._storage_path.parent,
                prefix=f".{self._storage_path.name}.", suffix=".tmp", delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                temporary_file.write(serialized)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())
            os.replace(temporary_path, self._storage_path)
            published = True
            temporary_path = None
            self._sync_directory()
        except Exception as exc:
            # After replace, keep the published in-memory state and require review.
            # Rolling it back or retrying could overwrite a change already visible.
            self._persistence_uncertain = published
            try:
                audit.log("task_queue_save_error", {
                    "path": str(self._storage_path), "error": str(exc),
                    "published": published, "durability_uncertain": published,
                })
            except Exception:
                pass  # Reporting must not hide the persistence failure or prevent rollback.
            raise TaskQueuePersistenceError(
                f"Task queue persistence failed for {self._storage_path}: {exc}",
                published=published,
            ) from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    # Do not hide the persistence failure if cleanup also fails.
                    pass

    def _sync_directory(self) -> None:
        """Sync the replacement directory on POSIX where the filesystem supports it."""
        if os.name != "posix":
            return
        unsupported = {errno.EINVAL, errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS}
        try:
            descriptor = os.open(
                self._storage_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
            )
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except OSError as exc:
            if exc.errno not in unsupported:
                raise

    def _task_from_dict(self, item: dict[str, Any]) -> AgentTask | None:
        task_id = str(item.get("task_id") or "")
        goal = str(item.get("goal") or "")
        if not task_id.strip() or not goal.strip():
            return None
        result = item.get("result")
        return AgentTask(
            task_id=task_id,
            goal=goal,
            status=str(item["status"]) if isinstance(item.get("status"), str) else str(item.get("status") or "pending"),
            created_at=str(item["created_at"]) if isinstance(item.get("created_at"), str) else str(item.get("created_at") or datetime.now(UTC).isoformat()),
            result=result if isinstance(result, dict) else None,
            error=str(item["error"]) if item.get("error") is not None else None,
        )


task_queue = TaskQueue(DEFAULT_TASK_STORE)
