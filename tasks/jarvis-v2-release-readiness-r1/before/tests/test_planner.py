from __future__ import annotations

from app.brain.llm_client import OllamaConnectionError, llm_client
from app.brain.planner import TaskPlan, planner


def test_task_plan_fields() -> None:
    plan = TaskPlan(goal="test", steps=["a"], tool_hints=[], estimated_turns=1)
    assert plan.goal == "test"


def test_fallback_mode(monkeypatch) -> None:
    def raise_offline(*args, **kwargs):
        raise OllamaConnectionError("offline")

    monkeypatch.setattr(llm_client, "chat", raise_offline)
    result = planner.plan("do something")
    assert result.steps == ["do something"] and result.estimated_turns == 1


def test_llm_mode_valid_json(monkeypatch) -> None:
    def return_json(*args, **kwargs):
        return (
            '{"goal":"do something","steps":["step 1","step 2"],'
            '"tool_hints":["shell"],"estimated_turns":2}'
        )

    monkeypatch.setattr(llm_client, "chat", return_json)
    result = planner.plan("do something")
    assert len(result.steps) > 0


def test_llm_mode_bad_json(monkeypatch) -> None:
    monkeypatch.setattr(llm_client, "chat", lambda *args, **kwargs: "not json at all")
    result = planner.plan("do something")
    assert result.steps == ["do something"]


def test_singleton() -> None:
    from app.brain.planner import planner as p1, planner as p2

    assert p1 is p2
