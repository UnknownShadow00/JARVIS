import os
import json

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
