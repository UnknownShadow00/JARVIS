"""Rollover/restore contracts, synthetic keys, disposable SQLite state only."""
from datetime import UTC,datetime,timedelta
import json
from pathlib import Path
import uuid
import pytest
from app.agent.authority import Authority,AuthorityError
from app.agent.ledger import LedgerGuard
from app.agent.recovery import OperatorPermits,RecoveryActions
from app.agent.runtime import SERVICE_ACTOR as ACTOR

KEY=b'synthetic-sprint3-ledger-only-key-00000000'
OPKEY=b'synthetic-sprint3-operator-only-key-000000'

def key():return str(uuid.uuid4())

@pytest.fixture
def env(tmp_path):
    store=key();anchors=tmp_path/'protected';db=tmp_path/'db'/'state.sqlite';exports=tmp_path/'exports';exports.mkdir(mode=0o700)
    g=LedgerGuard(anchors,KEY,store,initialize=True,rollover=True,epoch_capacity=4,recovery=True)
    a=Authority(db,allow_simulation=True,ledger=g)
    permits=OperatorPermits(OPKEY);actions=RecoveryActions(a,permits)
    yield a,g,actions,permits,{'db':db,'anchors':anchors,'exports':exports,'store_id':store,'parent':tmp_path}
    a.close()

def issue(env,command,payload,request_id):
    a,g,actions,permits,paths=env;now=datetime.now(UTC)
    return permits.issue(request_id=request_id,principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())

def exported(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'held synthetic task')
    export_id=key();payload={'export_id':export_id,'destination':str(paths['exports'])}
    return actions.export(ACTOR,export_id,paths['exports'],issue(env,'export_ledger',payload,export_id))

def test_rollover_retains_checkpoint_identities(env):
    a,g,actions,permits,paths=env
    old={p.name:p.read_bytes() for p in paths['anchors'].glob('*.json')}
    for _ in range(8):a.submit(ACTOR,key(),'synthetic')
    head,pending,history=g.history()
    assert g._epoch>=2 and not pending
    assert [h['sequence'] for h in history]==list(range(1,head['sequence']+1))
    assert all((paths['anchors']/name).read_bytes()==raw for name,raw in old.items())
    assert a.readiness()['ledger_integrity']['epoch']>=2

def test_export_attestation_survives_source_database_loss(env):
    a,g,actions,permits,paths=env
    result=exported(env)
    assert result['attestation']['verified']
    verified=g.verify_export(paths['exports']/result['export']['export_id'])
    assert verified['format']=='jarvis-ledger-export-v2'
    assert g.verify_export_attestation(verified)['completion_receipt_id']==result['publication']['request_id']

def test_wrong_key_and_expired_reference_refused(env):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'value')
    now=datetime.now(UTC)
    ref=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=1)).isoformat())
    with pytest.raises(AuthorityError,match='checkpoint_trust_key_mismatch'):
        LedgerGuard(paths['anchors'],b'wrong-synthetic-key-0000000000000000000',paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)
    ref['expires_at']=(now-timedelta(milliseconds=1)).isoformat()
    with pytest.raises(AuthorityError,match='checkpoint_trust_expired'):
        LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True,trust_context=ref)

def test_total_generation_capacity_is_conservative(env):
    a,g,actions,permits,paths=env
    g.max_epochs=1
    a.submit(ACTOR,key(),'one');a.submit(ACTOR,key(),'two')
    with pytest.raises(AuthorityError,match='checkpoint_generation_capacity'):
        a.submit(ACTOR,key(),'refused')

@pytest.mark.parametrize('fault',['rollover_intent_durable','rollover_link_durable'])
def test_interrupted_rollover_is_not_silently_reset(env,fault):
    a,g,actions,permits,paths=env
    a.submit(ACTOR,key(),'one');a.submit(ACTOR,key(),'two')
    def stop(stage):
        if stage==fault:raise RuntimeError('power-loss-like injected interruption')
    g._fault=stop
    with pytest.raises(RuntimeError):a.submit(ACTOR,key(),'interrupted')
    a.close()
    new=LedgerGuard(paths['anchors'],KEY,paths['store_id'],rollover=True,epoch_capacity=4,recovery=True)
    if fault=='rollover_intent_durable':
        with pytest.raises(AuthorityError,match='checkpoint_rollover_incomplete'):Authority(paths['db'],ledger=new)
    else:
        recovered=Authority(paths['db'],ledger=new)
        try:assert recovered.readiness()['ledger_integrity']['epoch']==1
        finally:recovered.close()
