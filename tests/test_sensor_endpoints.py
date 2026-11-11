from __future__ import annotations
import pytest
from application_fixtures import admitted_app

from fastapi.testclient import TestClient

from app.agent import sensor_store
from app.server import app


def setup_function() -> None:
    sensor_store._store.clear()


def test_post_sensor_data() -> None:
    with TestClient(app, headers={"Authorization":"Bearer synthetic-coverage-client"}) as client:
        response = client.post("/sensors/data", json={"node_id": "rpi-1", "readings": {"cpu_temp": 42.0}})
    assert response.status_code == 200
    assert response.json()["received"] is True


def test_get_sensor_readings() -> None:
    with TestClient(app, headers={"Authorization":"Bearer synthetic-coverage-client"}) as client:
        client.post("/sensors/data", json={"node_id": "rpi-1", "readings": {"cpu_temp": 42.0}})
        response = client.get("/sensors/rpi-1")
    assert response.status_code == 200
    assert "readings" in response.json()


def test_list_sensors() -> None:
    with TestClient(app, headers={"Authorization":"Bearer synthetic-coverage-client"}) as client:
        client.post("/sensors/data", json={"node_id": "rpi-list-test", "readings": {"cpu_temp": 42.0}})
        response = client.get("/sensors")
    assert response.status_code == 200
    assert "nodes" in response.json()


@pytest.fixture(autouse=True)
def authenticated_fixture(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings.server,"api_token","synthetic-coverage-client")
