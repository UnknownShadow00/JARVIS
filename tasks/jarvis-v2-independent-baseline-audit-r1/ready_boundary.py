import pytest,httpx
from fastapi import FastAPI
from app.agent.api import router
from app.agent import api
from app.agent.authority import AuthorityError
from app.config import settings
from app import cli

@pytest.mark.asyncio
@pytest.mark.parametrize('supplied',['', 'Bearer wrong', 'Bearer audit-token'])
async def test_real_route_identity_precedes_readiness(monkeypatch,supplied):
 monkeypatch.setattr(settings.server,'api_token','audit-token');calls=[]
 def ready():calls.append(1);return dict(scheduler_ready=True,storage_ready=True)
 monkeypatch.setattr(api.scheduler,'readiness',ready)
 monkeypatch.setattr(api,'execution_readiness',lambda:dict(synthetic_execution_enabled=False))
 app=FastAPI();app.include_router(router)
 async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as c:
  for _ in range(2):
   r=await c.get('/ready',headers={'Authorization':supplied})
   assert r.status_code==(200 if supplied=='Bearer audit-token' else 401)
 assert len(calls)==(2 if supplied=='Bearer audit-token' else 0)

@pytest.mark.asyncio
@pytest.mark.parametrize('code',['owner_fenced','store_replaced','ledger_inconsistent','unsafe_storage_ancestor','authority_unavailable'])
async def test_storage_and_stale_authority_never_ready(monkeypatch,code):
 monkeypatch.setattr(settings.server,'api_token','audit-token')
 def refused():raise AuthorityError(code)
 monkeypatch.setattr(api.scheduler,'readiness',refused)
 app=FastAPI();app.include_router(router)
 async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),base_url='http://synthetic') as c:
  r=await c.get('/ready',headers={'Authorization':'Bearer audit-token'});assert r.status_code!=200

@pytest.mark.parametrize('error',[httpx.ReadTimeout('synthetic'),httpx.ConnectError('synthetic')])
def test_interrupted_client_has_one_attempt_no_start(monkeypatch,error):
 monkeypatch.setattr(settings.server,'api_token','audit-token');calls=[]
 def get(*a,**kw):calls.append(1);raise error
 monkeypatch.setattr(cli.httpx,'get',get)
 assert cli.main(['ready'])==1 and len(calls)==1

def test_bad_command_never_requests(monkeypatch):
 monkeypatch.setattr(cli.httpx,'get',lambda *a,**k:pytest.fail('request forbidden'))
 with pytest.raises(SystemExit) as e:cli.main(['ready','--unknown'])
 assert e.value.code==2
