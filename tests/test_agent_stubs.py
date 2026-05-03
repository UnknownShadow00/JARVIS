from __future__ import annotations

import asyncio

from app.agent.scheduler import ScheduledJob, Scheduler
from app.agent.task_queue import AgentTask, TaskQueue, task_queue


def test_add_task() -> None:
    task_queue._tasks.clear()

    task = asyncio.run(task_queue.add_task("do something"))

    assert isinstance(task, AgentTask)
    assert task.goal == "do something"
    assert task.status == "pending"


def test_list_tasks_empty() -> None:
    queue = TaskQueue()

    tasks = asyncio.run(queue.list_tasks())

    assert isinstance(tasks, list)
    assert tasks == []


def test_list_tasks_by_status() -> None:
    queue = TaskQueue()
    task = asyncio.run(queue.add_task("do something"))

    tasks = asyncio.run(queue.list_tasks("pending"))

    assert task in tasks


def test_update_task_status() -> None:
    queue = TaskQueue()
    task = asyncio.run(queue.add_task("do something"))

    updated = asyncio.run(queue.update_status(task.task_id, "done"))
    stored = asyncio.run(queue.get_task(task.task_id))

    assert updated is True
    assert stored is not None
    assert stored.status == "done"


def test_add_scheduler_job() -> None:
    local_scheduler = Scheduler()

    job = local_scheduler.add_job("daily", "0 8 * * *", "morning report")

    assert isinstance(job, ScheduledJob)
    assert job.name == "daily"
    assert job.goal == "morning report"


def test_list_scheduler_jobs() -> None:
    local_scheduler = Scheduler()
    job = local_scheduler.add_job("daily", "0 8 * * *", "morning report")

    jobs = local_scheduler.list_jobs()

    assert job in jobs


def test_remove_scheduler_job() -> None:
    local_scheduler = Scheduler()
    job = local_scheduler.add_job("daily", "0 8 * * *", "morning report")

    removed = local_scheduler.remove_job(job.job_id)

    assert removed is True
    assert local_scheduler.list_jobs() == []
