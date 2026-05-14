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


SESSION_ID = str(uuid.uuid4())


class AuditLogger:
    def __init__(self, audit_log_path: str) -> None:
        self._path = Path(audit_log_path)
        self._queue: queue.SimpleQueue[dict[str, Any] | None] = queue.SimpleQueue()
        self._worker = threading.Thread(
            target=self._run_writer,
            name="jarvis-audit-logger",
            daemon=True,
        )
        self._worker.start()
        atexit.register(self._shutdown)

    def log(self, event_type: str, data: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event_type": str(event_type),
            "data": dict(data),
            "session_id": SESSION_ID,
        }
        self._queue.put(entry)

    def _run_writer(self) -> None:
        while True:
            entry = self._queue.get()
            if entry is None:
                break

            try:
                self._path.parent.mkdir(parents=True, exist_ok=True)
                with self._path.open("a", encoding="utf-8") as audit_file:
                    audit_file.write(json.dumps(entry, ensure_ascii=True) + "\n")
            except Exception as exc:
                print(f"Warning: failed to write audit log to {self._path}: {exc}")

    def _shutdown(self) -> None:
        try:
            self._queue.put(None)
        except Exception:
            return

        if self._worker.is_alive():
            self._worker.join(timeout=1)


audit = AuditLogger(settings.logging.audit_log)

AuditLog = AuditLogger

