from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

import httpx
import yaml

from app import config_check as cc
from app.config import load_settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_temp_config(raw: dict, name: str) -> Path:
    path = PROJECT_ROOT / "tasks" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    return path


def test_example_config_matches_schema() -> None:
    example = load_settings(PROJECT_ROOT / "config.yaml.example")

    assert example.models.main == "qwen3-nothink"
    assert example.voice.stt_model == "large-v3-turbo"
    assert example.voice.tts_engine == "chatterbox"
    assert example.voice.dictation_enabled is True
    assert example.voice.dictation_hotkey == "ctrl+shift+space"
    assert example.voice.dictation_type_out is False
    assert example.server.host == "127.0.0.1"
    assert example.server.remote_access_enabled is False
    assert example.server.enable_voice_on_startup is False
    assert example.server.enable_hotkey_listener is False
    assert example.resource_mode.enabled is True
    assert example.resource_mode.idle_timeout_minutes == 10
    assert example.resource_mode.deep_sleep_timeout_minutes == 60
    assert example.resource_mode.keep_wake_listener_in_light_sleep is True
    assert example.resource_mode.keep_wake_listener_in_deep_sleep is False
    assert example.resource_mode.stop_server_on_auto_deep_sleep is True
    assert example.memory.graphiti_enabled is False
    assert example.memory.neo4j_uri == "bolt://localhost:7687"
    assert example.memory.neo4j_user == "neo4j"
    assert example.memory.neo4j_password_env == "NEO4J_PASSWORD"
    assert example.tools.obsidian_enabled is False
    assert example.tools.obsidian_vault_path == "./jarvis-vault"
    assert example.routing.embedding_enabled is False
    assert example.routing.embedding_model == "nomic-embed-text"
    assert example.routing.embedding_top_k == 3


def test_non_loopback_host_requires_remote_access_flag() -> None:
    raw = yaml.safe_load((PROJECT_ROOT / "config.yaml.example").read_text(encoding="utf-8"))
    raw["server"]["host"] = "0.0.0.0"
    raw["server"]["remote_access_enabled"] = False
    config_path = _write_temp_config(raw, "tmp_config_reject_remote.yaml")

    try:
        try:
            load_settings(config_path)
        except ValueError as exc:
            assert "server.host must be localhost/loopback" in str(exc)
        else:
            raise AssertionError("0.0.0.0 should be rejected unless remote access is enabled")
    finally:
        config_path.unlink(missing_ok=True)


def test_non_loopback_host_allowed_when_remote_access_enabled() -> None:
    raw = yaml.safe_load((PROJECT_ROOT / "config.yaml.example").read_text(encoding="utf-8"))
    raw["server"]["host"] = "0.0.0.0"
    raw["server"]["remote_access_enabled"] = True
    config_path = _write_temp_config(raw, "tmp_config_allow_remote.yaml")

    try:
        loaded = load_settings(config_path)
    finally:
        config_path.unlink(missing_ok=True)

    assert loaded.server.host == "0.0.0.0"
    assert loaded.server.remote_access_enabled is True


def test_ollama_base_url_can_be_overridden_for_container(monkeypatch) -> None:
    monkeypatch.setenv("JARVIS_OLLAMA_BASE_URL", "http://ollama:11434")

    loaded = load_settings(PROJECT_ROOT / "config.yaml.example")

    assert loaded.models.ollama_base_url == "http://ollama:11434"


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
