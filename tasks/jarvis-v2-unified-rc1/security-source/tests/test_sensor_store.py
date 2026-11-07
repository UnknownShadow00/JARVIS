from __future__ import annotations

from app.agent import sensor_store


def setup_function() -> None:
    sensor_store._store.clear()


def test_add_and_get_reading() -> None:
    sensor_store.add_reading("rpi-1", {"readings": {"cpu_temp": 45.0}})
    readings = sensor_store.get_readings("rpi-1", 1)
    assert len(readings) == 1
    assert readings[0]["readings"]["cpu_temp"] == 45.0


def test_list_nodes() -> None:
    sensor_store.add_reading("node-a", {})
    sensor_store.add_reading("node-b", {})
    assert "node-a" in sensor_store.list_nodes()


def test_max_readings() -> None:
    for value in range(101):
        sensor_store.add_reading("overflow-node", {"readings": {"cpu_temp": float(value)}})
    assert len(sensor_store.get_readings("overflow-node", 200)) == 100


def test_get_unknown_node() -> None:
    assert sensor_store.get_readings("nonexistent") == []
