"""Intentional reporting faults, only selected with --probe; never acceptance tests."""
import time
import pytest


def test_pass():
    pass


def test_failure():
    raise AssertionError('synthetic private payload must not appear in JSON')


@pytest.fixture
def broken_setup():
    raise RuntimeError('synthetic private setup detail')


def test_setup_error(broken_setup):
    pass


@pytest.fixture
def broken_teardown():
    yield
    raise RuntimeError('synthetic private teardown detail')


def test_teardown_error(broken_teardown):
    pass


def test_skip():
    pytest.skip('intentional probe')


def test_timeout():
    time.sleep(2)


def test_caught_timeout():
    # A tested component can catch TimeoutError. The gate must still fail it.
    try:
        time.sleep(2)
    except TimeoutError:
        pass
