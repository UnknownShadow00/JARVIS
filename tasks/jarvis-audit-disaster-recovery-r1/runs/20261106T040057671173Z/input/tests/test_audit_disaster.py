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


def restore_ready(env):
    a,g,actions,permits,paths=env
    result=exported(env)
    now=datetime.now(UTC)
    g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    from app.agent.archive_restore import ArchiveRestorer
    restorer=ArchiveRestorer(g,permits)
    target=paths['parent']/'restores';target.mkdir(mode=0o700)
    return restorer,result,paths['exports']/result['export']['export_id'],target


def restore_permit(env,result,target,restore_id):
    payload={'export_id':result['export']['export_id'],'manifest_sha256':result['export']['manifest_sha256'],'target_parent':str(target),'restore_id':restore_id}
    return issue(env,'restore_archive',payload,restore_id)


def test_restore_reconstructs_exact_disabled_artifact(env):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key();before=g._head.copy()
    receipt=restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert receipt['verified'] and receipt['state']=='committed'
    assert not receipt['execution_enabled'] and not receipt['runtime_activation_allowed']
    assert g._head==before
    artifact=parent/restore_id
    assert restorer.verify_restored(artifact)['summary']['unresolved']==1
    assert restorer.reconcile(restore_id)['replayed']
    with pytest.raises(AuthorityError,match='restore_already_exists_reconcile'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    with pytest.raises(AuthorityError,match='ledger_checkpoint_required'):
        Authority(artifact/'state.sqlite')


def test_default_restore_requires_external_reference_and_explicit_grant(env):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env
    result=exported(env);restorer=ArchiveRestorer(g,permits)
    archive=paths['exports']/result['export']['export_id']
    with pytest.raises(AuthorityError,match='restore_external_trust_reference_required'):
        restorer.verify_archive(archive,result['export']['manifest_sha256'])
    restorer,result,archive,parent=restore_ready_existing(env,result)
    restore_id=key();token=restore_permit(env,result,parent,restore_id)
    with pytest.raises(AuthorityError,match='explicit_disposable_restore_required'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token)
    token['hmac_sha256']='0'*64
    with pytest.raises(AuthorityError,match='operator_authentication_failed'):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],token,disposable=True)
    assert list(parent.iterdir())==[]


def restore_ready_existing(env,result):
    from app.agent.archive_restore import ArchiveRestorer
    a,g,actions,permits,paths=env;now=datetime.now(UTC)
    g.trust_context=g.trust_reference(valid_from=(now-timedelta(seconds=1)).isoformat(),expires_at=(now+timedelta(minutes=10)).isoformat())
    parent=paths['parent']/'restores';parent.mkdir(mode=0o700)
    return ArchiveRestorer(g,permits),result,paths['exports']/result['export']['export_id'],parent


@pytest.mark.parametrize('damage',['missing','duplicate','modified','reordered'])
def test_archive_disaster_rejected_before_target_creation(env,damage):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    data=archive/'state.jsonl';lines=data.read_bytes().splitlines(keepends=True)
    if damage=='missing':lines.pop()
    elif damage=='duplicate':lines.append(lines[-1])
    elif damage=='modified':lines[-1]=lines[-1].replace(b'events',b'evEnts')
    else:lines[1],lines[2]=lines[2],lines[1]
    data.write_bytes(b''.join(lines))
    restore_id=key()
    with pytest.raises(AuthorityError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert list(parent.iterdir())==[]
    assert not list(g.directory.glob('restore-*.intent.json'))


def test_restored_unknown_and_cancellation_are_preserved(env):
    from app.agent.execution import ExecutionPipeline,SimulatedPolicy
    a,g,actions,permits,paths=env
    p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
    op=key()
    p.submit(ACTOR,op,'uncertain','synthetic.echo',{'value':'uncertain'},(datetime.now(UTC)+timedelta(minutes=1)).isoformat())
    p._claim(ACTOR,op);p._unknown(ACTOR,op,a.generation,'uncertain');a.cancel(ACTOR,key(),op)
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key()
    restored=restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    assert restored['summary']['unknown']==1 and restored['summary']['cancel_requested']==1
    import sqlite3
    conn=sqlite3.connect((parent/restore_id/'state.sqlite').as_uri()+'?mode=ro',uri=True)
    try:
        row=json.loads(conn.execute("SELECT data FROM records WHERE kind='task' AND id=?",(op,)).fetchone()[0])
        assert row['status']=='unknown' and row['result'] is None and row['cancel_requested']
    finally:conn.close()


@pytest.mark.parametrize('stage',['restore_intent_durable','restore_row_inserted','restore_prepared_durable','restore_target_published'])
def test_restore_failure_is_quarantined_or_reconciled(env,stage):
    a,g,actions,permits,paths=env
    restorer,result,archive,parent=restore_ready(env)
    restore_id=key()
    restorer._fault=lambda current:(_ for _ in ()).throw(RuntimeError('simulated power interruption')) if current==stage else None
    with pytest.raises(RuntimeError):
        restorer.restore(ACTOR,restore_id,archive,parent,result['export']['manifest_sha256'],restore_permit(env,result,parent,restore_id),disposable=True)
    restorer._fault=lambda _:None
    if stage in {'restore_prepared_durable','restore_target_published'}:
        assert restorer.reconcile(restore_id)['verified']
        assert restorer.verify_restored(parent/restore_id)['verified']
    else:
        with pytest.raises(AuthorityError,match='restore_incomplete_manual_quarantine'):restorer.reconcile(restore_id)
        assert not (parent/restore_id).exists()
