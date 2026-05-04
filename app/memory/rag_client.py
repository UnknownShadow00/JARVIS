from __future__ import annotations

from app.config import settings
from app.logs.audit import audit

try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    CHROMADB_AVAILABLE = False


class RAGClient:
    def __init__(self) -> None:
        self._client = None
        self._collection = None
        self._db_path = settings.memory.chromadb_path

    def _get_collection(self):
        if not CHROMADB_AVAILABLE:
            return None

        if self._client is None or self._collection is None:
            self._client = chromadb.PersistentClient(path=self._db_path)
            self._collection = self._client.get_or_create_collection("jarvis")

        return self._collection

    def index(self, documents: list[str], ids: list[str] | None = None) -> dict:
        if ids is None:
            ids = [str(i) for i in range(len(documents))]

        if not CHROMADB_AVAILABLE:
            audit.log("rag_index", {"count": len(documents)})
            return {
                "stub": True,
                "indexed": len(documents),
                "note": "ChromaDB integration in Phase 4",
            }

        try:
            collection = self._get_collection()
            if collection is None:
                audit.log("rag_index", {"count": len(documents)})
                return {
                    "stub": True,
                    "indexed": len(documents),
                    "note": "ChromaDB integration in Phase 4",
                }

            collection.add(documents=documents, ids=ids)
            audit.log("rag_index", {"count": len(documents)})
            return {"indexed": len(documents), "total": collection.count()}
        except Exception as e:
            return {"error": str(e)}

    def query(self, query_text: str, n_results: int = 5) -> dict:
        if not CHROMADB_AVAILABLE:
            audit.log("rag_query", {"query": query_text, "n_results": n_results})
            return {"stub": True, "results": [], "note": "ChromaDB integration in Phase 4"}

        try:
            collection = self._get_collection()
            if collection is None:
                audit.log("rag_query", {"query": query_text, "n_results": n_results})
                return {
                    "stub": True,
                    "results": [],
                    "note": "ChromaDB integration in Phase 4",
                }

            result = collection.query(query_texts=[query_text], n_results=n_results)
            docs = result["documents"][0]
            ids = result["ids"][0]
            audit.log("rag_query", {"query": query_text, "n_results": n_results})
            return {"results": docs, "ids": ids}
        except Exception as e:
            return {"error": str(e)}


rag_client = RAGClient()
