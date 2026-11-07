from __future__ import annotations

import pytest

from app.agent.scheduler import ScheduledJob, Scheduler


def test_add_job() -> None:
    scheduler = Scheduler()

    job = scheduler.add_job("test", "0 * * * *", "run test")

    assert isinstance(job, ScheduledJob)
    assert job.name == "test"
    assert job.cron_expr == "0 * * * *"
    assert job.goal == "run test"
    assert job.enabled is True
    assert job.last_run is None


def test_remove_job_exists() -> None:
    scheduler = Scheduler()
    job = scheduler.add_job("test", "0 * * * *", "run test")

    removed = scheduler.remove_job(job.job_id)

    assert removed is True


def test_remove_job_missing() -> None:
    scheduler = Scheduler()

    removed = scheduler.remove_job("missing")

    assert removed is False


def test_list_jobs() -> None:
    scheduler = Scheduler()
    scheduler.add_job("test-1", "0 * * * *", "run test 1")
    scheduler.add_job("test-2", "30 * * * *", "run test 2")

    jobs = scheduler.list_jobs()

    assert len(jobs) == 2


@pytest.mark.asyncio
async def test_no_apscheduler(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.agent.scheduler.APSCHEDULER_AVAILABLE", False)
    scheduler = Scheduler()

    await scheduler.start()

    assert scheduler._running is True
    assert scheduler._scheduler is None
