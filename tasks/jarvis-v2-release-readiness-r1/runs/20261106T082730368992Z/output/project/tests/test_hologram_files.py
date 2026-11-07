import os


def test_hologram_index_exists() -> None:
    assert os.path.exists("frontend/hologram/index.html") is True


def test_hologram_app_exists() -> None:
    assert os.path.exists("frontend/hologram/app.js") is True


def test_hologram_has_threejs() -> None:
    with open("frontend/hologram/index.html", encoding="utf-8") as file:
        assert "three" in file.read().lower()
