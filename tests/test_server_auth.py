import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import API_TOKEN_ENV, load_settings, settings
from app.server import app

client = TestClient(app)


@pytest.fixture
def api_token(monkeypatch) -> str:
    token = "test-secret-token"
    monkeypatch.setattr(settings.server, "api_token", token)
    return token


def test_auth_disabled_by_default() -> None:
    assert settings.server.api_token == ""
    response = client.get("/tasks")
    assert response.status_code == 200


def test_missing_token_rejected(api_token: str) -> None:
    response = client.get("/tasks")
    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"


def test_wrong_token_rejected(api_token: str) -> None:
    response = client.get("/tasks", headers={"Authorization": "Bearer wrong-token"})
    assert response.status_code == 401


def test_malformed_header_rejected(api_token: str) -> None:
    response = client.get("/tasks", headers={"Authorization": api_token})
    assert response.status_code == 401


def test_valid_token_accepted(api_token: str) -> None:
    response = client.get("/tasks", headers={"Authorization": f"Bearer {api_token}"})
    assert response.status_code == 200


def test_health_exempt(api_token: str) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ws_rejected_without_token(api_token: str) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws"):
            pass


def test_ws_rejected_with_wrong_token(api_token: str) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws?token=wrong-token"):
            pass


def test_ws_accepted_with_query_token(api_token: str) -> None:
    with client.websocket_connect(f"/ws?token={api_token}"):
        pass


def test_ws_accepted_with_bearer_header(api_token: str) -> None:
    with client.websocket_connect("/ws", headers={"Authorization": f"Bearer {api_token}"}):
        pass


def test_ue5_ws_rejected_without_token(api_token: str) -> None:
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ue5"):
            pass


def test_env_override_sets_api_token(monkeypatch) -> None:
    monkeypatch.setenv(API_TOKEN_ENV, "env-secret")
    loaded = load_settings()
    assert loaded.server.api_token == "env-secret"
