"""Lazy shared authority for the existing server and local CLI facades."""
from pathlib import Path
import threading
from app.agent.authority import Actor, Authority, AuthorityError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVICE_ACTOR = Actor("local-service")
_authority = None
_execution_worker = None
_mutex = threading.RLock()


def get_authority():
    global _authority
    with _mutex:
        if _authority is None:
            _authority = Authority(PROJECT_ROOT / "data/authority/queue.sqlite", legacy_paths=(PROJECT_ROOT / "data/agent_tasks.json", PROJECT_ROOT / "data/scheduled_jobs.json"))
        return _authority


def bind_authority(authority):
    """Trusted local embedding/test hook; never exposed through HTTP."""
    global _authority
    with _mutex:
        if _authority is not None:
            raise AuthorityError("authority_already_bound")
        _authority = authority


def close_authority():
    global _authority, _execution_worker
    with _mutex:
        if _execution_worker is not None and _execution_worker._task is not None:
            raise AuthorityError("execution_worker_must_stop")
        _execution_worker = None
        if _authority is not None:
            _authority.close()
            _authority = None


def bind_offline_execution(policy, *, max_pending=128):
    """Trusted embedding opt-in only; no environment/HTTP live execution switch."""
    global _execution_worker
    from app.agent.execution import ExecutionPipeline, ExecutionWorker
    with _mutex:
        if _execution_worker is not None:
            raise AuthorityError("execution_already_bound")
        pipeline = ExecutionPipeline(get_authority(), policy, enabled=True, max_pending=max_pending)
        _execution_worker = ExecutionWorker(pipeline, SERVICE_ACTOR)
        return _execution_worker


def get_execution_worker():
    with _mutex:
        return _execution_worker


def execution_readiness():
    worker = get_execution_worker()
    return worker.readiness() if worker else {"synthetic_execution_enabled": False, "execution_worker_ready": False,
                                           "execution_worker_failure": None, "real_execution_enabled": False}


def get_execution_pipeline():
    worker = get_execution_worker()
    if worker is None:
        raise AuthorityError("execution_disabled")
    if worker.failure is not None:
        raise AuthorityError("execution_worker_reconcile_required")
    if not worker.readiness()["execution_worker_ready"]:
        raise AuthorityError("execution_worker_not_ready")
    return worker.pipeline
