from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

try:
    import apscheduler  # noqa: F401
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger

    APSCHEDULER_AVAILABLE = True
except ImportError:
    AsyncIOScheduler = None
    CronTrigger = None
    APSCHEDULER_AVAILABLE = False

from app.agent.task_queue import task_queue
from app.logs.audit import audit


@dataclass
class ScheduledJob:
    job_id: str
    name: str
    cron_expr: str
    goal: str
    enabled: bool = True
    last_run: str | None = None


class Scheduler:
    def __init__(self) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._scheduler: AsyncIOScheduler | None = None

    def add_job(self, name: str, cron_expr: str, goal: str) -> ScheduledJob:
        job_id = str(uuid.uuid4())[:8]
        job = ScheduledJob(job_id=job_id, name=name, cron_expr=cron_expr, goal=goal)
        self._jobs[job_id] = job
        if self._scheduler is not None:
            self._register_job(job)
        audit.log(
            "job_added",
            {"job_id": job_id, "name": name, "cron_expr": cron_expr, "goal": goal},
        )
        return job

    def remove_job(self, job_id: str) -> bool:
        if job_id not in self._jobs:
            return False
        del self._jobs[job_id]
        if self._scheduler is not None:
            try:
                self._scheduler.remove_job(job_id, jobstore=None)
            except Exception:
                pass
        audit.log("job_removed", {"job_id": job_id})
        return True

    def list_jobs(self) -> list[ScheduledJob]:
        return list(self._jobs.values())

    async def start(self) -> None:
        if APSCHEDULER_AVAILABLE:
            if self._scheduler is None:
                self._scheduler = AsyncIOScheduler()
                self._scheduler.start()
            for job in self._jobs.values():
                self._register_job(job)
            self._running = True
            audit.log("scheduler_start", {"job_count": len(self._jobs), "backend": "apscheduler"})
            return

        self._running = True
        audit.log("scheduler_start", {"job_count": len(self._jobs), "backend": "stub"})

    async def stop(self) -> None:
        if self._scheduler is not None:
            self._scheduler.shutdown(wait=False)
            self._scheduler = None
        self._running = False
        audit.log("scheduler_stop", {})

    def _register_job(self, job: ScheduledJob) -> None:
        if self._scheduler is None or CronTrigger is None:
            return
        trigger = CronTrigger.from_crontab(job.cron_expr)
        self._scheduler.add_job(
            _run_job,
            trigger=trigger,
            args=[job],
            id=job.job_id,
            replace_existing=True,
        )


async def _run_job(job: ScheduledJob) -> None:
    job.last_run = datetime.utcnow().isoformat()
    await task_queue.add_task(job.goal)
    audit.log("job_executed", {"job_id": job.job_id, "name": job.name, "goal": job.goal})


scheduler = Scheduler()
