"""Application-facing disaster status and receipt corruption refusal."""
from datetime import UTC,datetime,timedelta
import json
import uuid
import httpx
import pytest

from app import server
from app.agent import runtime
from app.agent.authority import Authority
from synthetic_authority import fixture_authority as Authority
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits,RecoveryActions
from app.agent.archive_restore import ArchiveRestorer

KEY=b'synthetic-disaster-app-ledger-key-000000000'
OPKEY=b'synthetic-disaster-app-operator-key-0000000'

def key():return str(uuid.uuid4())

@pytest.fixture
def bound(tmp_path):
    previous,worker=runtime._authority,runtime._execution_worker
    runtime._authority=runtime._execution_worker=None
    exports=tmp_path/'exports';targets=tmp_path/'targets';exports.mkdir(mode=0o700);targets.mkdir(mode=0o700)
    g=LedgerGuard(tmp_path/'protected',KEY,key(),initialize=True,rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(tmp_path/'db'/'state.sqlite',allow_simulation=True,ledger=g)
    runtime.bind_authority(a)
    issuer=OperatorPermits(OPKEY);actions=RecoveryActions(a,issuer)
    for _ in range(4):a.submit(runtime.SERVICE_ACTOR,key(),'held')
    export_id=key();now=datetime.now(UTC)
    token=issuer.issue(request_id=export_id,principal='synthetic-operator',scope=runtime.SERVICE_ACTOR.scope,command='export_ledger',payload={'export_id':export_id,'destination':str(exports)},checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    result=actions.export(runtime.SERVICE_ACTOR,export_id,exports,token)
    g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    restore_id=key();payload={'export_id':export_id,'manifest_sha256':result['export']['manifest_sha256'],'target_parent':str(targets),'restore_id':restore_id}
    token=issuer.issue(request_id=restore_id,principal='synthetic-operator',scope=runtime.SERVICE_ACTOR.scope,command='restore_archive',payload=payload,checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    restored=ArchiveRestorer(g,issuer).restore(runtime.SERVICE_ACTOR,restore_id,exports/export_id,targets,result['export']['manifest_sha256'],token,disposable=True)
    yield a,g,restored
    runtime.close_authority();runtime._authority=previous;runtime._execution_worker=worker

@pytest.mark.asyncio
async def test_operator_status_exposes_rollover_and_verified_receipt_state(bound,monkeypatch):
    a,g,restored=bound
    monkeypatch.setattr(server.settings.server,'api_token','disaster-fixture-only')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic',headers={'Authorization':'Bearer disaster-fixture-only'}) as client:
        result=(await client.get('/operator/diagnostics')).json()
        assert result['disaster_recovery']['epoch']>=1
        assert result['disaster_recovery']['restores'][0]['status']=='committed'
        assert not result['disaster_recovery']['restores'][0]['artifact_currently_verified']
        assert all(not t['execution_completed'] for t in result['tasks'])
        assert (await client.post('/operator/restore',json={'target':'real'})).status_code==404

@pytest.mark.asyncio
async def test_missing_preparation_blocks_operator_health(bound,monkeypatch):
    a,g,restored=bound
    (g.directory/f"restore-{restored['restore_id']}.prepared.json").unlink()
    monkeypatch.setattr(server.settings.server,'api_token','disaster-fixture-only')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic',headers={'Authorization':'Bearer disaster-fixture-only'}) as client:
        response=await client.get('/operator/diagnostics')
        assert response.status_code==503 and response.json()['error']=='restore_history_incomplete'

@pytest.mark.asyncio
async def test_disaster_report_never_claims_execution_from_restore(bound):
    from app.agent.reporter import reporter
    a,g,restored=bound
    report=await reporter.build_report()
    assert '4 pending (admitted, execution held)' in report
    assert 'Ledger integrity verified' in report
    assert not restored['execution_enabled'] and not restored['runtime_activation_allowed']
