from __future__ import annotations

from app.config import settings
from app.logs.audit import audit


MEM0_AVAILABLE = False


class MemoryClient:
    def __init__(self) -> None:
        self._client = None
        self._enabled = settings.memory.mem0_enabled

    def add(self, content: str, user_id: str = "jarvis") -> dict:
        if not self._enabled:
            return {"stub": True, "note": "Mem0 disabled — enable in config.yaml at Phase 4"}

        audit.log("memory_add", {"user_id": user_id, "content_len": len(content)})
        return {"stub": True, "note": "Mem0 integration in Phase 4"}

    def search(self, query: str, user_id: str = "jarvis") -> dict:
        if not self._enabled:
            return {"stub": True, "results": [], "note": "Mem0 disabled"}

        audit.log("memory_search", {"user_id": user_id, "query": query})
        return {"stub": True, "results": [], "note": "Mem0 integration in Phase 4"}

    def get_all(self, user_id: str = "jarvis") -> dict:
        return {"stub": True, "results": [], "note": "Mem0 integration in Phase 4"}


memory_client = MemoryClient()
