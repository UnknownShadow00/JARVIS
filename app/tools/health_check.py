from __future__ import annotations

import shutil
from pathlib import Path

import httpx

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def _wake_model_available(value: str) -> bool:
    if not value:
        return False

    path = Path(value)
    if path.suffix or path.parent != Path("."):
        return _path(value).is_file()

    return True


def check_tools() -> dict[str, bool]:
    try:
        ollama = httpx.get(f"{settings.models.ollama_base_url}/api/tags", timeout=2.0).status_code == 200
    except httpx.HTTPError:
        ollama = False
    piper = any(
        (
            shutil.which("piper"),
            shutil.which("piper.exe"),
            (PROJECT_ROOT / "piper" / "piper.exe").is_file(),
        )
    )
    return {
        "ollama": ollama,
        "piper": piper,
        "interpreter": shutil.which("interpreter") is not None,
        "wake_model": _wake_model_available(settings.voice.wake_word_model),
    }
