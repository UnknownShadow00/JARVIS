"""One-shot nominal callbacks; admission and last_run share one transaction."""
from datetime import UTC, datetime
import uuid
from app.agent.authority import AuthorityError, instant
from app.agent.runtime import SERVICE_ACTOR, get_authority


def cron_next(expression, after):
    from apscheduler.triggers.cron import CronTrigger
    trigger = CronTrigger.from_crontab(expression, timezone=UTC)
    now = datetime.fromisoformat(instant(after))
    value = trigger.get_next_fire_time(now, now)
    if value is None or value <= now:
        raise AuthorityError("invalid_cron")
    return value.astimezone(UTC).isoformat()


class Scheduler:
    def __init__(self, storage_path=None):
        if storage_path is not None:
            raise AuthorityError("independent_store_disabled")
        self._backend = None
        self._epoch = None
        self._failure = None

    def add_job(self, name, cron_expr, goal, *, request_id):
        a = get_authority()
        previous = a.receipt(SERVICE_ACTOR, request_id)
        nominal = previous["result"].get("next_run_at") if previous and previous["operation"] == "add_schedule" else cron_next(cron_expr, datetime.now(UTC).isoformat())
        result = a.add_schedule(SERVICE_ACTOR, request_id, name, cron_expr, goal, nominal)
        if self._backend is not None:
            try:
                current = next(j for j in a.list_schedules(SERVICE_ACTOR, include_removed=True) if j["job_id"] == result["result"]["job_id"])
                self._register(current)
            except Exception as exc:
                self._failure = "backend_registration_failed"
                raise AuthorityError("backend_registration_reconcile") from exc
        return result

    def remove_job(self, job_id, *, request_id):
        result = get_authority().set_schedule(SERVICE_ACTOR, request_id, job_id, removed=True)
        if self._backend is not None and self._backend.get_job(job_id) is not None:
            self._backend.remove_job(job_id)
        return result

    def list_jobs(self):
        return get_authority().list_schedules(SERVICE_ACTOR)

    async def start(self):
        if self._backend is not None:
            if self._failure:
                raise AuthorityError("scheduler_reconcile_required")
            return
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        a = get_authority()
        a.readiness()
        now = datetime.now(UTC).isoformat()
        jobs = self.list_jobs()
        for job in jobs:
            if job["enabled"] and job["next_run_at"] <= now:
                raise AuthorityError("overdue_schedule_reconcile_required")
        control = a.scheduler_control(SERVICE_ACTOR, str(uuid.uuid4()), True)
        self._epoch = control["result"]["epoch"]
        self._failure = None
        self._backend = AsyncIOScheduler(timezone=UTC)
        try:
            for job in jobs:
                self._register(job)
            self._backend.start()
        except BaseException:
            await self.stop()
            raise

    async def stop(self):
        get_authority().scheduler_control(SERVICE_ACTOR, str(uuid.uuid4()), False)
        backend, self._backend = self._backend, None
        self._epoch = None
        if backend is not None and backend.running:
            backend.shutdown(wait=False)

    def _register(self, job):
        if not job["enabled"] or job["removed"]:
            return
        from apscheduler.triggers.date import DateTrigger
        self._backend.add_job(self._dispatch, trigger=DateTrigger(run_date=datetime.fromisoformat(job["next_run_at"])), args=[job["job_id"], job["revision"], job["next_run_at"], self._epoch], id=job["job_id"], replace_existing=True)

    async def _dispatch(self, job_id, revision, nominal, epoch):
        try:
            job = next(j for j in self.list_jobs() if j["job_id"] == job_id)
            get_authority().admit_occurrence(SERVICE_ACTOR, job_id, revision, nominal, epoch, cron_next(job["cron_expr"], nominal))
            if self._backend is not None:
                current = next(j for j in self.list_jobs() if j["job_id"] == job_id)
                self._register(current)
        except (AuthorityError, StopIteration) as exc:
            if isinstance(exc, AuthorityError) and exc.code == "stale_occurrence":
                return
            self._failure = "occurrence_reconcile_required"
            get_authority().scheduler_control(SERVICE_ACTOR, str(uuid.uuid4()), False)
            raise

    def readiness(self):
        return {"scheduler_ready": self._backend is not None and self._failure is None, "scheduler_failure": self._failure, **get_authority().readiness()}


scheduler = Scheduler()
