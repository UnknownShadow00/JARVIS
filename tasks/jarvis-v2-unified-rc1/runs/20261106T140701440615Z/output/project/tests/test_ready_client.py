"""Credentialed readiness consumer fails closed without startup or retry."""
import httpx
import pytest
from app import cli
from app.config import settings

TOKEN='synthetic-ready-client'

@pytest.mark.parametrize('token',['',' ','\t'])
def test_ready_requires_nonblank_identity_before_request(monkeypatch,capsys,token):
    monkeypatch.setattr(settings.server,'api_token',token)
    def forbidden(*a,**kw):pytest.fail('unconfigured readiness made a request')
    monkeypatch.setattr(cli.httpx,'get',forbidden)
    assert cli.main(['ready'])==1
    assert 'requires a configured Bearer' in capsys.readouterr().err

@pytest.mark.parametrize('status,payload,expected',[
    (200,{'scheduler_ready':True,'synthetic_execution_enabled':False},0),
    (200,{'scheduler_ready':True,'synthetic_execution_enabled':True,'execution_worker_ready':True},0),
    (200,{'scheduler_ready':True,'synthetic_execution_enabled':True,'execution_worker_ready':False},1),
    (200,{'scheduler_ready':False,'synthetic_execution_enabled':False},1),
    (200,{},1),
    (200,{'scheduler_ready':True,'synthetic_execution_enabled':'false'},1),
    (401,{'detail':'authority_authentication_required'},1),
    (503,{'scheduler_ready':False,'synthetic_execution_enabled':False},1),
])
def test_ready_uses_bearer_and_preserves_failure(monkeypatch,capsys,status,payload,expected):
    monkeypatch.setattr(settings.server,'api_token',TOKEN)
    calls=[]
    def get(url,*,headers,timeout):
        calls.append((url,headers))
        return httpx.Response(status,json=payload,request=httpx.Request('GET',url))
    monkeypatch.setattr(cli.httpx,'get',get)
    assert cli.main(['ready'])==expected
    assert len(calls)==1 and calls[0][0].endswith('/ready')
    assert calls[0][1]=={'Authorization':'Bearer '+TOKEN}
    captured=capsys.readouterr()
    assert TOKEN not in captured.out+captured.err


def test_ready_transport_failure_does_not_retry_or_start(monkeypatch,capsys):
    monkeypatch.setattr(settings.server,'api_token',TOKEN)
    calls=[]
    def get(*a,**kw):
        calls.append(1)
        raise httpx.ConnectError('synthetic unavailable')
    monkeypatch.setattr(cli.httpx,'get',get)
    assert cli.main(['ready'])==1 and len(calls)==1
    assert 'No retry' in capsys.readouterr().err
