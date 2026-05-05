from __future__ import annotations

import builtins


def test_speak_error_no_raise(monkeypatch) -> None:
    original_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "app.voice.tts":
            raise ImportError("tts unavailable")
        return original_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    from app.voice.error_recovery import speak_error

    speak_error("test")


def test_error_recovery_imports() -> None:
    from app.voice.error_recovery import speak_error

    assert callable(speak_error)


def test_error_phrases_defined() -> None:
    from app.voice import error_recovery

    phrases = [
        value
        for name, value in vars(error_recovery).items()
        if "PHRASE" in name and isinstance(value, str)
    ]

    assert len(phrases) >= 3
