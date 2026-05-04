"""App launcher tool - open or close applications by name."""
from __future__ import annotations

import re
import subprocess
from typing import Any

from app.config import settings

SAFETY_LEVEL = 0
DESCRIPTION = "Launch or close a named application on this PC."

_APP_MAP: dict[str, list[str]] = {
    "vscode": ["code"],
    "vs code": ["code"],
    "code": ["code"],
    "notepad": ["notepad"],
    "chrome": ["chrome"],
    "firefox": ["firefox"],
    "explorer": ["explorer"],
    "terminal": ["wt"],
    "powershell": ["powershell"],
    "cmd": ["cmd"],
    "task manager": ["taskmgr"],
    "taskmgr": ["taskmgr"],
    "calculator": ["calc"],
    "calc": ["calc"],
    "paint": ["mspaint"],
    "discord": ["discord"],
    "spotify": ["spotify"],
    "obs": ["obs64"],
    "blender": ["blender"],
}


def execute(params: dict[str, Any]) -> str | dict[str, str]:
    """Open or close a known application by name."""
    action = str(params.get("action", "open")).lower().strip()
    app_name = _extract_app_name(params)

    if not app_name:
        return {"error": "No app name provided."}

    if settings.safety.dry_run:
        return f"[DRY RUN] Would {action} '{app_name}'."

    if action == "close":
        return close_app(app_name)
    return open_app(app_name)


def open_app(app_name: str) -> str | dict[str, str]:
    """Open an application by friendly name."""
    normalized = app_name.lower().strip()
    if normalized not in _APP_MAP:
        return {"error": f"Unknown app: {normalized}"}
    cmd = _APP_MAP[normalized]

    try:
        subprocess.Popen(cmd, shell=True)  # noqa: S602 - intentional app launch
        return f"Launched '{normalized}', sir."
    except Exception as exc:
        return f"Failed to launch '{normalized}': {exc}"


def close_app(app_name: str) -> str:
    """Close an application by process image name."""
    normalized = app_name.lower().strip()
    executable = _APP_MAP.get(normalized, [normalized])[0]
    image = f"{executable}.exe" if "." not in executable else executable

    try:
        subprocess.run(["taskkill", "/IM", image, "/F"], capture_output=True, text=True, check=False)
        return f"Closed '{normalized}', sir."
    except Exception as exc:
        return f"Failed to close '{normalized}': {exc}"


def _extract_app_name(params: dict[str, Any]) -> str:
    explicit = str(params.get("app") or params.get("name") or "").lower().strip()
    if explicit:
        return explicit

    query = str(params.get("query", "")).lower().replace("visual studio code", "vscode")
    for app_name in sorted(_APP_MAP, key=len, reverse=True):
        if re.search(rf"\b{re.escape(app_name)}\b", query):
            return app_name

    for verb in ("open", "launch", "start", "close"):
        query = re.sub(rf"\b{verb}\b", "", query)
    return query.strip(" .")
