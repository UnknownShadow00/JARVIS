from __future__ import annotations

from unittest.mock import Mock

import httpx

from app import config_check as cc


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
