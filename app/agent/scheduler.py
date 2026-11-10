"""One-shot nominal callbacks; admission and last_run share one transaction."""
import asyncio
import inspect
from datetime import UTC, datetime
import uuid
from app.agent.authority import AuthorityError, instant
from app.agent.runtime import SERVICE_ACTOR, get_authority, get_execution_pipeline


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
        self._lifecycle = asyncio.Lock()
        self._cleanup_task = None
        self._cleanup_timeout = 1.0

    def add_job(self, name, cron_expr, goal, *, request_id, execution=None):
        a = get_authority()
        previous = a.receipt(SERVICE_ACTOR, request_id)
        nominal = previous["result"].get("next_run_at") if previous and previous["operation"] == "add_schedule" else cron_next(cron_expr, datetime.now(UTC).isoformat())
        template = None
        if execution is not None:
            pipeline = get_execution_pipeline()
            # Preserve the first server-derived authorization time on retries.
            old = previous["result"].get("execution_template") if previous and previous["operation"] == "add_schedule" else None
            normalized = {"timeout_seconds": 10, "expires_after_seconds": 60, **execution}
            if old and {k:v for k,v in old.items() if k != "authorization"} == normalized:
                template = old
            else:
                template = pipeline.schedule_template(SERVICE_ACTOR, **execution)
        result = a.add_schedule(SERVICE_ACTOR, request_id, name, cron_expr, goal, nominal, execution=template)
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
        try:
            if self._backend is not None and self._backend.get_job(job_id) is not None:
                self._backend.remove_job(job_id)
        except Exception as exc:
            self._failure = "backend_removal_failed"
            raise AuthorityError("backend_removal_reconcile") from exc
        return result

    def list_jobs(self):
        return get_authority().list_schedules(SERVICE_ACTOR)

    async def start(self):
        async with self._lifecycle:
            await self._start()

    async def _start(self):
        if self._failure:
            raise AuthorityError("scheduler_reconcile_required")
        if self._backend is not None:
            return
        from app.agent.scheduler_backend import OwnedAsyncIOScheduler
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
        try:
            self._backend = OwnedAsyncIOScheduler(timezone=UTC)
            for job in jobs:
                self._register(job)
            self._backend.start()
        except BaseException:
            await self._stop()
            raise

    async def stop(self):
        # Fence retained callbacks and start attempts before any await.
        self._epoch = None
        self._failure = "shutdown_in_progress"
        async with self._lifecycle:
            await self._stop()

    async def _shutdown_backend(self, backend):
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from app.agent.scheduler_backend import OwnedAsyncIOScheduler
        if isinstance(backend, OwnedAsyncIOScheduler):
            await backend.aclose()
        elif isinstance(backend, AsyncIOScheduler):
            # An unowned deferred API provides no completion contract.
            raise AuthorityError("scheduler_cleanup_protocol_required")
        else:
            # Synchronous backends promise completion on return; coroutine
            # backends promise it on await. Retry after a failure regardless
            # of their running flag, which can precede actual cleanup.
            result = backend.shutdown(wait=False)
            if inspect.isawaitable(result):
                await result

    def _observe_cleanup(self, task):
        if not task.cancelled():
            failed = task.exception() is not None
            if failed and task is self._cleanup_task:
                self._failure = "backend_shutdown_failed"

    async def _stop(self):
        self._epoch = None
        self._failure = "shutdown_in_progress"
        error = None
        try:
            get_authority().scheduler_control(SERVICE_ACTOR, str(uuid.uuid4()), False)
        except BaseException as exc:
            error = exc
        try:
            if self._backend is not None:
                if self._cleanup_task is None or self._cleanup_task.done() and (
                    self._cleanup_task.cancelled() or self._cleanup_task.exception() is not None
                ):
                    self._cleanup_task = asyncio.create_task(self._shutdown_backend(self._backend))
                    self._cleanup_task.add_done_callback(self._observe_cleanup)
                # Timeout/caller cancellation must not cancel or abandon the
                # cleanup operation. A stop retry awaits the same owned task.
                await asyncio.wait_for(asyncio.shield(self._cleanup_task), self._cleanup_timeout)
        except BaseException:
            self._failure = "backend_shutdown_unconfirmed"
            if error is None:
                raise
            error.add_note("Backend cleanup also remains unconfirmed; restart is fenced.")
        else:
            self._backend = None
            self._cleanup_task = None
        if error is not None:
            self._failure = self._failure if self._backend is not None else "durable_stop_unconfirmed"
            raise error
        self._failure = None

    def _register(self, job):
        if self._epoch is None or self._failure:
            return
        if not job["enabled"] or job["removed"]:
            return
        from apscheduler.triggers.date import DateTrigger
        self._backend.add_job(self._dispatch, trigger=DateTrigger(run_date=datetime.fromisoformat(job["next_run_at"])), args=[job["job_id"], job["revision"], job["next_run_at"], self._epoch], id=job["job_id"], replace_existing=True)

    async def _dispatch(self, job_id, revision, nominal, epoch):
        if self._backend is None or epoch != self._epoch or self._failure:
            return
        job = next((j for j in self.list_jobs() if j["job_id"] == job_id), None)
        if job is None or not job["enabled"] or job["removed"] or job["revision"] != revision:
            return
        try:
            get_authority().admit_occurrence(SERVICE_ACTOR, job_id, revision, nominal, epoch, cron_next(job["cron_expr"], nominal))
            if self._backend is not None:
                current = next(j for j in self.list_jobs() if j["job_id"] == job_id)
                self._register(current)
        except Exception as exc:
            if isinstance(exc, AuthorityError) and exc.code == "stale_occurrence":
                return
            self._failure = "occurrence_reconcile_required"
            get_authority().scheduler_control(SERVICE_ACTOR, str(uuid.uuid4()), False)
            raise

    def readiness(self):
        return {"scheduler_ready": self._backend is not None and self._failure is None, "scheduler_failure": self._failure, **get_authority().readiness()}


scheduler = Scheduler()
