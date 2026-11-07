"""Authority routes under the existing server authentication middleware."""
from typing import Annotated
from fastapi import APIRouter, Query, Request
import secrets
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from app.agent.authority import AuthorityError
from app.agent.runtime import SERVICE_ACTOR, get_authority, get_execution_pipeline, execution_readiness
from app.agent.scheduler import scheduler

router = APIRouter()
PUBLIC_REQUEST_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$"
UNAVAILABLE = frozenset({"execution_disabled", "execution_worker_not_ready", "execution_worker_reconcile_required",
    "owner_busy", "owner_fenced", "store_replaced", "authority_unavailable", "storage_unknown_reconcile",
    "legacy_migration_required", "backend_registration_reconcile", "backend_removal_reconcile", "ledger_inconsistent",
    "ledger_checkpoint_required", "ledger_checkpoint_mismatch", "checkpoint_missing", "checkpoint_authentication_failed",
    "checkpoint_continuity_failed", "checkpoint_gap", "ledger_commit_reconcile", "checkpoint_reconciliation_required"})


class Submission(BaseModel):
    model_config = ConfigDict(extra="forbid")
    request_id: StrictStr = Field(max_length=36, pattern=PUBLIC_REQUEST_PATTERN)
    goal: StrictStr = Field(max_length=8192)


class ScheduledExecution(BaseModel):
    model_config = ConfigDict(extra="forbid")
    capability: StrictStr = Field(max_length=128)
    payload: dict[str, Annotated[StrictStr, Field(max_length=8192)]] = Field(min_length=1, max_length=1)
    timeout_seconds: StrictInt = 10
    expires_after_seconds: StrictInt = 60


class Schedule(Submission):
    name: StrictStr = Field(max_length=256)
    cron_expr: StrictStr = Field(max_length=256)
    execution: ScheduledExecution | None = None


class ExecutionSubmission(Submission):
    capability: StrictStr = Field(max_length=128)
    payload: dict[str, Annotated[StrictStr, Field(max_length=8192)]] = Field(min_length=1, max_length=1)
    expires_at: StrictStr = Field(max_length=64)
    timeout_seconds: StrictInt = 10


def invoke(operation):
    try:
        return operation()
    except AuthorityError as exc:
        if exc.code in UNAVAILABLE or exc.code.startswith(("ledger_", "checkpoint_", "restore_", "archive_attestation_", "enrollment_", "recovery_", "authority_unenrolled")):
            code = 503
        elif exc.code in {"request_conflict", "stale_occurrence"}:
            code = 409
        else:
            code = {"not_found": 404, "queue_capacity_exceeded": 429}.get(exc.code, 400)
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


@router.get("/operator/diagnostics")
async def operator_diagnostics(request: Request, task_id: str | None = None,
    limit: Annotated[int, Query(ge=1,le=200)] = 100, offset: Annotated[int, Query(ge=0,le=1000000)] = 0):
    # Require a configured credential even when the host app permits anonymous
    # ordinary routes. Also protects independently embedded copies of this router.
    from app.config import settings
    from app.agent.recovery import OperatorRecovery
    expected=settings.server.api_token
    supplied=request.headers.get('authorization','')
    if not expected or not secrets.compare_digest(supplied.encode(), ('Bearer '+expected).encode()):
        return JSONResponse(status_code=401,content={"error":"operator_authentication_required"})
    return invoke(lambda: OperatorRecovery(get_authority()).diagnose(SERVICE_ACTOR,task_id=task_id,limit=limit,offset=offset))


@router.get("/tasks")
async def tasks(status: str | None = None, limit: Annotated[int, Query(ge=1, le=200)] = 100, offset: Annotated[int, Query(ge=0, le=1000000)] = 0):
    return invoke(lambda: get_authority().task_page(SERVICE_ACTOR, status=status, limit=limit, offset=offset))


@router.get("/tasks/{task_id}")
async def task(task_id: str):
    return invoke(lambda: get_authority().get_task(SERVICE_ACTOR, task_id))


@router.delete("/tasks/{task_id}")
async def cancel(task_id: str, request_id: Annotated[str, Query(pattern=PUBLIC_REQUEST_PATTERN)]):
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
    return invoke(lambda: scheduler.add_job(request.name, request.cron_expr, request.goal, request_id=request.request_id,
        execution=request.execution.model_dump() if request.execution is not None else None))


@router.get("/schedule/jobs")
async def jobs():
    return invoke(lambda: {"jobs": scheduler.list_jobs()})


@router.delete("/schedule/jobs/{job_id}")
async def remove_job(job_id: str, request_id: Annotated[str, Query(pattern=PUBLIC_REQUEST_PATTERN)]):
    return invoke(lambda: scheduler.remove_job(job_id, request_id=request_id))


@router.get("/ready")
async def readiness():
    result = invoke(scheduler.readiness)
    if isinstance(result, dict):
        result.update(execution_readiness())
        if not result["scheduler_ready"] or result["synthetic_execution_enabled"] and not result["execution_worker_ready"]:
            return JSONResponse(status_code=503, content=result)
    return result
