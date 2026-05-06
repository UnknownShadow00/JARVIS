from __future__ import annotations

from pathlib import Path
from typing import Any

from app.config import settings
from app.logs.audit import audit
from app.memory import rag_client as rag_module

TEXT_SUFFIXES = {
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
MAX_FILE_BYTES = 250_000


def index_configured_projects() -> dict[str, Any]:
    """Index configured project/doc paths into RAG when ChromaDB is enabled."""
    if not settings.memory.chromadb_enabled:
        return _stub("disabled", "settings.memory.chromadb_enabled is false")

    if not rag_module.CHROMADB_AVAILABLE:
        return _stub("missing_dependency", "ChromaDB is not installed")

    documents: list[str] = []
    ids: list[str] = []
    skipped: list[str] = []

    for configured in settings.memory.index_paths:
        root = _resolve_path(configured)
        if not root.exists():
            skipped.append(str(root))
            continue

        for path in _iter_indexable_files(root):
            content = _read_text(path)
            if content is None:
                skipped.append(str(path))
                continue
            documents.append(content)
            ids.append(str(path))

    if not documents:
        return {"indexed": 0, "skipped": skipped, "enabled": True}

    result = rag_module.rag_client.index(documents, ids)
    result.update({"enabled": True, "paths": list(settings.memory.index_paths), "skipped": skipped})
    audit.log("project_indexer_complete", {"indexed": len(documents), "skipped": len(skipped)})
    return result


def status() -> dict[str, Any]:
    return {
        "enabled": settings.memory.chromadb_enabled,
        "chromadb_available": rag_module.CHROMADB_AVAILABLE,
        "paths": list(settings.memory.index_paths),
    }


def _stub(reason: str, detail: str) -> dict[str, Any]:
    result = {
        "stub": True,
        "enabled": False,
        "indexed": 0,
        "reason": reason,
        "detail": detail,
        "paths": list(settings.memory.index_paths),
    }
    audit.log("project_indexer_stub", result)
    return result


def _resolve_path(value: str) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return Path.cwd() / path


def _iter_indexable_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() in TEXT_SUFFIXES else []

    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
            files.append(path)
    return files


def _read_text(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    except OSError:
        return None
