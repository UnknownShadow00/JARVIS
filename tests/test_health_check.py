from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import httpx
from fastapi.testclient import TestClient

from app.server import app
from app.tools import health_check


def test_ollama_down(monkeypatch) -> None:
    def raise_error(*args, **kwargs):
        raise httpx.ConnectError("down")

    monkeypatch.setattr(health_check.httpx, "get", raise_error)
    assert health_check.check_tools()["ollama"] is False


def test_ollama_up(monkeypatch) -> None:
    monkeypatch.setattr(health_check.httpx, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200))
    assert health_check.check_tools()["ollama"] is True


def test_piper_found(monkeypatch) -> None:
    monkeypatch.setattr(health_check.shutil, "which", lambda name: "/usr/bin/piper" if "piper" in name else None)
    assert health_check.check_tools()["piper"] is True


def test_piper_missing(monkeypatch) -> None:
    monkeypatch.setattr(health_check.shutil, "which", lambda name: None)
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    assert health_check.check_tools()["piper"] is False


def test_interpreter_missing(monkeypatch) -> None:
    monkeypatch.setattr(health_check.shutil, "which", lambda name: None)
    assert health_check.check_tools()["interpreter"] is False


def test_builtin_wake_model_is_available(monkeypatch) -> None:
    monkeypatch.setattr(health_check.settings.voice, "wake_word_model", "hey_jarvis")
    monkeypatch.setattr(health_check.httpx, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200))
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    assert health_check.check_tools()["wake_model"] is True


def test_custom_wake_model_path_missing(monkeypatch) -> None:
    monkeypatch.setattr(health_check.settings.voice, "wake_word_model", "./models/custom.onnx")
    monkeypatch.setattr(health_check.httpx, "get", lambda *args, **kwargs: SimpleNamespace(status_code=200))
    monkeypatch.setattr(Path, "is_file", lambda self: False)
    assert health_check.check_tools()["wake_model"] is False


def test_server_route(monkeypatch) -> None:
    expected = {"ollama": True, "piper": True, "interpreter": True, "wake_model": True}
    monkeypatch.setattr("app.server.check_tools", lambda: expected)
    client = TestClient(app)
    response = client.get("/health/tools")
    assert response.status_code == 200
    assert response.json() == expected
