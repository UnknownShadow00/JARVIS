"""Feature-flagged Graphiti temporal knowledge graph wrapper."""
from __future__ import annotations

import asyncio
import inspect
import os
from datetime import UTC, datetime
from typing import Any

from app.config import settings
from app.logs.audit import audit

try:
    from graphiti_core import Graphiti  # type: ignore[import-untyped]
    from graphiti_core.nodes import EntityNode, EpisodeType  # type: ignore[import-untyped]
except ImportError:
    Graphiti = None
    EntityNode = None
    EpisodeType = None
    GRAPHITI_AVAILABLE = False
else:
    GRAPHITI_AVAILABLE = True


class GraphitiClient:
    """Lazy Graphiti client that never connects unless explicitly enabled."""

    def __init__(self) -> None:
        self._client: Any | None = None

    def is_enabled(self) -> bool:
        return bool(settings.memory.graphiti_enabled and GRAPHITI_AVAILABLE and self._password())

    def add_episode(self, text: str, source: str = "jarvis", ts: datetime | str | None = None) -> dict[str, Any]:
        """Add a temporal text episode when Graphiti is enabled."""
        if not self.is_enabled():
            return self._stub("add_episode")

        timestamp = _coerce_timestamp(ts)
        audit.log("graphiti_add_episode", {"chars": len(text), "source": source, "ts": timestamp.isoformat()})
        try:
            result = self._run(
                self._get_client().add_episode(
                    name=source or "jarvis",
                    episode_body=text,
                    source=EpisodeType.text,
                    reference_time=timestamp,
                )
            )
            return {"added": True, "result": _serializable(result)}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    def query(self, text: str, limit: int = 5) -> dict[str, Any]:
        """Search the temporal graph when Graphiti is enabled."""
        if not self.is_enabled():
            return self._stub("query", results=[])

        safe_limit = max(1, min(int(limit), 25))
        audit.log("graphiti_query", {"query_chars": len(text), "limit": safe_limit})
        try:
            result = self._run(self._get_client().search(text, num_results=safe_limit))
            return {"results": _serializable(result), "limit": safe_limit}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc), "results": []}

    def add_entity(self, name: str, type: str) -> dict[str, Any]:  # noqa: A002
        """Add an entity when the installed Graphiti client exposes a compatible method."""
        if not self.is_enabled():
            return self._stub("add_entity")

        audit.log("graphiti_add_entity", {"name": name, "type": type})
        try:
            client = self._get_client()
            if hasattr(client, "add_entity"):
                result = self._run(client.add_entity(name=name, type=type))
                return {"added": True, "result": _serializable(result)}
            if EntityNode is not None and hasattr(client, "add_node"):
                node = EntityNode(name=name, group_id="jarvis", labels=[type], summary=f"{type}: {name}")
                result = self._run(client.add_node(node))
                return {"added": True, "result": _serializable(result)}
            return {"stub": True, "reason": "graphiti_add_entity_method_unavailable"}
        except Exception as exc:  # noqa: BLE001
            return {"error": str(exc)}

    def _get_client(self) -> Any:
        if self._client is None:
            self._client = Graphiti(settings.memory.neo4j_uri, settings.memory.neo4j_user, self._password())
        return self._client

    def _password(self) -> str:
        return os.environ.get(settings.memory.neo4j_password_env, "")

    def _stub(self, action: str, **extra: Any) -> dict[str, Any]:
        reason = "disabled"
        if settings.memory.graphiti_enabled and not GRAPHITI_AVAILABLE:
            reason = "graphiti_core_unavailable"
        elif settings.memory.graphiti_enabled and not self._password():
            reason = "missing_neo4j_password_env"
        return {
            "stub": True,
            "action": action,
            "reason": reason,
            "note": "Graphiti is disabled or unavailable.",
            **extra,
        }

    def _run(self, value: Any) -> Any:
        if inspect.isawaitable(value):
            return asyncio.run(value)
        return value


def _coerce_timestamp(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else value.replace(tzinfo=UTC)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)


def _serializable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _serializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_serializable(item) for item in value]
    if hasattr(value, "model_dump"):
        return _serializable(value.model_dump())
    if hasattr(value, "__dict__"):
        return _serializable(vars(value))
    return str(value)


graphiti_client = GraphitiClient()
