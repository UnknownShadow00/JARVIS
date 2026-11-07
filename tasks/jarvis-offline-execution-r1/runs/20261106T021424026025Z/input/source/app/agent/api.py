"""Authority routes under the existing server authentication middleware."""
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StrictInt, StrictStr
from app.agent.authority import AuthorityError
from app.agent.runtime import SERVICE_ACTOR, get_authority, get_execution_pipeline, execution_readiness
from app.agent.scheduler import scheduler

router = APIRouter()


class Submission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: StrictStr
    goal: StrictStr


class Schedule(Submission):
    name: StrictStr
    cron_expr: StrictStr


class ExecutionSubmission(Submission):
    capability: StrictStr
    payload: dict[str, StrictStr]
    expires_at: StrictStr
    timeout_seconds: StrictInt = 10


def invoke(operation):
    try:
        return operation()
    except AuthorityError as exc:
        code = 404 if exc.code == "not_found" else 409 if exc.code in {"request_conflict", "stale_occurrence"} else 429 if exc.code == "queue_capacity_exceeded" else 503 if exc.code in {"execution_disabled", "execution_worker_reconcile_required", "owner_busy", "authority_unavailable", "storage_unknown_reconcile", "legacy_migration_required", "backend_registration_reconcile", "backend_removal_reconcile"} else 400
        return JSONResponse(status_code=code, content={"error": exc.code, "automatic_retry": False, "reconcile_with_original_request_id": True})
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "invalid_cron", "automatic_retry": False})


@router.post("/tasks")
async def submit(request: Submission):
    return invoke(lambda: get_authority().submit(SERVICE_ACTOR, request.request_id, request.goal))


@router.post("/execution/tasks")
async def submit_execution(request: ExecutionSubmission):
    return invoke(lambda: get_execution_pipeline().submit(SERVICE_ACTOR, **request.model_dump()))


@router.get("/execution/status")
async def execution_status():
    return invoke(lambda: {**get_authority().readiness(), **execution_readiness()})


@router.get("/tasks")
async def tasks(status: str | None = None):
    def read():
        rows = [t for t in get_authority().list_tasks(SERVICE_ACTOR) if status is None or t["status"] == status]
        return {"tasks": rows, "count": len(rows)}
    return invoke(read)


@router.get("/tasks/{task_id}")
async def task(task_id: str):
    def read():
        rows = [t for t in get_authority().list_tasks(SERVICE_ACTOR) if t["task_id"] == task_id]
        if not rows:
            raise AuthorityError("not_found")
        return rows[0]
    return invoke(read)


@router.delete("/tasks/{task_id}")
async def cancel(task_id: str, request_id: str):
    return invoke(lambda: get_authority().cancel(SERVICE_ACTOR, request_id, task_id))


@router.get("/requests/{request_id}")
async def receipt(request_id: str):
    def read():
        result = get_authority().receipt(SERVICE_ACTOR, request_id)
        if result is None:
            raise AuthorityError("not_found")
        return result
    return invoke(read)


@router.post("/schedule/jobs")
async def add_job(request: Schedule):
    return invoke(lambda: scheduler.add_job(request.name, request.cron_expr, request.goal, request_id=request.request_id))


@router.get("/schedule/jobs")
async def jobs():
    return invoke(lambda: {"jobs": scheduler.list_jobs()})


@router.delete("/schedule/jobs/{job_id}")
async def remove_job(job_id: str, request_id: str):
    return invoke(lambda: scheduler.remove_job(job_id, request_id=request_id))


@router.get("/ready")
async def readiness():
    result = invoke(scheduler.readiness)
    if isinstance(result, dict):
        result.update(execution_readiness())
        if not result["scheduler_ready"] or result["synthetic_execution_enabled"] and not result["execution_worker_ready"]:
            return JSONResponse(status_code=503, content=result)
    return result
