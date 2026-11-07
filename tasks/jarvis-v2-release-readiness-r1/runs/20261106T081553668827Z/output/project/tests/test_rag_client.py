from __future__ import annotations

from unittest.mock import Mock

from app.memory import rag_client as rag_module


def test_index_no_chromadb(monkeypatch) -> None:
    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", True)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", False)

    client = rag_module.RAGClient()
    result = client.index(["doc1"], ["1"])

    assert "stub" in result


def test_query_no_chromadb(monkeypatch) -> None:
    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", True)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", False)

    client = rag_module.RAGClient()
    result = client.query("test")

    assert "stub" in result


def test_index_with_chromadb(monkeypatch) -> None:
    collection = Mock()
    collection.count.return_value = 2

    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", True)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", True)

    client = rag_module.RAGClient()
    monkeypatch.setattr(client, "_get_collection", lambda: collection)

    result = client.index(["a", "b"], ["1", "2"])

    collection.add.assert_called_once_with(documents=["a", "b"], ids=["1", "2"])
    assert result == {"indexed": 2, "total": 2}


def test_query_with_chromadb(monkeypatch) -> None:
    collection = Mock()
    collection.query.return_value = {"documents": [["doc1"]], "ids": [["1"]]}

    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", True)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", True)

    client = rag_module.RAGClient()
    monkeypatch.setattr(client, "_get_collection", lambda: collection)

    result = client.query("test")

    collection.query.assert_called_once_with(query_texts=["test"], n_results=5)
    assert result["results"] == ["doc1"]


def test_index_error(monkeypatch) -> None:
    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", True)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", True)

    client = rag_module.RAGClient()

    def raise_error():
        raise Exception("db error")

    monkeypatch.setattr(client, "_get_collection", raise_error)

    result = client.index(["doc1"], ["1"])

    assert "error" in result


def test_query_disabled_by_config(monkeypatch) -> None:
    monkeypatch.setattr(rag_module.settings.memory, "chromadb_enabled", False)
    monkeypatch.setattr(rag_module, "CHROMADB_AVAILABLE", True)

    client = rag_module.RAGClient()
    result = client.query("test")

    assert result["stub"] is True
    assert result["reason"] == "disabled"
