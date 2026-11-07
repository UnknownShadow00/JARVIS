"""Actual application routes/status with an authenticated enrolled disposable DB."""
import httpx
import pytest
from app import server
from app.agent import runtime
from app.agent.authority import Authority,AuthorityError
from app.agent.ledger import LedgerGuard
from enrollment_fixtures import build,uid,KEY

@pytest.fixture
def bound(tmp_path,monkeypatch):
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    s,p=build(tmp_path/'case');result=s.enroll(runtime.SERVICE_ACTOR,p,disposable=True);s.guard.close()
    g=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(s.destination/'state.sqlite',ledger=g,enrollment_context=result['witness'])
    runtime.bind_authority(a)
    monkeypatch.setattr(server.settings.server,'api_token','synthetic-enrollment-app')
    yield a,s
    runtime.close_authority();runtime._authority=previous;runtime._execution_worker=worker

@pytest.mark.asyncio
async def test_authenticated_operator_diagnostics_show_verified_enrollment(bound):
    a,s=bound
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic') as client:
        assert (await client.get('/operator/diagnostics')).status_code==401
        response=await client.get('/operator/diagnostics',headers={'Authorization':'Bearer synthetic-enrollment-app'})
        assert response.status_code==200 and response.json()['enrollment']['state']=='VERIFIED'
        assert (await client.post('/operator/enrollment',json={},headers={'Authorization':'Bearer synthetic-enrollment-app'})).status_code==404

@pytest.mark.asyncio
async def test_missing_custody_receipt_blocks_public_admission(bound):
    a,s=bound;before=a._conn.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]
    (s.custody/'FINAL.json').rename(s.custody/'FINAL.missing')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic',headers={'Authorization':'Bearer synthetic-enrollment-app'}) as client:
        response=await client.post('/tasks',json={'request_id':uid(),'goal':'must be blocked'})
        assert response.status_code==503 and not response.json()['automatic_retry']
    assert a._conn.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]==before

@pytest.mark.asyncio
async def test_reporter_labels_enrollment_without_claiming_execution(bound):
    from app.agent.reporter import reporter
    result=await reporter.build_report()
    assert 'Enrollment VERIFIED' in result
    assert bound[0].readiness()['execution_enabled'] is False

@pytest.mark.asyncio
async def test_default_runtime_missing_store_is_unavailable_and_never_created(tmp_path,monkeypatch):
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    monkeypatch.setattr(runtime,'PROJECT_ROOT',tmp_path/'unprovisioned')
    monkeypatch.setattr(server.settings.server,'api_token','')
    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic') as client:
            result=await client.get('/tasks')
            assert result.status_code==503 and result.json()['error']=='authority_unenrolled_or_missing'
        assert not (tmp_path/'unprovisioned').exists()
    finally:runtime._authority=previous;runtime._execution_worker=worker
