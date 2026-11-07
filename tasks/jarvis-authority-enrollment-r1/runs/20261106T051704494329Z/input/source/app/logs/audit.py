from __future__ import annotations

import atexit
import json
import queue
import threading
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.observability.tracing import JsonlTraceWriter, current_trace_id


SESSION_ID = str(uuid.uuid4())
DEFAULT_MAX_BYTES = max(1, settings.logging.max_log_size_mb) * 1024 * 1024
DEFAULT_BACKUP_COUNT = 3


class AuditLogger:
    def __init__(
        self,
        audit_log_path: str,
        *,
        max_bytes: int = DEFAULT_MAX_BYTES,
        backup_count: int = DEFAULT_BACKUP_COUNT,
    ) -> None:
        self._path = Path(audit_log_path)
        self._writer = JsonlTraceWriter(
            self._path,
            max_bytes=max_bytes,
            backup_count=backup_count,
        )
        self._queue: queue.SimpleQueue[dict[str, Any] | None] = queue.SimpleQueue()
        self._shutdown_lock = threading.Lock()
        self._shutdown_requested = False
        self._worker = threading.Thread(
            target=self._run_writer,
            name="jarvis-audit-logger",
            daemon=True,
        )
        self._worker.start()
        atexit.register(self._shutdown)

    def log(self, event_type: str, data: dict[str, Any]) -> None:
        entry = {
            "schema_version": 2,
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": str(event_type),
            "data": dict(data),
            "session_id": SESSION_ID,
        }
        trace_id = current_trace_id()
        if trace_id is not None:
            entry["trace_id"] = trace_id
        self._queue.put(entry)

    def _run_writer(self) -> None:
        while True:
            entry = self._queue.get()
            if entry is None:
                break

            try:
                self._writer.write(entry)
            except Exception as exc:
                print(f"Warning: failed to write audit log to {self._path}: {exc}")
                # Rotation failure must not discard an ordinary safety/tool event
                # when the active file itself is still appendable.
                try:
                    self._path.parent.mkdir(parents=True, exist_ok=True)
                    with self._path.open("a", encoding="utf-8") as audit_file:
                        audit_file.write(json.dumps(entry, ensure_ascii=True) + "\n")
                except Exception as fallback_exc:
                    print(f"Warning: audit fallback write failed for {self._path}: {fallback_exc}")

    def _shutdown(self) -> None:
        with self._shutdown_lock:
            if not self._shutdown_requested:
                self._shutdown_requested = True
                try:
                    self._queue.put(None)
                except Exception:
                    return

        if self._worker.is_alive():
            self._worker.join(timeout=1)


audit = AuditLogger(settings.logging.audit_log)

AuditLog = AuditLogger
