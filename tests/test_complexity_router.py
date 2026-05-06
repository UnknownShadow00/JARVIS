from __future__ import annotations

from app.brain.complexity_router import complexity_router


def test_deep_reasoning_uses_thinking_model(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("app.brain.complexity_router.settings.models.main", "qwen3-nothink")

    decision = complexity_router.decide("debug this failing audio pipeline", "deep_reasoning")

    assert decision.tier == "deep"
    assert decision.think is True
    assert decision.model == "qwen3:14b"


def test_trivial_response_uses_router_model(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("app.brain.complexity_router.settings.models.router", "gemma3:4b")

    decision = complexity_router.decide("what time is it", "respond")

    assert decision.tier == "trivial"
    assert decision.model == "gemma3:4b"
    assert decision.think is False
