from __future__ import annotations

import importlib.util
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 1
DESCRIPTION = "Browser-use agent stub for browser automation plans."
ACTION_TAG = "[ACTION:BROWSER_AGENT:{goal}]"


def execute(params: dict[str, Any]) -> dict[str, Any]:
    goal = str(params.get("goal") or params.get("query") or "").strip()
    if not goal:
        return {"error": "goal required", "action_tag": ACTION_TAG}

    dependency_available = importlib.util.find_spec("browser_use") is not None
    if settings.safety.dry_run or not dependency_available:
        result = {
            "dry_run": True,
            "available": dependency_available,
            "goal": goal,
            "action_tag": ACTION_TAG.format(goal=goal),
            "note": "Would run browser-use agent for this goal.",
        }
        if not dependency_available:
            result["remediation"] = "Install browser-use only when live browser-agent automation is approved."
        audit.log("browser_use_stub", result)
        return result

    return {
        "available": True,
        "dry_run": True,
        "goal": goal,
        "note": "Live browser-use execution is intentionally deferred; stub returned a plan only.",
    }
