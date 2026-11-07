from __future__ import annotations

import json
import uuid
from pathlib import Path

import pytest

from app.brain import router as router_module
from app.brain import tool_embeddings
from app.config import settings


pytestmark = pytest.mark.unit


class _FakeEmbeddingResponse:
    def __init__(self, embedding: list[float]) -> None:
        self._embedding = embedding

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, list[float]]:
        return {"embedding": self._embedding}


class _FakeEmbeddingClient:
    def __init__(self, *_args, **_kwargs) -> None:
        pass

    def __enter__(self) -> "_FakeEmbeddingClient":
        return self

    def __exit__(self, *_args) -> bool:
        return False

    def post(self, _url: str, json: dict) -> _FakeEmbeddingResponse:  # noqa: A002
        prompt = str(json["prompt"]).lower()
        if "calendar" in prompt or "schedule" in prompt:
            return _FakeEmbeddingResponse([1.0, 0.0])
        if "search" in prompt or "web" in prompt:
            return _FakeEmbeddingResponse([0.0, 1.0])
        return _FakeEmbeddingResponse([0.5, 0.5])


def _cache_path() -> Path:
    return Path("tasks") / f".tool-embeddings-test-{uuid.uuid4().hex}.json"


def test_embedding_selector_ranks_tools_with_mocked_ollama(monkeypatch) -> None:
    cache_path = _cache_path()
    descriptions = {
        "calendar": "Calendar schedule events and appointments. SAFETY_LEVEL=0",
        "web_search": "Search the web for current information. SAFETY_LEVEL=0",
    }

    monkeypatch.setattr(tool_embeddings, "CACHE_PATH", cache_path)
    monkeypatch.setattr(tool_embeddings.httpx, "Client", _FakeEmbeddingClient)
    monkeypatch.setattr(settings.routing, "embedding_model", "nomic-embed-text")
    monkeypatch.setattr(settings.routing, "embedding_top_k", 2)
    monkeypatch.setattr(tool_embeddings.audit, "log", lambda *_args, **_kwargs: None)

    try:
        selected = tool_embeddings.select_tool_by_embedding(
            "what appointments are on my schedule",
            ["web_search", "calendar"],
            descriptions,
        )

        assert selected == "calendar"
        cached = json.loads(cache_path.read_text(encoding="utf-8"))
        assert cached["model"] == "nomic-embed-text"
        assert set(cached["tools"]) == {"calendar", "web_search"}
    finally:
        cache_path.unlink(missing_ok=True)


def test_router_flag_off_keeps_existing_route(monkeypatch) -> None:
    def fail_if_called(_text: str, _candidates: list[str]) -> str:
        raise AssertionError("embedding selector should be disabled")

    monkeypatch.setattr(settings.routing, "embedding_enabled", False)
    monkeypatch.setattr(router_module, "embedding_select_tool", fail_if_called)

    result = router_module.router.classify("search latest Python release notes")

    assert result.intent == "use_tool"
    assert result.suggested_tool == "web_search"


def test_router_flag_on_can_replace_ambiguous_tool(monkeypatch) -> None:
    from app.tools import registry as registry_module

    monkeypatch.setattr(settings.routing, "embedding_enabled", True)
    monkeypatch.setattr(
        registry_module,
        "tool_descriptions",
        lambda: {"web_search": "web search", "calendar": "calendar schedule"},
    )
    monkeypatch.setattr(router_module, "embedding_select_tool", lambda _text, _candidates: "calendar")

    result = router_module.router.classify("search my schedule")

    assert result.intent == "use_tool"
    assert result.suggested_tool == "calendar"
    assert "Embedding selector chose calendar" in result.reasoning
