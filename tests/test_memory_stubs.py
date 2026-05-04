from __future__ import annotations

from app.memory import rag_client as rag_module
from app.memory.memory_client import memory_client


def test_memory_add_disabled() -> None:
    result = memory_client.add("test")

    assert "stub" in result


def test_memory_search_disabled() -> None:
    result = memory_client.search("test")

    assert result["results"] == []


def test_memory_get_all() -> None:
    result = memory_client.get_all()

    assert "stub" in result


def test_rag_index(monkeypatch) -> None:
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", False)

    client = rag_module.RAGClient()
    result = client.index(["doc1", "doc2"])

    assert result["stub"] is True
    assert result["indexed"] == 2


def test_rag_query(monkeypatch) -> None:
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", False)

    client = rag_module.RAGClient()
    result = client.query("hello")

    assert "results" in result
