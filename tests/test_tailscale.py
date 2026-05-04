from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.server import app


def test_tailscale_not_installed(monkeypatch) -> None:
    from app.network import tailscale

    def raise_missing(*args, **kwargs):
        raise FileNotFoundError

    monkeypatch.setattr(tailscale.subprocess, "run", raise_missing)
    result = tailscale.get_status()
    assert result["available"] is False


def test_tailscale_parse_success(monkeypatch) -> None:
    from app.network import tailscale

    stdout = json.dumps(
        {
            "Self": {"TailscaleIPs": ["100.x.x.x"], "HostName": "jarvis-server"},
            "Peer": {"abc": {}},
        }
    )
    monkeypatch.setattr(
        tailscale.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout=stdout),
    )
    result = tailscale.get_status()
    assert result["available"] is True
    assert result["self_ip"] == "100.x.x.x"
    assert result["peers"] == 1


def test_tailscale_timeout(monkeypatch) -> None:
    from app.network import tailscale

    def raise_timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired("tailscale", 5)

    monkeypatch.setattr(tailscale.subprocess, "run", raise_timeout)
    result = tailscale.get_status()
    assert result["available"] is False


def test_network_status_endpoint(monkeypatch) -> None:
    from app.network import tailscale

    monkeypatch.setattr(tailscale, "get_status", lambda: {"available": False})
    client = TestClient(app)
    response = client.get("/network/status")
    assert response.status_code == 200
    assert "tailscale" in response.json()
