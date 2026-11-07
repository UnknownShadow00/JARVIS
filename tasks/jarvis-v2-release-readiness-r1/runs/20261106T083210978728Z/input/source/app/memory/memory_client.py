from __future__ import annotations

from app.config import settings
from app.logs.audit import audit

try:
    from mem0 import Memory

    MEM0_AVAILABLE = True
except ImportError:
    Memory = None
    MEM0_AVAILABLE = False


class MemoryClient:
    def __init__(self) -> None:
        self._client = None
        self._enabled = settings.memory.mem0_enabled
        if self._enabled and MEM0_AVAILABLE:
            self._client = Memory()

    def add(self, content: str, user_id: str = "jarvis") -> dict:
        if not self._enabled or not MEM0_AVAILABLE or self._client is None:
            return {"stub": True, "note": "Mem0 disabled - enable in config.yaml at Phase 4"}

        try:
            result = self._client.add(content, user_id=user_id)
            audit.log("memory_add", {"user_id": user_id, "content_len": len(content)})
            return result
        except Exception as e:
            return {"error": str(e)}

    def search(self, query: str, user_id: str = "jarvis") -> dict:
        if not self._enabled or not MEM0_AVAILABLE or self._client is None:
            return {"stub": True, "results": [], "note": "Mem0 disabled"}

        try:
            result = self._client.search(query, user_id=user_id)
            audit.log("memory_search", {"user_id": user_id, "query": query})
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_all(self, user_id: str = "jarvis") -> dict:
        if not self._enabled or not MEM0_AVAILABLE or self._client is None:
            return {"stub": True, "results": [], "note": "Mem0 disabled"}

        try:
            result = self._client.get_all(user_id=user_id)
            audit.log("memory_get_all", {"user_id": user_id})
            return result
        except Exception as e:
            return {"error": str(e)}


memory_client = MemoryClient()
