from __future__ import annotations

from app.computer import screenshot
from app.logs.audit import audit


class ActionVerifier:
    def verify(self, action: str, expected: str | None = None) -> dict:
        try:
            path = screenshot.capture()
            audit.log("action_verify", {"action": action, "screenshot": path})
        except Exception as e:  # noqa: BLE001
            return {"verified": False, "error": str(e)}

        if expected is None:
            return {"verified": True, "screenshot": path, "note": "no expectation set"}

        return {
            "verified": None,
            "screenshot": path,
            "expected": expected,
            "note": "visual verification requires Phase 4 VLM",
        }


verifier = ActionVerifier()
