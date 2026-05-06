from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOB_STORE = PROJECT_ROOT / "data" / "scheduled_jobs.json"


@dataclass
class ScheduledJob:
    job_id: str
    name: str
    cron_expr: str
    goal: str
    enabled: bool = True
    last_run: str | None = None


class Scheduler:
    def __init__(self, storage_path: str | Path | None = None) -> None:
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._scheduler: AsyncIOScheduler | None = None
        self._storage_path = Path(storage_path) if storage_path is not None else None
        self._load()

    def add_job(self, name: str, cron_expr: str, goal: str) -> ScheduledJob:
        job_id = str(uuid.uuid4())[:8]
        job = ScheduledJob(job_id=job_id, name=name, cron_expr=cron_expr, goal=goal)
        self._jobs[job_id] = job
        self._save()
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
        self._save()
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

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.is_file():
            return
        try:
            raw = json.loads(self._storage_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            audit.log("scheduler_load_error", {"path": str(self._storage_path), "error": str(exc)})
            return
        if not isinstance(raw, list):
            return
        jobs: dict[str, ScheduledJob] = {}
        for item in raw:
            if not isinstance(item, dict):
                continue
            job = self._job_from_dict(item)
            if job is not None:
                jobs[job.job_id] = job
        self._jobs = jobs

    def _save(self) -> None:
        if self._storage_path is None:
            return
        try:
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            payload = [asdict(job) for job in self._jobs.values()]
            self._storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except OSError as exc:
            audit.log("scheduler_save_error", {"path": str(self._storage_path), "error": str(exc)})

    def _job_from_dict(self, item: dict[str, Any]) -> ScheduledJob | None:
        job_id = str(item.get("job_id") or "").strip()
        name = str(item.get("name") or "").strip()
        cron_expr = str(item.get("cron_expr") or "").strip()
        goal = str(item.get("goal") or "").strip()
        if not job_id or not name or not cron_expr or not goal:
            return None
        return ScheduledJob(
            job_id=job_id,
            name=name,
            cron_expr=cron_expr,
            goal=goal,
            enabled=bool(item.get("enabled", True)),
            last_run=str(item["last_run"]) if item.get("last_run") is not None else None,
        )


async def _run_job(job: ScheduledJob) -> None:
    job.last_run = datetime.now(UTC).isoformat()
    await task_queue.add_task(job.goal)
    audit.log("job_executed", {"job_id": job.job_id, "name": job.name, "goal": job.goal})


scheduler = Scheduler(DEFAULT_JOB_STORE)
