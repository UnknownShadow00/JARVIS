from __future__ import annotations

import datetime as dt
from types import SimpleNamespace

from fastapi.testclient import TestClient
import yaml

from app.config import settings
from app.memory import graphiti_client as graphiti_module
from app.memory.graphiti_client import GraphitiClient
from app.server import app


class _FakeEpisodeType:
    text = "text"


class _FakeGraphiti:
    instances: list["_FakeGraphiti"] = []

    def __init__(self, uri: str, user: str, password: str) -> None:
        self.uri = uri
        self.user = user
        self.password = password
        self.episodes: list[dict] = []
        _FakeGraphiti.instances.append(self)

    async def add_episode(self, **kwargs):
        self.episodes.append(kwargs)
        return {"episode": kwargs["name"]}

    async def search(self, text: str, num_results: int):
        return [SimpleNamespace(text=text, limit=num_results)]

    async def add_entity(self, name: str, type: str):  # noqa: A002
        return {"name": name, "type": type}


def test_graphiti_disabled_path_returns_stubs(monkeypatch) -> None:
    monkeypatch.setattr(settings.memory, "graphiti_enabled", False)
    client = GraphitiClient()

    assert client.add_episode("hello", "unit")["stub"] is True
    assert client.query("hello")["results"] == []
    assert client.add_entity("JARVIS", "Agent")["stub"] is True
    assert client.is_enabled() is False


def test_graphiti_enabled_path_uses_env_password_and_mocks(monkeypatch) -> None:
    events: list[tuple[str, dict]] = []
    _FakeGraphiti.instances.clear()
    monkeypatch.setattr(settings.memory, "graphiti_enabled", True)
    monkeypatch.setattr(settings.memory, "neo4j_uri", "bolt://test:7687")
    monkeypatch.setattr(settings.memory, "neo4j_user", "neo4j")
    monkeypatch.setattr(settings.memory, "neo4j_password_env", "NEO4J_PASSWORD")
    monkeypatch.setenv("NEO4J_PASSWORD", "env-only")
    monkeypatch.setattr(graphiti_module, "GRAPHITI_AVAILABLE", True)
    monkeypatch.setattr(graphiti_module, "Graphiti", _FakeGraphiti)
    monkeypatch.setattr(graphiti_module, "EpisodeType", _FakeEpisodeType)
    monkeypatch.setattr(graphiti_module.audit, "log", lambda event, data: events.append((event, data)))

    client = GraphitiClient()
    timestamp = dt.datetime(2026, 5, 14, 12, 0, tzinfo=dt.UTC)
    added = client.add_episode("private graph text", "unit-test", timestamp)
    queried = client.query("graph question", limit=3)
    entity = client.add_entity("JARVIS", "Agent")

    assert added == {"added": True, "result": {"episode": "unit-test"}}
    assert queried == {"results": [{"text": "graph question", "limit": 3}], "limit": 3}
    assert entity == {"added": True, "result": {"name": "JARVIS", "type": "Agent"}}
    assert _FakeGraphiti.instances[0].password == "env-only"
    assert _FakeGraphiti.instances[0].episodes[0]["source"] == "text"
    assert events[0] == (
        "graphiti_add_episode",
        {"chars": 18, "source": "unit-test", "ts": "2026-05-14T12:00:00+00:00"},
    )


def test_graphiti_server_endpoints_503_when_disabled(monkeypatch) -> None:
    monkeypatch.setattr("app.server.graphiti_client.is_enabled", lambda: False)

    with TestClient(app) as client:
        add_response = client.post("/memory/graph/add", json={"text": "hello"})
        query_response = client.post("/memory/graph/query", json={"text": "hello"})

    assert add_response.status_code == 503
    assert query_response.status_code == 503
    assert add_response.json() == {"error": "graphiti_disabled"}
    assert query_response.json() == {"error": "graphiti_disabled"}


def test_graphiti_server_endpoints_use_client_when_enabled(monkeypatch) -> None:
    monkeypatch.setattr("app.server.graphiti_client.is_enabled", lambda: True)
    monkeypatch.setattr(
        "app.server.graphiti_client.add_episode",
        lambda text, source, ts: {"added": True, "text": text, "source": source, "ts": ts.isoformat() if ts else None},
    )
    monkeypatch.setattr("app.server.graphiti_client.query", lambda text, limit: {"results": [text], "limit": limit})

    with TestClient(app) as client:
        add_response = client.post(
            "/memory/graph/add",
            json={"text": "hello graph", "source": "test", "ts": "2026-05-14T12:00:00Z"},
        )
        query_response = client.post("/memory/graph/query", json={"text": "hello", "limit": 2})

    assert add_response.status_code == 200
    assert add_response.json() == {
        "added": True,
        "text": "hello graph",
        "source": "test",
        "ts": "2026-05-14T12:00:00+00:00",
    }
    assert query_response.json() == {"results": ["hello"], "limit": 2}


def test_neo4j_compose_service_uses_env_password() -> None:
    compose = yaml.safe_load(open("docker-compose.yml", encoding="utf-8"))
    neo4j = compose["services"]["neo4j"]

    assert neo4j["image"].startswith("neo4j:5")
    assert "127.0.0.1:7474:7474" in neo4j["ports"]
    assert "127.0.0.1:7687:7687" in neo4j["ports"]
    assert "neo4j_data:/data" in neo4j["volumes"]
    assert "NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}" in neo4j["environment"]
