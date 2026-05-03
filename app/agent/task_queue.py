from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.logs.audit import audit


@dataclass
class AgentTask:
    task_id: str
    goal: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    result: dict | None = None
    error: str | None = None


class TaskQueue:
    def __init__(self) -> None:
        self._tasks: dict[str, AgentTask] = {}
        self._lock: asyncio.Lock | None = None

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
        audit.log("task_status_update", {"task_id": task_id, "status": status})
        return True


task_queue = TaskQueue()
