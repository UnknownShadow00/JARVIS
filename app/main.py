"""Entry point - uvicorn app.main:app"""
from __future__ import annotations

import asyncio

from app.config_check import check_startup
from app.logs.audit import audit
from app.server import app  # noqa: F401 - re-exported for uvicorn


def _log_startup_checks() -> None:
    audit.log("config_check", check_startup())


@app.on_event("startup")
async def startup_config_check() -> None:
    asyncio.create_task(asyncio.to_thread(_log_startup_checks))
