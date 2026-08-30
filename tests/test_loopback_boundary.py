from __future__ import annotations

import ipaddress
from pathlib import Path
import re
from urllib.parse import urlsplit

import pytest
import yaml

from app.config import load_settings
from scripts import sensor_node


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOOPBACK_CONFIGS = (PROJECT_ROOT / "config.yaml", PROJECT_ROOT / "config.yaml.example")


def _is_loopback_url(value: str, *, schemes: set[str]) -> bool:
    parsed = urlsplit(value)
    if parsed.scheme not in schemes or not parsed.hostname:
        return False
    if parsed.hostname.lower() == "localhost":
        return True
    try:
        return ipaddress.ip_address(parsed.hostname).is_loopback
    except ValueError:
        return False


def _javascript_urls(path: str) -> list[str]:
    source = (PROJECT_ROOT / path).read_text(encoding="utf-8")
    return re.findall(r'["\']((?:https?|wss?)://[^"\']+)["\']', source)


@pytest.mark.parametrize("config_path", LOOPBACK_CONFIGS)
def test_default_server_and_browser_origins_are_loopback(config_path: Path) -> None:
    configured = load_settings(config_path)

    assert ipaddress.ip_address(configured.server.host).is_loopback
    assert configured.server.remote_access_enabled is False
    assert configured.server.cors_origins
    assert "*" not in configured.server.cors_origins
    assert all(
        _is_loopback_url(origin, schemes={"http", "https"})
        for origin in configured.server.cors_origins
    )
    assert _is_loopback_url(
        configured.models.ollama_base_url,
        schemes={"http", "https"},
    )


@pytest.mark.parametrize(
    ("origins", "message"),
    [
        (["*"], "must not contain a wildcard"),
        (["http://192.168.1.10:3000"], "only localhost/loopback origins"),
    ],
)
def test_local_mode_rejects_unsafe_cors_origins(
    tmp_path: Path,
    origins: list[str],
    message: str,
) -> None:
    raw = yaml.safe_load((PROJECT_ROOT / "config.yaml.example").read_text(encoding="utf-8"))
    raw["server"]["cors_origins"] = origins
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(raw), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_settings(config_path)


def test_explicit_authenticated_remote_mode_preserves_future_origin_support(tmp_path: Path) -> None:
    raw = yaml.safe_load((PROJECT_ROOT / "config.yaml.example").read_text(encoding="utf-8"))
    raw["server"].update(
        {
            "host": "0.0.0.0",
            "remote_access_enabled": True,
            "api_token": "test-only-token",
            "cors_origins": ["https://jarvis.internal.example"],
        }
    )
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(raw), encoding="utf-8")

    configured = load_settings(config_path)

    assert configured.server.host == "0.0.0.0"
    assert configured.server.cors_origins == ["https://jarvis.internal.example"]


def test_all_active_compose_published_ports_bind_host_loopback() -> None:
    compose = yaml.safe_load((PROJECT_ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    published: list[tuple[str, str]] = []

    for service_name, service in compose["services"].items():
        for mapping in service.get("ports", []):
            assert isinstance(mapping, str), f"unsupported port mapping in {service_name}: {mapping!r}"
            parts = mapping.split(":")
            assert len(parts) == 3, f"{service_name} must declare host IP: {mapping}"
            host_ip = parts[0]
            assert ipaddress.ip_address(host_ip).is_loopback, (
                f"{service_name} publishes {mapping} on a non-loopback host interface"
            )
            published.append((service_name, mapping))

    assert published == [
        ("ollama", "127.0.0.1:11434:11434"),
        ("jarvis_backend", "127.0.0.1:8000:8000"),
        ("neo4j", "127.0.0.1:7474:7474"),
        ("neo4j", "127.0.0.1:7687:7687"),
    ]


def test_browser_client_defaults_are_loopback() -> None:
    frontend_paths = (
        "frontend/pwa/app.js",
        "frontend/hologram/app.js",
        "frontend/electron/preload.js",
    )

    for path in frontend_paths:
        websocket_urls = [url for url in _javascript_urls(path) if url.startswith(("ws://", "wss://"))]
        assert websocket_urls, f"no WebSocket default found in {path}"
        assert all(_is_loopback_url(url, schemes={"ws", "wss"}) for url in websocket_urls)


def test_sensor_node_default_target_is_loopback() -> None:
    assert _is_loopback_url(sensor_node.DEFAULT_JARVIS_URL, schemes={"http", "https"})
