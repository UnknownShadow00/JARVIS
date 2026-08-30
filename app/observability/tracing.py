"""Concurrency-safe local JSONL tracing with privacy-safe metadata."""
from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator, Mapping

from app.config import settings

SCHEMA_VERSION = 1
DEFAULT_TRACE_PATH = Path(settings.openjarvis.traces_dir) / "spans.jsonl"
DEFAULT_MAX_BYTES = max(1, settings.logging.max_log_size_mb) * 1024 * 1024
DEFAULT_BACKUP_COUNT = 3

_logger = logging.getLogger(__name__)
_trace_id_var: ContextVar[str | None] = ContextVar("jarvis_trace_id", default=None)
_span_stack_var: ContextVar[tuple[str, ...]] = ContextVar("jarvis_span_stack", default=())

_SAFE_METADATA_FIELDS = {
    "capability",
    "confirmation_required",
    "message_count",
    "model",
    "origin",
    "parameter_keys",
    "request_id",
    "streaming",
    "safety_level",
    "tool",
    "transport",
}


class JsonlTraceWriter:
    """Append JSONL records with bounded, same-directory rotation."""

    def __init__(
        self,
        path: str | Path,
        *,
        enabled: bool = True,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ) -> None:
        self.path = Path(path)
        self.enabled = enabled
        self.max_bytes = max(1, int(max_bytes))
        self.backup_count = max(0, int(backup_count))
        self._lock = threading.Lock()

    def write(self, record: Mapping[str, Any]) -> None:
        if not self.enabled:
            return
        line = json.dumps(dict(record), ensure_ascii=True, separators=(",", ":")) + "\n"
        encoded_size = len(line.encode("utf-8"))
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._rotate_if_needed(encoded_size)
            with self.path.open("a", encoding="utf-8") as trace_file:
                trace_file.write(line)

    def _rotate_if_needed(self, incoming_size: int) -> None:
        if self.backup_count == 0 or not self.path.exists():
            return
        if self.path.stat().st_size + incoming_size <= self.max_bytes:
            return

        oldest = self.path.with_name(f"{self.path.name}.{self.backup_count}")
        oldest.unlink(missing_ok=True)
        for index in range(self.backup_count - 1, 0, -1):
            source = self.path.with_name(f"{self.path.name}.{index}")
            if source.exists():
                source.replace(self.path.with_name(f"{self.path.name}.{index + 1}"))
        self.path.replace(self.path.with_name(f"{self.path.name}.1"))


_writer = JsonlTraceWriter(
    DEFAULT_TRACE_PATH,
    enabled=settings.openjarvis.trace_logging_enabled,
)


def configure_tracing(
    path: str | Path = DEFAULT_TRACE_PATH,
    *,
    enabled: bool = True,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> JsonlTraceWriter:
    """Replace the process trace writer; primarily useful for tests and host setup."""
    global _writer
    _writer = JsonlTraceWriter(
        path,
        enabled=enabled,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )
    return _writer


def current_trace_id() -> str | None:
    """Return the active request trace ID, if any."""
    return _trace_id_var.get()


def current_span_id() -> str | None:
    """Return the innermost active span ID, if any."""
    stack = _span_stack_var.get()
    return stack[-1] if stack else None


@contextmanager
def start_trace(
    *,
    origin: str = "user_direct",
    component: str = "app.server",
    transport: str | None = None,
    trace_id: str | None = None,
) -> Iterator[str]:
    """Start one logical request trace and its root request span."""
    generated_trace_id = trace_id or str(uuid.uuid4())
    trace_token = _trace_id_var.set(generated_trace_id)
    stack_token = _span_stack_var.set(())
    metadata: dict[str, Any] = {"origin": origin}
    if transport is not None:
        metadata["transport"] = transport
    try:
        with trace_span("request", component=component, metadata=metadata):
            yield generated_trace_id
    finally:
        _span_stack_var.reset(stack_token)
        _trace_id_var.reset(trace_token)


@contextmanager
def trace_span(
    stage: str,
    *,
    component: str,
    metadata: Mapping[str, Any] | None = None,
) -> Iterator[str | None]:
    """Record a timed child span while preserving normal exception behavior."""
    trace_id = current_trace_id()
    if trace_id is None:
        yield None
        return

    span_id = str(uuid.uuid4())
    parent_span_id = current_span_id()
    stack_token = _span_stack_var.set((*_span_stack_var.get(), span_id))
    started = time.perf_counter()
    safe_metadata = _safe_metadata(metadata)
    _emit(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=parent_span_id,
        stage=stage,
        event="start",
        component=component,
        status="started",
        duration_ms=0.0,
        metadata=safe_metadata,
    )
    try:
        yield span_id
    except BaseException as exc:
        _emit(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            stage=stage,
            event="end",
            component=component,
            status="error",
            duration_ms=_duration_ms(started),
            metadata={**safe_metadata, "error_type": type(exc).__name__},
        )
        raise
    else:
        _emit(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            stage=stage,
            event="end",
            component=component,
            status="ok",
            duration_ms=_duration_ms(started),
            metadata=safe_metadata,
        )
    finally:
        _span_stack_var.reset(stack_token)


def emit_event(
    stage: str,
    *,
    component: str,
    status: str = "ok",
    metadata: Mapping[str, Any] | None = None,
) -> str | None:
    """Emit an untimed event under the active trace."""
    trace_id = current_trace_id()
    if trace_id is None:
        return None
    span_id = str(uuid.uuid4())
    _emit(
        trace_id=trace_id,
        span_id=span_id,
        parent_span_id=current_span_id(),
        stage=stage,
        event="event",
        component=component,
        status=status,
        duration_ms=0.0,
        metadata=_safe_metadata(metadata),
    )
    return span_id


def _emit(
    *,
    trace_id: str,
    span_id: str,
    parent_span_id: str | None,
    stage: str,
    event: str,
    component: str,
    status: str,
    duration_ms: float,
    metadata: Mapping[str, Any],
) -> None:
    record: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_span_id": parent_span_id,
        "stage": str(stage),
        "event": str(event),
        "component": str(component),
        "status": str(status),
        "duration_ms": round(max(0.0, duration_ms), 3),
        **metadata,
    }
    try:
        _writer.write(record)
    except Exception as exc:  # noqa: BLE001 - observability must remain fail-safe
        _logger.warning("Failed to persist JARVIS trace span: %s", type(exc).__name__)


def _safe_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    if not metadata:
        return {}
    safe: dict[str, Any] = {}
    for key, value in metadata.items():
        if key not in _SAFE_METADATA_FIELDS and key != "error_type":
            continue
        if key == "parameter_keys":
            if isinstance(value, (list, tuple, set)):
                safe[key] = sorted({str(item) for item in value})
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            safe[key] = value
    return safe


def _duration_ms(started: float) -> float:
    return (time.perf_counter() - started) * 1000.0
