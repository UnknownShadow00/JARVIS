from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path
from types import ModuleType
from unittest.mock import AsyncMock, patch

import pytest

from app.brain.router import RouterResult
from app.config import settings
from app.logs.audit import AuditLogger
from app.observability import tracing
from app.observability.tracing import (
    current_trace_id,
    emit_event,
    start_trace,
    trace_span,
)
from app.tools.registry import ToolRegistry


@pytest.fixture
def trace_path(tmp_path: Path):
    path = tmp_path / "traces" / "spans.jsonl"
    tracing.configure_tracing(path, enabled=True, max_bytes=1024 * 1024, backup_count=2)
    yield path
    tracing.configure_tracing(
        tracing.DEFAULT_TRACE_PATH,
        enabled=settings.openjarvis.trace_logging_enabled,
    )


def _records(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def test_trace_id_is_generated_stable_and_uuid4(trace_path: Path) -> None:
    assert current_trace_id() is None
    with start_trace() as trace_id:
        assert uuid.UUID(trace_id).version == 4
        assert current_trace_id() == trace_id
        with trace_span("router", component="test.router"):
            assert current_trace_id() == trace_id
    assert current_trace_id() is None


def test_different_requests_get_different_trace_ids(trace_path: Path) -> None:
    with start_trace() as first:
        pass
    with start_trace() as second:
        pass
    assert first != second


@pytest.mark.asyncio
async def test_concurrent_requests_do_not_leak_trace_ids(trace_path: Path) -> None:
    ready = asyncio.Event()
    seen: dict[str, tuple[str, str]] = {}

    async def request(name: str) -> None:
        with start_trace() as trace_id:
            before = current_trace_id()
            if name == "first":
                ready.set()
                await asyncio.sleep(0.01)
            else:
                await ready.wait()
            await asyncio.sleep(0)
            seen[name] = (trace_id, current_trace_id() or "")

    await asyncio.gather(request("first"), request("second"))
    assert seen["first"][0] == seen["first"][1]
    assert seen["second"][0] == seen["second"][1]
    assert seen["first"][0] != seen["second"][0]


def test_parent_child_relationship_and_non_negative_durations(trace_path: Path) -> None:
    with start_trace():
        with trace_span("router", component="test.router") as parent:
            with trace_span("llm", component="test.llm") as child:
                pass

    records = _records(trace_path)
    child_start = next(row for row in records if row["span_id"] == child and row["event"] == "start")
    child_end = next(row for row in records if row["span_id"] == child and row["event"] == "end")
    assert child_start["parent_span_id"] == parent
    assert child_end["status"] == "ok"
    assert child_end["duration_ms"] >= 0


def test_failing_span_records_error_and_propagates_original_exception(trace_path: Path) -> None:
    error = RuntimeError("credential-shaped message must not be logged")
    with pytest.raises(RuntimeError) as captured:
        with start_trace():
            with trace_span("tool", component="test.tool"):
                raise error
    assert captured.value is error

    records = _records(trace_path)
    failing = next(row for row in records if row["stage"] == "tool" and row["event"] == "end")
    assert failing["status"] == "error"
    assert failing["error_type"] == "RuntimeError"
    assert "credential-shaped" not in trace_path.read_text(encoding="utf-8")


def test_audit_entry_includes_active_trace_and_remains_backward_compatible(
    trace_path: Path,
    tmp_path: Path,
) -> None:
    audit_path = tmp_path / "audit.jsonl"
    logger = AuditLogger(str(audit_path))
    with start_trace() as trace_id:
        logger.log("protected_action", {"tool": "shell"})
    logger.log("startup_event", {})
    logger._shutdown()  # noqa: SLF001 - deterministic queue flush for the isolated logger

    rows = [json.loads(line) for line in audit_path.read_text(encoding="utf-8").splitlines()]
    assert rows[0]["trace_id"] == trace_id
    assert rows[0]["schema_version"] == 2
    assert "trace_id" not in rows[1]
    assert rows[1]["event_type"] == "startup_event"


def test_span_metadata_drops_secret_values_and_unknown_fields(trace_path: Path) -> None:
    secret = "super-secret-bearer-value"
    with start_trace():
        emit_event(
            "safety",
            component="test.security",
            metadata={
                "tool": "shell",
                "parameter_keys": ["command", "api_token"],
                "api_token": secret,
                "authorization": f"Bearer {secret}",
                "cookie": secret,
                "params": {"password": secret},
            },
        )
    content = trace_path.read_text(encoding="utf-8")
    assert secret not in content
    event = next(row for row in _records(trace_path) if row["event"] == "event")
    assert event["parameter_keys"] == ["api_token", "command"]
    assert "api_token" not in event
    assert "authorization" not in event
    assert "params" not in event


def test_jsonl_records_have_required_schema_fields(trace_path: Path) -> None:
    with start_trace(origin="derived", transport="evaluation"):
        emit_event("confirmation", component="test.server", status="required")
    required = {
        "schema_version",
        "timestamp",
        "trace_id",
        "span_id",
        "parent_span_id",
        "stage",
        "event",
        "component",
        "status",
        "duration_ms",
    }
    rows = _records(trace_path)
    assert rows
    assert all(required <= row.keys() for row in rows)
    assert all(row["schema_version"] == 1 for row in rows)


def test_trace_write_failure_warns_but_does_not_break_processing(
    trace_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def fail_write(_record) -> None:  # noqa: ANN001
        raise PermissionError("unwritable")

    monkeypatch.setattr(tracing._writer, "write", fail_write)  # noqa: SLF001
    with caplog.at_level("WARNING"):
        with start_trace():
            with trace_span("router", component="test.router"):
                result = 42
    assert result == 42
    assert "Failed to persist JARVIS trace span" in caplog.text


def test_tool_trace_records_keys_not_values(
    trace_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings.safety, "dry_run", False)
    registry = ToolRegistry()
    module = ModuleType("test_trace_tool")
    module.SAFETY_LEVEL = 0  # type: ignore[attr-defined]
    module.DESCRIPTION = "Test-only trace tool"  # type: ignore[attr-defined]
    module.execute = lambda params: "ok"  # type: ignore[attr-defined]
    registry._tools["trace_test"] = module  # noqa: SLF001
    registry._tool_modules["trace_test"] = "test_trace_tool"  # noqa: SLF001
    secret = "private-tool-value"

    with start_trace():
        result = registry.call("trace_test", {"token": secret, "query": "private"}, confirmed=True)
    assert result.output == "ok"
    assert secret not in trace_path.read_text(encoding="utf-8")
    tool_end = next(row for row in _records(trace_path) if row["stage"] == "tool" and row["event"] == "end")
    assert tool_end["parameter_keys"] == ["query", "token"]


def test_small_max_size_rotates_trace_file(trace_path: Path) -> None:
    tracing.configure_tracing(trace_path, enabled=True, max_bytes=300, backup_count=2)
    for _ in range(5):
        with start_trace():
            pass
    assert trace_path.exists()
    assert trace_path.with_name("spans.jsonl.1").exists()


def test_tracing_overhead_is_small_for_local_noop_spans(trace_path: Path) -> None:
    iterations = 50
    baseline_start = time.perf_counter()
    for _ in range(iterations):
        pass
    baseline = time.perf_counter() - baseline_start

    traced_start = time.perf_counter()
    for _ in range(iterations):
        with start_trace():
            with trace_span("noop", component="test.benchmark"):
                pass
    traced = time.perf_counter() - traced_start
    overhead_ms = max(0.0, traced - baseline) * 1000 / iterations
    assert overhead_ms < 20.0


@pytest.mark.asyncio
async def test_chat_entry_point_creates_one_request_trace(trace_path: Path) -> None:
    from app import server

    intent = RouterResult("respond", 1.0, "", "test")
    with (
        patch.object(server.resource_manager, "ensure_awake_for_interaction", new=AsyncMock(return_value=True)),
        patch.object(server, "_process", new=AsyncMock(return_value=("Hello, sir.", intent))),
    ):
        response = await server.chat(server.ChatRequest(message="Hello"))
    assert response.reply == "Hello, sir."
    request_starts = [
        row
        for row in _records(trace_path)
        if row["stage"] == "request" and row["event"] == "start"
    ]
    assert len(request_starts) == 1
    assert request_starts[0]["transport"] == "http"


@pytest.mark.asyncio
async def test_confirmation_continues_original_trace(trace_path: Path) -> None:
    from app import server
    from app.tools.registry import ToolResult

    original_trace = str(uuid.uuid4())
    server._pending_confirmations["trace123"] = {  # noqa: SLF001
        "tool": "shell",
        "params": {"command": "echo safe"},
        "trace_id": original_trace,
    }
    try:
        with patch.object(
            server.registry,
            "call",
            return_value=ToolResult(tool="shell", output="safe"),
        ):
            result = await server.confirm_request("trace123")
    finally:
        server._pending_confirmations.clear()  # noqa: SLF001
    assert result["confirmed"] is True
    rows = _records(trace_path)
    assert rows
    assert {row["trace_id"] for row in rows} == {original_trace}
    assert any(row["stage"] == "confirmation" and row["status"] == "confirmed" for row in rows)
