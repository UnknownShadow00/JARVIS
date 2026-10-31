from __future__ import annotations

import json
import importlib.util
import errno
import os
import stat
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

AsyncIOScheduler = None
CronTrigger = None
APSCHEDULER_AVAILABLE = importlib.util.find_spec("apscheduler") is not None

from app.agent.task_queue import TaskQueueAuditError, TaskQueueIdentifierError, TaskQueuePersistenceError, task_queue
from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOB_STORE = PROJECT_ROOT / "data" / "scheduled_jobs.json"


class SchedulerOperationError(RuntimeError):
    """An attempted scheduler operation failed; applied state must be reconciled."""

    def __init__(
        self, message: str, *, operation: str | None = None, job_id: str | None = None,
        applied: bool = False, published: bool = False, uncertain: bool = False,
        phase: str = "persistence",
    ) -> None:
        super().__init__(message)
        self.operation, self.job_id = operation, job_id
        self.applied, self.published = applied, published
        self.uncertain, self.phase = uncertain, phase


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
        self._load_error: str | None = None
        self._persistence_uncertain = False
        self._runtime_uncertain = False
        self._generation = 0
        self._load()

    def add_job(self, name: str, cron_expr: str, goal: str) -> ScheduledJob:
        self._check_health("create")
        for _ in range(32):
            job_id = str(uuid.uuid4())[:8]
            if job_id not in self._jobs:
                break
        else:
            raise SchedulerOperationError("Identifier attempts exhausted.", operation="create", phase="identifier")
        job = ScheduledJob(job_id=job_id, name=name, cron_expr=cron_expr, goal=goal)
        if not self._record_valid(asdict(job)):
            raise SchedulerOperationError("Invalid job fields.", operation="create", job_id=job_id, phase="validation")
        trigger = self._prepare_trigger(job, "create")
        previous = self._jobs.copy()
        self._jobs[job_id] = job
        try:
            self._save()
        except SchedulerOperationError as exc:
            exc.operation, exc.job_id = "create", job_id
            if not exc.applied:
                self._jobs = previous
            raise
        try:
            if self._scheduler is not None:
                self._register_job(job, trigger=trigger)
        except Exception as exc:
            raise self._runtime_failure("create", job_id, "backend") from exc
        self._audit_applied("create", job_id,
            "job_added",
            {"job_id": job_id, "name": name, "cron_expr": cron_expr, "goal": goal},
        )
        return job

    def remove_job(self, job_id: str) -> bool:
        self._check_health("delete", job_id)
        if job_id not in self._jobs:
            return False
        previous = self._jobs.copy()
        del self._jobs[job_id]
        try:
            self._save()
        except SchedulerOperationError as exc:
            exc.operation, exc.job_id = "delete", job_id
            if not exc.applied:
                self._jobs = previous
            raise
        if self._scheduler is not None:
            try:
                self._scheduler.remove_job(job_id, jobstore=None)
            except Exception as exc:
                raise self._runtime_failure("delete", job_id, "backend") from exc
        self._audit_applied("delete", job_id, "job_removed", {"job_id": job_id})
        return True

    def list_jobs(self) -> list[ScheduledJob]:
        return list(self._jobs.values())

    async def start(self) -> None:
        self._check_health("start")
        if self._running:
            return
        if _load_apscheduler():
            triggers = {
                job.job_id: self._prepare_trigger(job, "start")
                for job in self._jobs.values() if job.enabled
            }
            self._generation += 1
            try:
                self._scheduler = AsyncIOScheduler()
                for job in self._jobs.values():
                    self._register_job(job, trigger=triggers.get(job.job_id))
                self._scheduler.start()
            except Exception as exc:
                self._failed_start_cleanup()
                raise SchedulerOperationError(
                    "Scheduler backend start failed; review before restart.",
                    operation="start", uncertain=True, phase="backend",
                ) from exc
            self._running = True
            try:
                audit.log("scheduler_start", {"job_count": len(self._jobs), "backend": "apscheduler"})
            except Exception as exc:
                self._failed_start_cleanup()
                raise SchedulerOperationError(
                    "Scheduler started but audit reporting failed; admission blocked.",
                    operation="start", applied=True, uncertain=True, phase="audit",
                ) from exc
            return

        self._generation += 1
        self._running = True
        try:
            audit.log("scheduler_start", {"job_count": len(self._jobs), "backend": "stub"})
        except Exception as exc:
            self._running = False
            self._generation += 1
            self._runtime_uncertain = True
            raise SchedulerOperationError(
                "Stub start audit reporting failed.", operation="start", applied=True,
                uncertain=True, phase="audit",
            ) from exc

    async def stop(self) -> None:
        # Invalidate every retained callback before attempting backend shutdown.
        self._running = False
        self._generation += 1
        if self._scheduler is not None:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception as exc:
                self._runtime_uncertain = True
                raise SchedulerOperationError(
                    "Backend shutdown failed; admission is blocked.", operation="stop",
                    applied=True, uncertain=True, phase="backend",
                ) from exc
            self._scheduler = None
        try:
            audit.log("scheduler_stop", {})
        except Exception as exc:
            self._runtime_uncertain = True
            raise SchedulerOperationError(
                "Scheduler admission stopped but audit reporting failed.", operation="stop",
                applied=True, uncertain=True, phase="audit",
            ) from exc

    def _register_job(self, job: ScheduledJob, *, trigger: Any = None) -> None:
        if self._jobs.get(job.job_id) is not job or not job.enabled:
            return
        if self._scheduler is None or not _load_apscheduler() or CronTrigger is None:
            return
        if trigger is None:
            trigger = self._prepare_trigger(job, "register")
        self._scheduler.add_job(
            self._dispatch_job,
            trigger=trigger,
            args=[job, self._generation],
            id=job.job_id,
            replace_existing=True,
        )

    async def _dispatch_job(self, job: ScheduledJob, generation: int) -> None:
        if (
            not self._running or self._scheduler is None or generation != self._generation
            or self._jobs.get(job.job_id) is not job or not job.enabled
            or self._load_error is not None or self._persistence_uncertain or self._runtime_uncertain
        ):
            return
        # This is admission, not cancellation: an already admitted enqueue can
        # finish after remove/stop while waiting on the task queue's instance lock.
        await _run_job(job)

    def _prepare_trigger(self, job: ScheduledJob, operation: str) -> Any:
        if not _load_apscheduler() or CronTrigger is None:
            return None  # Stub mode stores jobs without claiming cron validation.
        try:
            return CronTrigger.from_crontab(job.cron_expr)
        except Exception as exc:
            raise SchedulerOperationError(
                "Invalid cron expression.", operation=operation, job_id=job.job_id, phase="validation",
            ) from exc

    def _check_health(self, operation: str, job_id: str | None = None) -> None:
        if self._load_error is not None or self._persistence_uncertain or self._runtime_uncertain:
            raise SchedulerOperationError(
                "Scheduler requires review; new mutations and admission are blocked.",
                operation=operation, job_id=job_id, phase="admission", uncertain=True,
            )

    def _runtime_failure(self, operation: str, job_id: str, phase: str) -> SchedulerOperationError:
        self._runtime_uncertain = True
        return SchedulerOperationError(
            "Job state applied but backend/audit acknowledgement failed; reconcile before retry.",
            operation=operation, job_id=job_id, applied=True,
            published=self._storage_path is not None, uncertain=True, phase=phase,
        )

    def _audit_applied(self, operation: str, job_id: str, event: str, details: dict[str, Any]) -> None:
        try:
            audit.log(event, details)
        except Exception as exc:
            raise self._runtime_failure(operation, job_id, "audit") from exc

    def _failed_start_cleanup(self) -> None:
        self._running = False
        self._generation += 1
        self._runtime_uncertain = True
        if self._scheduler is not None:
            try:
                self._scheduler.shutdown(wait=False)
            except Exception:
                return  # Keep the backend reference for an explicit stop attempt.
            self._scheduler = None

    def _load(self) -> None:
        if self._storage_path is None:
            return
        try:
            raw = json.loads(self._read_store(), object_pairs_hook=self._unique_object, parse_constant=self._reject_constant)
        except FileNotFoundError:
            if self._storage_path.is_symlink():
                self._block_load()
            return
        except (OSError, ValueError):
            self._block_load()
            return
        if not isinstance(raw, list):
            self._block_load()
            return
        jobs: dict[str, ScheduledJob] = {}
        for item in raw:
            if not isinstance(item, dict) or not self._record_valid(item):
                self._block_load()
                continue
            job = self._job_from_dict(item)
            if job is not None:
                if job.job_id in jobs:
                    self._block_load()
                jobs[job.job_id] = job
        self._jobs = jobs

    def _block_load(self) -> None:
        if self._load_error is not None:
            return
        self._load_error = "Invalid or unreadable scheduled-job store."
        try:
            audit.log("scheduler_load_error", {"path": str(self._storage_path), "error": self._load_error})
        except Exception:
            pass

    def _read_store(self) -> str:
        if not stat.S_ISREG(self._storage_path.stat().st_mode):
            raise ValueError("Store is not a regular file.")
        descriptor = os.open(self._storage_path, os.O_RDONLY | getattr(os, "O_NONBLOCK", 0))
        try:
            if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                raise ValueError("Store changed to a nonregular file.")
            with os.fdopen(descriptor, "r", encoding="utf-8", closefd=False) as opened:
                return opened.read()
        finally:
            os.close(descriptor)

    @staticmethod
    def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate JSON key.")
            result[key] = value
        return result

    @staticmethod
    def _reject_constant(value: str) -> None:
        raise ValueError("Nonfinite JSON constant.")

    @staticmethod
    def _record_valid(item: dict[str, Any]) -> bool:
        if item.keys() - {"job_id", "name", "cron_expr", "goal", "enabled", "last_run"}:
            return False
        if any(not isinstance(item.get(name), str) or not item[name].strip() for name in ("job_id", "name", "cron_expr", "goal")):
            return False
        return (
            isinstance(item.get("enabled", True), bool)
            and (item.get("last_run") is None or isinstance(item["last_run"], str))
        )

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._check_health("save")
        temporary_path: Path | None = None
        published = False
        try:
            payload = [asdict(job) for job in self._jobs.values()]
            if any(not self._record_valid(item) for item in payload):
                raise ValueError("Job record cannot be reloaded without loss.")
            serialized = json.dumps(payload, indent=2, allow_nan=False)
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self._storage_path.parent,
                prefix=f".{self._storage_path.name}.", suffix=".tmp", delete=False,
            ) as opened:
                temporary_path = Path(opened.name)
                opened.write(serialized)
                opened.flush()
                os.fsync(opened.fileno())
            os.replace(temporary_path, self._storage_path)
            published, temporary_path = True, None
            self._sync_directory()
        except Exception as exc:
            self._persistence_uncertain = published
            try:
                audit.log("scheduler_save_error", {"path": str(self._storage_path), "published": published})
            except Exception:
                pass
            raise SchedulerOperationError(
                "Scheduled-job publication failed.", applied=published,
                published=published, uncertain=published,
            ) from exc
        finally:
            if temporary_path is not None:
                try:
                    temporary_path.unlink(missing_ok=True)
                except OSError:
                    pass

    def _sync_directory(self) -> None:
        if os.name != "posix":
            return
        unsupported = {errno.EINVAL, errno.ENOTSUP, errno.EOPNOTSUPP, errno.ENOSYS}
        try:
            descriptor = os.open(self._storage_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        except OSError as exc:
            if exc.errno not in unsupported:
                raise

    def _job_from_dict(self, item: dict[str, Any]) -> ScheduledJob | None:
        job_id = str(item.get("job_id") or "")
        name = str(item.get("name") or "")
        cron_expr = str(item.get("cron_expr") or "")
        goal = str(item.get("goal") or "")
        if not all(value.strip() for value in (job_id, name, cron_expr, goal)):
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
    if not job.enabled:
        return
    try:
        task = await task_queue.add_task(job.goal)
    except (TaskQueuePersistenceError, TaskQueueIdentifierError, TaskQueueAuditError) as exc:
        try:
            audit.log("job_enqueue_failed", {
                "job_id": job.job_id, "task_id": getattr(exc, "task_id", None),
                "published": isinstance(exc, (TaskQueuePersistenceError, TaskQueueAuditError)) and exc.published,
                "audit_failed_after_apply": isinstance(exc, TaskQueueAuditError),
                "automatic_retry": False,
            })
        except Exception:
            pass  # Retain the original queue failure if reporting is unavailable.
        raise
    job.last_run = datetime.now(UTC).isoformat()
    try:
        audit.log("job_executed", {
            "job_id": job.job_id, "name": job.name, "goal": job.goal,
            "task_id": task.task_id, "outcome": "enqueued_only",
        })
    except Exception as exc:
        raise TaskQueueAuditError(
            operation="create", task_id=task.task_id,
            published=task_queue._storage_path is not None,
        ) from exc


def _load_apscheduler() -> bool:
    global APSCHEDULER_AVAILABLE, AsyncIOScheduler, CronTrigger
    if not APSCHEDULER_AVAILABLE:
        return False
    if AsyncIOScheduler is not None and CronTrigger is not None:
        return True

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler as LoadedAsyncIOScheduler
        from apscheduler.triggers.cron import CronTrigger as LoadedCronTrigger
    except ImportError:
        APSCHEDULER_AVAILABLE = False
        AsyncIOScheduler = None
        CronTrigger = None
        return False

    AsyncIOScheduler = LoadedAsyncIOScheduler
    CronTrigger = LoadedCronTrigger
    APSCHEDULER_AVAILABLE = True
    return True


scheduler = Scheduler(DEFAULT_JOB_STORE)
