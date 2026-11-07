"""Phase 0 safety acceptance tests."""
from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.brain import kill_switch
from app.brain.router import RouterResult, router
from app.config import settings
from app.tools.registry import ToolError, registry


def _dummy_tool(level: int) -> ModuleType:
    mod = ModuleType(f"dummy_l{level}")
    mod.SAFETY_LEVEL = level
    mod.DESCRIPTION = f"Dummy level {level} tool."

    def execute(params):  # noqa: ANN001
        return {"ok": True, "params": params}

    mod.execute = execute  # type: ignore[attr-defined]
    return mod


def _expect_error(label: str, fn) -> bool:  # noqa: ANN001
    try:
        fn()
    except ToolError:
        print(f"{label}: PASS")
        return True
    print(f"{label}: FAIL")
    return False


def _expect(label: str, condition: bool) -> bool:
    print(f"{label}: {'PASS' if condition else 'FAIL'}")
    return condition


def run() -> None:
    original_tools = dict(registry._tools)  # noqa: SLF001
    original_dry_run = settings.safety.dry_run
    original_mode = settings.safety.approval_mode
    failures = 0

    try:
        registry._tools.update(  # noqa: SLF001
            {
                "dummy_l0": _dummy_tool(0),
                "dummy_l1": _dummy_tool(1),
                "dummy_l2": _dummy_tool(2),
                "dummy_l3": _dummy_tool(3),
            }
        )

        settings.safety.dry_run = False
        settings.safety.approval_mode = "balanced"

        for level in range(4):
            for confirmed in (False, True):
                failures += not _expect_error("legacy effect refused", lambda: registry.call(f"dummy_l{level}", confirmed=confirmed))
        settings.safety.dry_run = True
        failures += not _expect_error("dry run cannot authorize legacy effect", lambda: registry.call("dummy_l0"))

        low_conf = router._finalize(RouterResult("use_tool", 0.1, "system_stats", "low confidence"), "maybe do a thing")  # noqa: SLF001
        failures += not _expect("Low confidence falls back to confirmation", low_conf.intent == "confirm_action")

        kill_switch.reset()
        failures += not _expect("Kill switch starts active", kill_switch.is_active())
        failures += not _expect("Stop phrase triggers kill switch", kill_switch.check_voice("please stop now"))
        failures += not _expect("Kill switch deactivates JARVIS", not kill_switch.is_active())
        kill_switch.reset()
        failures += not _expect("Abort phrase triggers kill switch", kill_switch.check_voice("abort"))
        kill_switch.reset()

    finally:
        registry._tools = original_tools  # noqa: SLF001
        settings.safety.dry_run = original_dry_run
        settings.safety.approval_mode = original_mode
        kill_switch.reset()

    if failures:
        raise SystemExit(1)
    print("All safety tests passed.")


def test_safety_gates_and_kill_switch() -> None:
    run()


if __name__ == "__main__":
    run()
