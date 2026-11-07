from __future__ import annotations

import shutil
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "CLI-Anything wrapper stub for OBS, FFmpeg, Blender, and generic command readiness."

KNOWN_COMMANDS: dict[str, tuple[str, ...]] = {
    "obs": ("obs64", "obs"),
    "ffmpeg": ("ffmpeg",),
    "blender": ("blender",),
}


def execute(params: dict[str, Any]) -> dict[str, Any]:
    action = str(params.get("action", "status")).lower().strip()
    target = str(params.get("target", "")).lower().strip()

    if action == "status":
        return readiness(target or None)

    result = {
        "dry_run": True,
        "action": action,
        "target": target,
        "command": params.get("command"),
        "note": "Would route through CLI-Anything harness after explicit approval.",
        "global_dry_run": settings.safety.dry_run,
    }
    audit.log("cli_anything_stub", result)
    return result


def readiness(target: str | None = None) -> dict[str, Any]:
    targets = [target] if target else sorted(KNOWN_COMMANDS)
    checks = {}
    for name in targets:
        names = KNOWN_COMMANDS.get(name, (name,))
        found = next((path for candidate in names if (path := shutil.which(candidate))), None)
        checks[name] = {"available": found is not None, "path": found, "candidates": names}
    return {"stub": True, "checks": checks}
