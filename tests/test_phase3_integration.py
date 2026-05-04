from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.server import app
from app.tools.registry import ToolError, ToolResult


def _intent(tool: str) -> SimpleNamespace:
    return SimpleNamespace(intent="use_tool", confidence=0.95, suggested_tool=tool, reasoning="")


def test_screenshot_via_chat() -> None:
    with TestClient(app) as client, patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch("app.server.intent_router.classify", return_value=_intent("screenshot")), patch("app.server.registry.call", return_value=ToolResult(tool="screenshot", output={"path": "/tmp/test.png", "monitor": 0})), patch("app.server.llm_client.chat", new=AsyncMock(return_value="Screenshot captured, sir.")):
        response = client.post("/chat", json={"message": "take a screenshot"})
    assert response.status_code == 200
    assert "sir" in response.json()["reply"].lower()


def test_interpreter_via_chat() -> None:
    with TestClient(app) as client, patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch("app.server.intent_router.classify", return_value=_intent("interpreter")), patch("app.server.registry.call", return_value=ToolResult(tool="interpreter", output={"output": "hello", "returncode": 0, "task": "echo hello"})), patch("app.server.llm_client.chat", new=AsyncMock(return_value="Done, sir.")):
        response = client.post("/chat", json={"message": "run echo hello"})
    assert response.status_code == 200


def test_mouse_keyboard_confirmation_gate() -> None:
    with TestClient(app) as client, patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch("app.server.intent_router.classify", return_value=_intent("mouse_keyboard")), patch("app.server.registry.call", side_effect=ToolError("Level 2. Requires user confirmation")), patch("app.server.llm_client.chat", new=AsyncMock(return_value="Need confirmation, sir.")):
        response = client.post("/chat", json={"message": "click on the start button"})
    assert response.status_code == 200
    assert isinstance(response.json()["active"], bool)


def test_vision_via_chat() -> None:
    with TestClient(app) as client, patch("app.server.check_voice", return_value=False), patch("app.server.is_active", return_value=True), patch("app.server.intent_router.classify", return_value=_intent("vision")), patch("app.server.registry.call", return_value=ToolResult(tool="vision", output={"stub": True, "source": "screen"})), patch("app.server.llm_client.chat", new=AsyncMock(return_value="I can see the screen, sir.")):
        response = client.post("/chat", json={"message": "what do you see on screen"})
    assert response.status_code == 200


def test_ws_listening_broadcast() -> None:
    intent = SimpleNamespace(intent="respond", confidence=0.9, suggested_tool="", reasoning="")
    with patch("app.server.start_hotkey_listener"), patch("app.server.register_callback"), patch("app.voice.audio_stream.voice_pipeline.start"), patch("app.voice.audio_stream.voice_pipeline.stop"), patch("app.server.tts.stop"), patch("app.server._process_stream", new=AsyncMock(return_value=None)), patch("app.server._process", new=AsyncMock(return_value=("Hello, sir.", intent))):
        with TestClient(app) as client, client.websocket_connect("/ws") as ws:
            ws.send_json({"message": "hello"})
            messages = [ws.receive_json(), ws.receive_json()]
    assert any(msg.get("type") == "reply" for msg in messages)
