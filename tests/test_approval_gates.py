from unittest.mock import patch

from fastapi.testclient import TestClient

from app.server import _is_confirmation_required_error, _pending_confirmations, app
from app.tools.registry import ToolError, ToolResult


def setup_function() -> None:
    _pending_confirmations.clear()


def teardown_function() -> None:
    _pending_confirmations.clear()


def test_pending_dict_starts_empty() -> None:
    assert _pending_confirmations == {}


def test_is_confirmation_error_true() -> None:
    assert _is_confirmation_required_error(ToolError("Tool requires user confirmation")) is True


def test_is_confirmation_error_false() -> None:
    assert _is_confirmation_required_error(ToolError("blocked")) is False


def test_confirm_unknown_request_id() -> None:
    with TestClient(app) as client:
        response = client.post("/confirm/badid")
    assert response.status_code == 404
    assert response.json()["error"] == "Unknown or expired request"


def test_confirm_known_request_id() -> None:
    _pending_confirmations["abc12345"] = {"tool": "shell", "params": {"command": "echo hi"}}
    with patch("app.server.registry.call", return_value=ToolResult(tool="shell", output="hi")) as mock_call:
        with TestClient(app) as client:
            response = client.post("/confirm/abc12345")
    assert response.status_code == 200
    assert response.json()["confirmed"] is True
    assert response.json()["tool"] == "shell"
    assert response.json()["output"] == "hi"
    mock_call.assert_called_once_with("shell", {"command": "echo hi"}, confirmed=True)
