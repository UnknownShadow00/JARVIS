import os

from app.server import app


def test_pwa_mount_exists() -> None:
    mounts = [route for route in app.routes if getattr(route, "name", "") == "pwa"]
    assert mounts


def test_pwa_files_exist() -> None:
    assert os.path.exists("frontend/pwa/index.html")
    assert os.path.exists("frontend/pwa/app.js")
    assert os.path.exists("frontend/pwa/manifest.json")
    assert os.path.exists("frontend/pwa/sw.js")
