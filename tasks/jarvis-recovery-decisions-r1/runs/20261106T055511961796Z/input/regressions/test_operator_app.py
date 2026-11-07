"""Actual configured app diagnostics and operator CLI; no provider requests."""
from datetime import UTC, datetime, timedelta
import json
import os
from pathlib import Path
import uuid

import httpx
import pytest

from app.agent.authority import Authority
from synthetic_authority import fixture_authority as Authority
from app.agent.execution import ExecutionPipeline, SimulatedPolicy
from app.agent.ledger import LedgerGuard
from app.agent import runtime
from app import server,cli

KEY=b'synthetic-operator-app-ledger-key-000000000'


@pytest.fixture
def bound(tmp_path):
    previous=runtime._authority;previous_worker=runtime._execution_worker
    runtime._authority=None;runtime._execution_worker=None
    store_id=str(uuid.uuid4());anchors=tmp_path/'protected'
    a=Authority(tmp_path/'state'/'db',allow_simulation=True,ledger=LedgerGuard(anchors,KEY,store_id,initialize=True))
    runtime.bind_authority(a)
    yield a,anchors,store_id
    runtime.close_authority();runtime._authority=previous;runtime._execution_worker=previous_worker


@pytest.mark.asyncio
async def test_operator_route_requires_explicit_token_and_has_no_mutations(bound,monkeypatch):
    a,anchors,store_id=bound
    monkeypatch.setattr(server.settings.server,'api_token','')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic') as client:
        assert (await client.get('/operator/diagnostics')).status_code==401
        monkeypatch.setattr(server.settings.server,'api_token','operator-fixture-token')
        assert (await client.get('/operator/diagnostics')).status_code==401
        client.headers['Authorization']='Bearer operator-fixture-token'
        before=a._ledger._head.copy()
        response=await client.get('/operator/diagnostics')
        assert response.status_code==200 and response.json()['consistent']
        assert response.json()['ledger_integrity']['verified']
        assert a._ledger._head==before
        assert (await client.post('/operator/diagnostics',json={'command':'complete'})).status_code==405
        assert (await client.post('/operator/recover',json={'command':'retry'})).status_code==404
        assert a._ledger._head==before


@pytest.mark.asyncio
async def test_operator_cli_consumes_actual_api_and_reports_unavailable(bound,monkeypatch,capsys):
    a,anchors,store_id=bound
    op=str(uuid.uuid4());a.submit(runtime.SERVICE_ACTOR,op,'held')
    monkeypatch.setattr(server.settings.server,'api_token','operator-fixture-token')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic',headers={'Authorization':'Bearer operator-fixture-token'}) as client:
        payload=(await client.get('/operator/diagnostics',params={'task_id':op})).json()
    monkeypatch.setattr(cli,'_get',lambda *args,**kwargs:payload)
    assert cli.main(['recovery','--task-id',op])==0
    assert json.loads(capsys.readouterr().out)['tasks'][0]['execution_completed'] is False
    monkeypatch.setattr(cli,'_get',lambda *args,**kwargs:None)
    assert cli.main(['recovery'])==1
    assert 'No retry was attempted' in capsys.readouterr().err
    assert cli.main(['recovery','--task-id','invalid'])==2


def test_quiesced_cli_key_descriptor_does_not_rewrite_store(bound,capsys):
    from app.agent.operator_cli import main
    a,anchors,store_id=bound
    op=str(uuid.uuid4());a.submit(runtime.SERVICE_ACTOR,op,'held')
    a.close()
    before=a.path.read_bytes()
    read_fd,write_fd=os.pipe()
    try:
        os.write(write_fd,KEY);os.close(write_fd)
        assert main(['--database',str(a.path),'--checkpoints',str(anchors),'--store-id',store_id,'--key-fd',str(read_fd)])==0
        output=capsys.readouterr().out
        assert KEY.decode() not in output
        assert json.loads(output)['tasks'][0]['original_request_id']==op
    finally:os.close(read_fd)
    assert a.path.read_bytes()==before


@pytest.mark.asyncio
async def test_guard_corruption_blocks_application_readiness(bound,monkeypatch):
    a,anchors,store_id=bound
    monkeypatch.setattr(server.settings.server,'api_token','operator-fixture-token')
    a._conn.execute('UPDATE control SET epoch=epoch+1')
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=server.app),base_url='http://synthetic',headers={'Authorization':'Bearer operator-fixture-token'}) as client:
        response=await client.get('/ready')
        assert response.status_code==503 and response.json()['error']=='ledger_checkpoint_mismatch'
        assert (await client.post('/execution/tasks',json={'request_id':str(uuid.uuid4()),'goal':'held','capability':'synthetic.echo','payload':{'value':'x'},'expires_at':(datetime.now(UTC)+timedelta(minutes=1)).isoformat()})).status_code==503


@pytest.mark.asyncio
async def test_operator_report_does_not_claim_admission_is_completion(bound):
    from app.agent.reporter import reporter
    a,anchors,store_id=bound
    a.submit(runtime.SERVICE_ACTOR,str(uuid.uuid4()),'held')
    report=await reporter.build_report()
    assert '1 pending (admitted, execution held)' in report
    assert 'Ledger integrity verified' in report and 'automatic retry disabled' in report
