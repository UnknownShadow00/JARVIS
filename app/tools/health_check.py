from __future__ import annotations

import shutil
from pathlib import Path

import httpx

from app.config import settings

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def check_tools() -> dict[str, bool]:
    wake_model = Path(settings.voice.wake_word_model)
    if not wake_model.is_absolute():
        wake_model = PROJECT_ROOT / wake_model
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
        "wake_model": settings.voice.wake_word_model != "" and wake_model.is_file(),
    }
