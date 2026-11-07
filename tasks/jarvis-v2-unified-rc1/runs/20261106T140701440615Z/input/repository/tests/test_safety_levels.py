"""Legacy confirmation/configuration never authorizes an effect-capable tool."""
from types import SimpleNamespace
from unittest.mock import Mock
import pytest
from app.tools.registry import ToolRegistry,ToolError,TOOLS


@pytest.mark.parametrize('level',range(4))
@pytest.mark.parametrize('dry_run',[False,True])
@pytest.mark.parametrize('confirmed',[False,True])
def test_legacy_flags_cannot_invoke_real_tools(monkeypatch,level,dry_run,confirmed):
    from app.config import settings
    monkeypatch.setattr(settings.safety,'dry_run',dry_run)
    real=Mock(side_effect=AssertionError('real module execute must not run'))
    registry=ToolRegistry();registry._tools['shell']=SimpleNamespace(SAFETY_LEVEL=level,execute=real)
    with pytest.raises(ToolError,match='independent_authorization_required'):
        registry.call('shell',{'command':'synthetic canary'},confirmed=confirmed)
    real.assert_not_called()


def test_compatibility_exports_and_getters_are_metadata_only():
    registry=ToolRegistry()
    for callback in (TOOLS['shell'],registry.TOOLS['shell'],registry.get_tool('shell').execute,registry.get('shell').execute):
        with pytest.raises(ToolError,match='independent_authorization_required'):callback({'command':'synthetic only'})
    assert all(item['execution_enabled'] is False for item in registry.list_tools())
