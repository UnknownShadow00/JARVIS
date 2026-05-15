from __future__ import annotations

import shutil
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app import boot
from app.memory import project_indexer
from app.tools import browser_use, cad, kasa, mcp_client
from app.tools.cli import readiness as cli_readiness
from app.tools.registry import registry


@pytest.mark.asyncio
async def test_boot_prefetch_context(monkeypatch) -> None:
    monkeypatch.setattr(boot, "pending_task_count", lambda: 4)
    monkeypatch.setattr(boot, "last_project_name", lambda: "voice")
    monkeypatch.setattr(boot, "recent_error_count", lambda: 2)
    monkeypatch.setattr("app.tools.system_stats.get_stats", lambda: {"gpu_temp": 55})

    context = await boot.prefetch_boot_context()

    assert context["pending_tasks"] == 4
    assert context["last_project"] == "voice"
    assert context["recent_errors"] == 2
    assert context["gpu_temp"] == 55


def test_project_indexer_disabled_stub(monkeypatch) -> None:
    monkeypatch.setattr(project_indexer.settings.memory, "chromadb_enabled", False)

    result = project_indexer.index_configured_projects()

    assert result["stub"] is True
    assert result["indexed"] == 0


def test_project_indexer_indexes_configured_text_path(monkeypatch) -> None:
    scratch = Path("tasks/.phase8_indexer_test")
    scratch.mkdir(parents=True, exist_ok=True)
    doc = scratch / "note.md"
    doc.write_text("hello project", encoding="utf-8")
    rag = Mock()
    rag.index.return_value = {"indexed": 1, "total": 1}

    try:
        monkeypatch.setattr(project_indexer.settings.memory, "chromadb_enabled", True)
        monkeypatch.setattr(project_indexer.settings.memory, "index_paths", [str(scratch)])
        monkeypatch.setattr(project_indexer.rag_module, "CHROMADB_AVAILABLE", True)
        monkeypatch.setattr(project_indexer.rag_module, "rag_client", rag)

        result = project_indexer.index_configured_projects()
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    rag.index.assert_called_once()
    assert result["indexed"] == 1


def test_mcp_client_rejects_unlisted_server() -> None:
    result = mcp_client.execute({"action": "call", "server": "unknown"})

    assert result["error"] == "server_not_whitelisted"


def test_browser_use_missing_dependency(monkeypatch) -> None:
    monkeypatch.setattr(browser_use.importlib.util, "find_spec", lambda name: None)

    result = browser_use.execute({"goal": "check a site"})

    assert result["dry_run"] is True
    assert result["available"] is False
    assert "BROWSER_AGENT" in result["action_tag"]


def test_kasa_status_is_level_zero_missing_dependency(monkeypatch) -> None:
    monkeypatch.setattr(kasa.importlib.util, "find_spec", lambda name: None)

    result = kasa.execute({"action": "status"})

    assert kasa.SAFETY_LEVEL == 0
    assert result["safety_level"] == 0
    assert result["available"] is False


def test_kasa_control_reports_level_one_semantics(monkeypatch) -> None:
    monkeypatch.setattr(kasa.importlib.util, "find_spec", lambda name: SimpleNamespace())

    result = kasa.execute({"action": "on"})

    assert result["safety_level"] == 1
    assert result["dry_run"] is True


def test_cad_returns_dry_run_plan(monkeypatch) -> None:
    monkeypatch.setattr(cad.importlib.util, "find_spec", lambda name: None)
    monkeypatch.setattr(cad.shutil, "which", lambda name: None)

    result = cad.execute({"prompt": "bracket"})

    assert cad.SAFETY_LEVEL == 2
    assert result["dry_run"] is True
    assert result["plan"]
    assert result["orcaslicer_available"] is False


def test_cli_readiness_checks_known_targets(monkeypatch) -> None:
    monkeypatch.setattr("app.tools.cli.shutil.which", lambda name: "ffmpeg.exe" if name == "ffmpeg" else None)

    result = cli_readiness("ffmpeg")

    assert result["checks"]["ffmpeg"]["available"] is True


def test_phase8_tools_registered() -> None:
    for name in ("browser_use", "cad", "kasa", "mcp_client", "cli", "obsidian"):
        assert name in registry.TOOLS
