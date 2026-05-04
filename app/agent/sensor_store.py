from __future__ import annotations

from collections import deque
from datetime import UTC, datetime
from typing import Any


MAX_READINGS = 100
_store: dict[str, deque[dict[str, Any]]] = {}


def add_reading(node_id: str, data: dict) -> None:
    if node_id not in _store:
        _store[node_id] = deque(maxlen=MAX_READINGS)
    _store[node_id].appendleft({"timestamp": datetime.now(UTC).isoformat(), **data})


def get_readings(node_id: str, limit: int = 10) -> list[dict]:
    return list(_store.get(node_id, deque()))[:limit]


def list_nodes() -> list[str]:
    return list(_store.keys())
