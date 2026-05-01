"""Entry point — uvicorn app.main:app"""
from app.server import app  # noqa: F401 — re-exported for uvicorn
