from __future__ import annotations

import asyncio
import errno
import json
import os
import tempfile
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_STORE = PROJECT_ROOT / "data" / "agent_tasks.json"


class TaskQueuePersistenceError(RuntimeError):
    """A write failed; ``published`` means the replacement may already be visible."""

    def __init__(self, message: str, *, published: bool = False) -> None:
        super().__init__(message)
        self.published = published


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
        self._load()

    async def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def add_task(self, goal: str) -> AgentTask:
        task_id = str(uuid.uuid4())[:8]
        task = AgentTask(task_id=task_id, goal=goal)
        lock = await self._get_lock()
        async with lock:
            previous = self._tasks.copy()
            self._tasks[task_id] = task
            try:
                self._save()
            except TaskQueuePersistenceError as exc:
                if not exc.published:
                    self._tasks = previous
                raise
        audit.log("task_queued", {"task_id": task_id, "goal": goal})
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
                if not exc.published:
                    task.status, task.result, task.error = previous
                raise
        audit.log("task_status_update", {"task_id": task_id, "status": status})
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
                if not exc.published:
                    self._tasks = previous
                raise
        audit.log("task_deleted", {"task_id": task_id})
        return True

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.is_file():
            return
        try:
            raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            audit.log("task_queue_load_error", {"path": str(self._storage_path), "error": str(exc)})
            return
        if not isinstance(raw, list):
            return
        tasks: dict[str, AgentTask] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            task = self._task_from_dict(item)
            if task is not None:
                tasks[task.task_id] = task
        self._tasks = tasks

    def _save(self) -> None:
        if self._storage_path is None:
            return
        if self._persistence_uncertain:
            raise TaskQueuePersistenceError(
                "Task queue writes are blocked after an uncertain publication; "
                "review the store and create a new TaskQueue instance."
            )
        temporary_path: Path | None = None
        published = False
        try:
            payload = [asdict(task) for task in self._tasks.values()]
            serialized = json.dumps(payload, indent=2)
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
        task_id = str(item.get("task_id") or "").strip()
        goal = str(item.get("goal") or "").strip()
        if not task_id or not goal:
            return None
        result = item.get("result")
        return AgentTask(
            task_id=task_id,
            goal=goal,
            status=str(item.get("status") or "pending"),
            created_at=str(item.get("created_at") or datetime.now(UTC).isoformat()),
            result=result if isinstance(result, dict) else None,
            error=str(item["error"]) if item.get("error") is not None else None,
        )


task_queue = TaskQueue(DEFAULT_TASK_STORE)
