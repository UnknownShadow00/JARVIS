"""Open Interpreter bridge tool."""
from __future__ import annotations

import shutil
import subprocess
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 2
DESCRIPTION = "Execute code or shell tasks via Open Interpreter"


def execute(params: dict[str, Any]) -> dict[str, Any]:
    """Execute a natural-language task with the Open Interpreter CLI."""
    task = str(params.get("task") or "").strip()
    if not task:
        return {"error": "missing task"}

    timeout = min(int(params.get("timeout") or 60), 300)

    if settings.safety.dry_run:
        return {
            "dry_run": True,
            "task": task,
            "note": "Would run Open Interpreter task: " + task,
        }

    if shutil.which("interpreter") is None:
        return {
            "error": "Open Interpreter not installed",
            "install": "pip install open-interpreter",
        }

    try:
        result = subprocess.run(
            [
                "interpreter",
                "--api_base",
                "http://localhost:11434/v1",
                "--api_key",
                "fake_key",
                "--model",
                settings.models.main,
                "--quiet",
                "-y",
                "--task",
                task,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"error": "timeout", "task": task, "timeout": timeout}

    audit.log("tool_interpreter", {"task": task, "returncode": result.returncode})
    return {
        "output": result.stdout[:3000],
        "returncode": result.returncode,
        "task": task,
    }
