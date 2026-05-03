from __future__ import annotations

import subprocess
from types import SimpleNamespace

from app.config import settings
from app.tools import interpreter


def test_safety_level() -> None:
    assert interpreter.SAFETY_LEVEL == 2


def test_dry_run(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = interpreter.execute({"task": "echo hi"})
    assert result["dry_run"] is True


def test_not_installed(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(interpreter.shutil, "which", lambda _: None)
    result = interpreter.execute({"task": "echo hi"})
    assert "error" in result
    assert "not installed" in result["error"]


def test_timeout(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(interpreter.shutil, "which", lambda _: "/usr/bin/interpreter")

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("interpreter", 30)

    monkeypatch.setattr(interpreter.subprocess, "run", raise_timeout)
    result = interpreter.execute({"task": "sleep forever", "timeout": 30})
    assert result["error"] == "timeout"


def test_success(monkeypatch) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    monkeypatch.setattr(interpreter.shutil, "which", lambda _: "/usr/bin/interpreter")
    monkeypatch.setattr(
        interpreter.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="Done."),
    )
    result = interpreter.execute({"task": "echo hi"})
    assert result["returncode"] == 0


def test_registered() -> None:
    from app.tools.registry import registry

    assert "interpreter" in registry.TOOLS
