from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.server import app
from app.tools.registry import ToolResult

client = TestClient(app)


def test_health_returns_200() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_respond_intent() -> None:
    intent = SimpleNamespace(intent="respond", confidence=0.9, suggested_tool="", reasoning="")
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.try_direct_reply", return_value=None), patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="It is 3pm sir.")
    ):
        response = client.post("/chat", json={"message": "what time is it"})
    assert response.status_code == 200
    assert response.json()["reply"] == "It is 3pm sir."


def test_chat_browser_tool() -> None:
    intent = SimpleNamespace(intent="use_tool", confidence=0.95, suggested_tool="browser", reasoning="")
    result = ToolResult(tool="browser", output="opened google", dry_run=False)
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.registry.call", return_value=result), patch(
        "app.server.llm_client.chat", new=AsyncMock(return_value="Opened, sir.")
    ):
        response = client.post("/chat", json={"message": "open google"})
    assert response.status_code == 200
    assert "reply" in response.json()


def test_chat_dry_run() -> None:
    intent = SimpleNamespace(intent="use_tool", confidence=0.95, suggested_tool="browser", reasoning="")
    result = ToolResult(tool="browser", output="noop", dry_run=True)
    with patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch(
        "app.brain.router.router.classify", return_value=intent
    ), patch("app.server.registry.call", return_value=result), patch("app.config.settings.safety.dry_run", True):
        response = client.post("/chat", json={"message": "open google"})
    assert response.status_code == 200
    assert "dry" in response.json()["reply"].lower()


def test_health_tools_route() -> None:
    expected = {"ollama": True, "piper": False}
    with patch("app.server.check_tools", return_value=expected):
        response = client.get("/health/tools")
    assert response.status_code == 200
    assert any(isinstance(v, bool) for v in response.json().values())


def test_chat_missing_message() -> None:
    response = client.post("/chat", json={})
    assert response.status_code == 422
