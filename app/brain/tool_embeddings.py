"""Embedding-backed tool selection helpers."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
import numpy as np

from app.config import settings
from app.logs.audit import audit

CACHE_PATH = Path("./data/tool_embeddings.json")


def select_tool_by_embedding(
    text: str,
    candidates: list[str],
    descriptions: dict[str, str],
) -> str | None:
    """Return the highest-similarity candidate, or None when embeddings fail."""
    if not text.strip() or not candidates:
        return None

    cache = _load_cache()
    try:
        candidate_embeddings = _candidate_embeddings(candidates, descriptions, cache)
        query_embedding = _embed(text)
    except Exception as exc:  # noqa: BLE001
        audit.log("tool_embedding_warning", {"reason": str(exc), "model": settings.routing.embedding_model})
        return None

    if query_embedding is None or not candidate_embeddings:
        return None

    query_vector = np.array(query_embedding, dtype=float)
    scored: list[tuple[str, float]] = []
    for name, embedding in candidate_embeddings.items():
        score = _cosine_similarity(query_vector, np.array(embedding, dtype=float))
        scored.append((name, score))

    if not scored:
        return None

    scored.sort(key=lambda item: item[1], reverse=True)
    top_k = max(1, settings.routing.embedding_top_k)
    audit.log(
        "tool_embedding_selection",
        {
            "model": settings.routing.embedding_model,
            "candidate_count": len(candidates),
            "top": [{"tool": name, "score": round(score, 4)} for name, score in scored[:top_k]],
        },
    )
    return scored[0][0]


def _candidate_embeddings(
    candidates: list[str],
    descriptions: dict[str, str],
    cache: dict[str, Any],
) -> dict[str, list[float]]:
    model = settings.routing.embedding_model
    cache["model"] = model
    tools_cache = cache.setdefault("tools", {})
    embeddings: dict[str, list[float]] = {}

    for name in candidates:
        description = descriptions.get(name, "").strip()
        if not description:
            continue
        entry = tools_cache.get(name)
        if (
            isinstance(entry, dict)
            and entry.get("model") == model
            and entry.get("description") == description
            and isinstance(entry.get("embedding"), list)
        ):
            embeddings[name] = [float(value) for value in entry["embedding"]]
            continue

        embedding = _embed(description)
        if embedding is None:
            continue
        embeddings[name] = embedding
        tools_cache[name] = {"model": model, "description": description, "embedding": embedding}

    _save_cache(cache)
    return embeddings


def _embed(text: str) -> list[float] | None:
    payload = {"model": settings.routing.embedding_model, "prompt": text}
    url = f"{settings.models.ollama_base_url}/api/embeddings"
    with httpx.Client(timeout=httpx.Timeout(10.0)) as client:
        response = client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

    embedding = data.get("embedding")
    if not isinstance(embedding, list) or not embedding:
        audit.log("tool_embedding_warning", {"reason": "empty_embedding", "model": settings.routing.embedding_model})
        return None
    return [float(value) for value in embedding]


def _cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    if left.shape != right.shape:
        return 0.0
    denominator = float(np.linalg.norm(left) * np.linalg.norm(right))
    if denominator == 0.0:
        return 0.0
    return float(np.dot(left, right) / denominator)


def _load_cache() -> dict[str, Any]:
    if not CACHE_PATH.is_file():
        return {"model": settings.routing.embedding_model, "tools": {}}
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"model": settings.routing.embedding_model, "tools": {}}
    if not isinstance(data, dict) or data.get("model") != settings.routing.embedding_model:
        return {"model": settings.routing.embedding_model, "tools": {}}
    if not isinstance(data.get("tools"), dict):
        data["tools"] = {}
    return data


def _save_cache(cache: dict[str, Any]) -> None:
    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    except OSError as exc:
        audit.log("tool_embedding_warning", {"reason": f"cache_write_failed: {exc}"})
