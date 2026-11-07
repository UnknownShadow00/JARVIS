from __future__ import annotations

import importlib.util
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 0
CONTROL_SAFETY_LEVEL = 1
DESCRIPTION = "TP-Link Kasa status/control stub. Read/status are Level 0; control actions are Level 1 semantics."
READ_ACTIONS = {"status", "discover"}
CONTROL_ACTIONS = {"on", "off", "toggle", "set_brightness"}


def execute(params: dict[str, Any]) -> dict[str, Any]:
    action = str(params.get("action", "status")).lower().strip()
    available = importlib.util.find_spec("kasa") is not None

    if action not in READ_ACTIONS | CONTROL_ACTIONS:
        return {"error": f"unknown action: {action}", "allowed": sorted(READ_ACTIONS | CONTROL_ACTIONS)}

    result = {
        "available": available,
        "action": action,
        "safety_level": CONTROL_SAFETY_LEVEL if action in CONTROL_ACTIONS else SAFETY_LEVEL,
        "dry_run": True,
    }

    if not available:
        result["remediation"] = "Install python-kasa only when live Kasa device control is approved."
    elif settings.safety.dry_run or action in CONTROL_ACTIONS:
        result["note"] = "Would query/control Kasa device; live control is deferred in this stub."
    else:
        result["note"] = "python-kasa is available, but this phase only reports readiness."

    audit.log("kasa_stub", result)
    return result
