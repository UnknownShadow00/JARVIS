"""Compose the deterministic JARVIS morning status report."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import CONFIG_PATH
from app.tools.system_stats import get_stats


def compose_morning_report(context: dict[str, Any] | None = None) -> str:
    now = datetime.now()
    current_time = now.strftime("%I:%M %p")
    greeting = _time_of_day(now.hour)
    context = context or {}
    gpu_temp = str(context.get("gpu_temp") or _gpu_temp())
    last_project = str(context.get("last_project") or _last_project())
    pending_tasks = _coerce_int(context.get("pending_tasks"), _pending_task_count())
    recent_errors = _coerce_int(context.get("recent_errors"), 0)
    error_sentence = f" Recent error count: {recent_errors}." if recent_errors else ""

    return (
        f"Good {greeting}, sir. The time is {current_time}. All systems operational. "
        f"GPU at {gpu_temp} degrees. {pending_tasks} tasks pending. "
        f"Last active project: {last_project}.{error_sentence}"
    )


def _time_of_day(hour: int) -> str:
    if 5 <= hour <= 11:
        return "morning"
    if 12 <= hour <= 17:
        return "afternoon"
    return "evening"


def _gpu_temp() -> str:
    try:
        stats = get_stats()
    except Exception:  # noqa: BLE001
        return "unknown"

    temp = stats.get("gpu_temp")
    if temp is None:
        return "unknown"

    return str(temp)


def _last_project() -> str:
    payload = _read_json(_resolve_path("data", "project_state.json"))
    value = payload.get("last_project")
    return str(value) if value not in (None, "") else "none"


def _pending_task_count() -> int:
    payload = _read_json(_resolve_path("tasks", "state.json"))
    value = payload.get("pending_count", 0)
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _coerce_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except Exception:  # noqa: BLE001
        return {}

    return payload if isinstance(payload, dict) else {}


def _resolve_path(*parts: str) -> Path:
    try:
        root = CONFIG_PATH.resolve().parent
    except Exception:  # noqa: BLE001
        root = Path.cwd()
    return root.joinpath(*parts)
