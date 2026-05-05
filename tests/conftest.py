import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "manual: requires real audio hardware - skipped in CI")
    config.addinivalue_line("markers", "unit: fast unit test with mocked dependencies")
