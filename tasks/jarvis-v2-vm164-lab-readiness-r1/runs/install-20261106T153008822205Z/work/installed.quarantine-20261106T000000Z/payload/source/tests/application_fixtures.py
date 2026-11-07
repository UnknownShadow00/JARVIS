"""Explicit disposable admission for actual application lifespan regression tests."""
import pytest
from app.agent import runtime
from synthetic_authority import fixture_authority

@pytest.fixture(autouse=True)
def admitted_app(tmp_path):
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    runtime.bind_authority(fixture_authority(tmp_path/'admitted/state.sqlite'))
    try:yield runtime._authority
    finally:
        runtime.close_authority();runtime._authority=previous;runtime._execution_worker=worker
