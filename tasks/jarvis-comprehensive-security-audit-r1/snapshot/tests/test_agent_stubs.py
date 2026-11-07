from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path

from app.agent.scheduler import ScheduledJob, Scheduler
from app.agent.task_queue import AgentTask, TaskQueue, task_queue

TEST_STORE_DIR = Path("tasks/.agent_persistence_test")


def _store_path(name: str) -> Path:
    shutil.rmtree(TEST_STORE_DIR, ignore_errors=True)
    TEST_STORE_DIR.mkdir(parents=True, exist_ok=True)
    return TEST_STORE_DIR / name


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


def test_task_queue_persists_tasks() -> None:
    try:
        store = _store_path("tasks.json")
        queue = TaskQueue(store)
        task = asyncio.run(queue.add_task("persist this"))
        asyncio.run(queue.update_status(task.task_id, "done", result={"ok": True}))

        reloaded = TaskQueue(store)
        stored = asyncio.run(reloaded.get_task(task.task_id))

        assert stored is not None
        assert stored.goal == "persist this"
        assert stored.status == "done"
        assert stored.result == {"ok": True}
    finally:
        shutil.rmtree(TEST_STORE_DIR, ignore_errors=True)


def test_task_queue_ignores_invalid_store() -> None:
    try:
        store = _store_path("tasks.json")
        store.write_text(json.dumps({"bad": "shape"}), encoding="utf-8")

        queue = TaskQueue(store)

        assert asyncio.run(queue.list_tasks()) == []
    finally:
        shutil.rmtree(TEST_STORE_DIR, ignore_errors=True)


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


def test_scheduler_persists_jobs() -> None:
    try:
        store = _store_path("jobs.json")
        local_scheduler = Scheduler(store)
        job = local_scheduler.add_job("daily", "0 8 * * *", "morning report")

        reloaded = Scheduler(store)
        jobs = reloaded.list_jobs()

        assert len(jobs) == 1
        assert jobs[0].job_id == job.job_id
        assert jobs[0].goal == "morning report"
    finally:
        shutil.rmtree(TEST_STORE_DIR, ignore_errors=True)
