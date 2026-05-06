from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TASK_STORE = PROJECT_ROOT / "data" / "agent_tasks.json"


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
            self._tasks[task_id] = task
            self._save()
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
            task.status = status
            task.result = result
            task.error = error
            self._save()
        audit.log("task_status_update", {"task_id": task_id, "status": status})
        return True

    async def delete_task(self, task_id: str) -> bool:
        lock = await self._get_lock()
        async with lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            self._save()
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
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = [asdict(task) for task in self._tasks.values()]
            self._storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            audit.log("task_queue_save_error", {"path": str(self._storage_path), "error": str(exc)})

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
