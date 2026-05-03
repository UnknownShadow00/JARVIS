from __future__ import annotations

import uuid
from dataclasses import dataclass

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

    def add_job(self, name: str, cron_expr: str, goal: str) -> ScheduledJob:
        job_id = str(uuid.uuid4())[:8]
        job = ScheduledJob(job_id=job_id, name=name, cron_expr=cron_expr, goal=goal)
        self._jobs[job_id] = job
        audit.log(
            "job_added",
            {"job_id": job_id, "name": name, "cron_expr": cron_expr, "goal": goal},
        )
        return job

    def remove_job(self, job_id: str) -> bool:
        if job_id not in self._jobs:
            return False
        del self._jobs[job_id]
        audit.log("job_removed", {"job_id": job_id})
        return True

    def list_jobs(self) -> list[ScheduledJob]:
        return list(self._jobs.values())

    async def start(self) -> None:
        self._running = True
        audit.log("scheduler_start", {"job_count": len(self._jobs)})

    async def stop(self) -> None:
        self._running = False
        audit.log("scheduler_stop", {})


scheduler = Scheduler()
