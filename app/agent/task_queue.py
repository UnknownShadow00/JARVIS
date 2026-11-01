"""Compatibility facade. No independent JSON writer or public completion API."""
from dataclasses import dataclass
from app.agent.authority import AuthorityError
from app.agent.runtime import SERVICE_ACTOR, get_authority


@dataclass
class AgentTask:
    task_id: str
    goal: str
    status: str
    created_at: str
    result: dict | None = None
    error: str | None = None
    cancel_requested: bool = False


def snapshot(row):
    return AgentTask(**{key: row[key] for key in AgentTask.__dataclass_fields__})


class TaskQueue:
    def __init__(self, storage_path=None):
        if storage_path is not None:
            raise AuthorityError("independent_store_disabled")

    @property
    def tasks(self):
        return [snapshot(t) for t in get_authority().list_tasks(SERVICE_ACTOR)]

    async def add_task(self, goal, *, request_id):
        return snapshot(get_authority().submit(SERVICE_ACTOR, request_id, goal)["result"])

    async def list_tasks(self, status=None):
        return [t for t in self.tasks if status is None or t.status == status]

    async def get_task(self, task_id):
        return next((t for t in self.tasks if t.task_id == task_id), None)

    async def update_status(self, *args, **kwargs):
        raise AuthorityError("public_completion_disabled")

    async def delete_task(self, task_id, *, request_id):
        return get_authority().cancel(SERVICE_ACTOR, request_id, task_id)


task_queue = TaskQueue()
