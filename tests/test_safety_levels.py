"""Safety level boundary tests for confidence, confirmation, blocking, and dry-run."""
from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.brain.router import RouterResult, router
from app.tools.registry import ToolError, ToolRegistry


def _make_registry(*, safety_level: int, execute: Mock) -> ToolRegistry:
    registry = ToolRegistry.__new__(ToolRegistry)
    module = SimpleNamespace(
        SAFETY_LEVEL=safety_level,
        DESCRIPTION=f"Level {safety_level} fake tool",
        execute=execute,
    )
    registry._tools = {"fake_tool": module}
    registry.TOOLS = {"fake_tool": module.execute}
    return registry


def _run_action(
    monkeypatch: pytest.MonkeyPatch,
    *,
    safety_level: int,
    confidence: float,
    dry_run: bool = False,
):
    monkeypatch.setattr("app.brain.router.audit.log", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.tools.registry.audit.log", lambda *args, **kwargs: None)
    monkeypatch.setattr("app.brain.router.settings.safety.confidence_threshold", 0.75)
    monkeypatch.setattr("app.tools.registry.settings.safety.approval_mode", "balanced")
    monkeypatch.setattr("app.tools.registry.settings.safety.dry_run", dry_run)

    execute = Mock(return_value="tool executed")
    registry = _make_registry(safety_level=safety_level, execute=execute)
    intent = router._finalize(  # noqa: SLF001
        RouterResult("use_tool", confidence, "fake_tool", "test"),
        "run fake tool",
    )

    if intent.intent != "use_tool":
        return {"intent": intent, "execute": execute, "result": None}

    result = registry.call("fake_tool", {"value": 1})
    return {"intent": intent, "execute": execute, "result": result}


def test_level0_always_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    run = _run_action(monkeypatch, safety_level=0, confidence=1.0)

    assert run["intent"].intent == "use_tool"
    assert run["result"].output == "tool executed"
    assert run["result"].dry_run is False
    run["execute"].assert_called_once_with({"value": 1})


def test_level0_executes_dry_run(monkeypatch: pytest.MonkeyPatch) -> None:
    run = _run_action(monkeypatch, safety_level=0, confidence=1.0, dry_run=True)

    assert run["intent"].intent == "use_tool"
    assert run["result"].dry_run is True
    assert "[DRY RUN]" in run["result"].output
    run["execute"].assert_not_called()


def test_level1_high_confidence_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    run = _run_action(monkeypatch, safety_level=1, confidence=0.9)

    assert run["intent"].intent == "use_tool"
    assert run["result"].output == "tool executed"
    run["execute"].assert_called_once_with({"value": 1})


def test_level1_low_confidence_requires_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    run = _run_action(monkeypatch, safety_level=1, confidence=0.5)

    assert run["intent"].intent == "confirm_action"
    assert run["result"] is None
    run["execute"].assert_not_called()


def test_level2_always_requires_confirm(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ToolError, match="Requires user confirmation"):
        _run_action(monkeypatch, safety_level=2, confidence=1.0)


def test_level3_never_executes(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ToolError, match="Level 3"):
        _run_action(monkeypatch, safety_level=3, confidence=1.0)


def test_level3_dry_run_still_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    with pytest.raises(ToolError, match="Level 3"):
        _run_action(monkeypatch, safety_level=3, confidence=1.0, dry_run=True)


def test_dry_run_prevents_execution(monkeypatch: pytest.MonkeyPatch) -> None:
    run = _run_action(monkeypatch, safety_level=1, confidence=0.95, dry_run=True)

    assert run["intent"].intent == "use_tool"
    assert run["result"].dry_run is True
    assert "[DRY RUN]" in run["result"].output
    run["execute"].assert_not_called()
