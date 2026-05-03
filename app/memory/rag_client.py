from __future__ import annotations

from app.config import settings
from app.logs.audit import audit


CHROMADB_AVAILABLE = False


class RAGClient:
    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._db_path = settings.memory.chromadb_path

    def index(self, documents: list[str], ids: list[str] | None = None) -> dict:
        if ids is None:
            ids = [str(i) for i in range(len(documents))]

        audit.log("rag_index", {"count": len(documents)})
        return {
            "stub": True,
            "indexed": len(documents),
            "note": "ChromaDB integration in Phase 4",
        }

    def query(self, query_text: str, n_results: int = 5) -> dict:
        audit.log("rag_query", {"query": query_text, "n_results": n_results})
        return {"stub": True, "results": [], "note": "ChromaDB integration in Phase 4"}


rag_client = RAGClient()
