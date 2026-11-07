from __future__ import annotations

import logging
import shutil
from pathlib import Path

import httpx

from app.config import settings
from app.logs.audit import audit

PROJECT_ROOT = Path(__file__).resolve().parent.parent
logger = logging.getLogger(__name__)


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _wake_model_available(value: str) -> bool:
    if not value:
        return True

    path = Path(value)
    if path.suffix or path.parent != Path("."):
        return _path(value).is_file()

    return True


def check_startup() -> dict[str, bool]:
    try:
        ollama_ok = httpx.get(f"{settings.models.ollama_base_url}/api/tags", timeout=2.0).status_code == 200
    except httpx.HTTPError:
        ollama_ok = False
    results = {
        "piper_binary": bool(
            shutil.which("piper")
            or shutil.which("piper.exe")
            or (PROJECT_ROOT / "piper" / "piper.exe").is_file()
        ),
        "piper_model": _path(settings.voice.piper_model_path).is_file(),
        "wake_model": _wake_model_available(settings.voice.wake_word_model),
        "ollama_reachable": ollama_ok,
    }
    for name, ok in results.items():
        if not ok:
            logger.warning("Startup config check failed: %s", name)
            audit.log("config_check_warn", {"component": name})
    return results
