from __future__ import annotations

import threading


class CancelToken:
    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        self._event.set()

    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def reset(self) -> None:
        self._event.clear()

    def wait_cancelled(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout=timeout)


current_token = CancelToken()
