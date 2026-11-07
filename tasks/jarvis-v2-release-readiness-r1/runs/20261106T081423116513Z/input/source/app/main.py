"""Runtime entry point for the JARVIS FastAPI app."""
from __future__ import annotations

import uvicorn

from app.config import settings
from app.server import app  # noqa: F401 - re-exported for uvicorn


def main() -> None:
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)


if __name__ == "__main__":
    main()
