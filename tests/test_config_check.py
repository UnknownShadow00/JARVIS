from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import httpx

from app import config_check as cc
from app.config import load_settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_example_config_matches_schema() -> None:
    example = load_settings(PROJECT_ROOT / "config.yaml.example")

    assert example.models.main == "qwen3:14b"
    assert example.voice.stt_model == "medium.en"
    assert example.voice.tts_engine == "piper"


def test_builtin_wake_model_is_available(monkeypatch) -> None:
    monkeypatch.setattr(cc.settings.voice, "wake_word_model", "hey_jarvis")
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: Mock(status_code=200))
    monkeypatch.setattr(cc.Path, "is_file", lambda _: False)
    assert cc.check_startup()["wake_model"] is True


def test_custom_wake_model_path_missing(monkeypatch) -> None:
    monkeypatch.setattr(cc.settings.voice, "wake_word_model", "./models/custom.onnx")
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: Mock(status_code=200))
    monkeypatch.setattr(cc.Path, "is_file", lambda _: False)
    assert cc.check_startup()["wake_model"] is False


def test_piper_binary_missing(monkeypatch) -> None:
    monkeypatch.setattr(cc.shutil, "which", lambda _: None)
    monkeypatch.setattr(cc.Path, "is_file", lambda _: False)
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: Mock(status_code=200))
    assert cc.check_startup()["piper_binary"] is False


def test_piper_model_missing(monkeypatch) -> None:
    monkeypatch.setattr(cc.settings.voice, "wake_word_model", "")
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: Mock(status_code=200))
    monkeypatch.setattr(cc.Path, "is_file", lambda _: False)
    assert cc.check_startup()["piper_model"] is False


def test_ollama_unreachable(monkeypatch) -> None:
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: (_ for _ in ()).throw(httpx.ConnectError("offline")))
    assert cc.check_startup()["ollama_reachable"] is False


def test_all_pass(monkeypatch) -> None:
    monkeypatch.setattr(cc.shutil, "which", lambda name: "piper" if name == "piper" else None)
    monkeypatch.setattr(cc.Path, "is_file", lambda _: True)
    monkeypatch.setattr(cc.httpx, "get", lambda *args, **kwargs: Mock(status_code=200))
    assert all(cc.check_startup().values())
