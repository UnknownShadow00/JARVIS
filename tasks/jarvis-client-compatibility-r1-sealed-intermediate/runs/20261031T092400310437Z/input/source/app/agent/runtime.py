"""Lazy shared authority for the existing server and local CLI facades."""
from pathlib import Path
import threading
from app.agent.authority import Actor, Authority, AuthorityError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SERVICE_ACTOR = Actor("local-service")
_authority = None
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
    global _authority
    with _mutex:
        if _authority is not None:
            _authority.close()
            _authority = None
