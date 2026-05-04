from __future__ import annotations

from app.memory import memory_client as memory_module


def test_add_disabled(monkeypatch) -> None:
    monkeypatch.setattr(memory_module.settings.memory, "mem0_enabled", False)

    client = memory_module.MemoryClient()
    result = client.add("test")

    assert "stub" in result


def test_search_disabled(monkeypatch) -> None:
    monkeypatch.setattr(memory_module.settings.memory, "mem0_enabled", False)

    client = memory_module.MemoryClient()
    result = client.search("query")

    assert "results" in result


def test_get_all_disabled(monkeypatch) -> None:
    monkeypatch.setattr(memory_module.settings.memory, "mem0_enabled", False)

    client = memory_module.MemoryClient()
    result = client.get_all()

    assert "results" in result


def test_add_enabled_no_mem0(monkeypatch) -> None:
    monkeypatch.setattr(memory_module.settings.memory, "mem0_enabled", True)
    monkeypatch.setattr(memory_module, "MEM0_AVAILABLE", False)

    client = memory_module.MemoryClient()
    result = client.add("test")

    assert "stub" in result


def test_add_enabled_with_mem0(monkeypatch) -> None:
    class FakeMemory:
        def add(self, content: str, user_id: str = "jarvis") -> dict:
            return {"results": []}

    monkeypatch.setattr(memory_module.settings.memory, "mem0_enabled", True)
    monkeypatch.setattr(memory_module, "MEM0_AVAILABLE", True)
    monkeypatch.setattr(memory_module, "Memory", FakeMemory)

    client = memory_module.MemoryClient()
    result = client.add("hello")

    assert "stub" not in result
    assert result == {"results": []}
