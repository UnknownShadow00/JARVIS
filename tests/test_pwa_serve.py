import os
import json
from pathlib import Path

from app.server import app


def test_pwa_mount_exists() -> None:
    mounts = [route for route in app.routes if getattr(route, "name", "") == "pwa"]
    assert mounts


def test_pwa_files_exist() -> None:
    assert os.path.exists("frontend/pwa/index.html")
    assert os.path.exists("frontend/pwa/app.js")
    assert os.path.exists("frontend/pwa/manifest.json")
    assert os.path.exists("frontend/pwa/sw.js")


def test_pwa_manifest_is_scoped_to_pwa_mount() -> None:
    with open("frontend/pwa/manifest.json", encoding="utf-8") as manifest_file:
        manifest = json.load(manifest_file)

    assert manifest["start_url"] == "./"
    assert manifest["scope"] == "./"


def test_pwa_does_not_store_or_transport_api_credentials() -> None:
    script = Path("frontend/pwa/app.js").read_text(encoding="utf-8")

    assert "jarvis_api_token" not in script
    assert "TOKEN_KEY" not in script
    assert "withTokenParam" not in script
    assert "Authorization" not in script
    assert "?token=" not in script
    assert "Enter API token" not in script
