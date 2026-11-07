"""Computer control safety gate."""
from __future__ import annotations

from app.config import settings
from app.logs.audit import audit


class ComputerSafetyGate:
    def check(self, action: str, safety_level: int, confirmed: bool = False) -> tuple[bool, str]:
        if safety_level >= 3:
            audit.log("computer_safety_check", {"action": action, "level": safety_level, "allowed": False})
            return False, "blocked"

        if safety_level == 2 and not confirmed:
            audit.log("computer_safety_check", {"action": action, "level": safety_level, "allowed": False})
            return False, "confirmation_required"

        if settings.safety.dry_run and safety_level >= 1:
            audit.log("computer_safety_check", {"action": action, "level": safety_level, "allowed": False})
            return False, "dry_run_active"

        audit.log("computer_safety_check", {"action": action, "level": safety_level, "confirmed": confirmed, "allowed": True})
        return True, "ok"

    def require_confirmation(self, action: str, params: dict) -> str:
        return f"That would {action} with params {params}, sir. Shall I proceed?"

    def is_safe_for_auto(self, safety_level: int) -> bool:
        return safety_level <= 1


safety_gate = ComputerSafetyGate()
