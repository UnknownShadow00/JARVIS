"""Protected disposable ledger, default-read-only diagnosis and archive safety."""
from datetime import UTC, datetime, timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

import pytest

from app.agent.authority import Authority, AuthorityError
from app.agent.execution import ExecutionPipeline, SimulatedPolicy, phase_id
from app.agent.ledger import LedgerGuard, encode, strict_json
from app.agent.recovery import OperatorRecovery, OperatorPermits, RecoveryActions
from app.agent.runtime import SERVICE_ACTOR as ACTOR

SYNTHETIC_KEY=b'synthetic-ledger-test-key-only-000000000000'
PERMIT_KEY=b'synthetic-operator-test-key-only-000000000'


def key():return str(uuid.uuid4())


@pytest.fixture
def env(tmp_path):
    paths={'db':tmp_path/'state'/'queue.sqlite','anchors':tmp_path/'protected','exports':tmp_path/'exports','store_id':key()}
    paths['exports'].mkdir(mode=0o700)
    guard=LedgerGuard(paths['anchors'],SYNTHETIC_KEY,paths['store_id'],initialize=True)
    a=Authority(paths['db'],allow_simulation=True,ledger=guard)
    pipeline=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
    permits=OperatorPermits(PERMIT_KEY)
    actions=RecoveryActions(a,permits)
    yield a,pipeline,guard,permits,actions,paths
    a.close()


def submit(p,**changes):
    body=dict(request_id=key(),goal='operator fixture',capability='synthetic.echo',payload={'value':'evidence'},expires_at=(datetime.now(UTC)+timedelta(minutes=2)).isoformat())
    body.update(changes)
    return p.submit(ACTOR,**body)


def permit(env,command,payload,request_id=None,**changes):
    a,p,g,issuer,actions,paths=env
    now=datetime.now(UTC)
    body=dict(request_id=request_id or key(),principal='synthetic-operator',scope=ACTOR.scope,command=command,payload=payload,
              checkpoint=g._head,issued_at=now.isoformat(),expires_at=(now+timedelta(minutes=2)).isoformat())
    body.update(changes)
    return issuer.issue(**body)


def test_guarded_pipeline_readiness_and_read_only_diagnostics(env):
    a,p,g,issuer,actions,paths=env
    op=submit(p)['request_id']
    before=g._head.copy();events=a._conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    report=OperatorRecovery(a).diagnose(ACTOR,task_id=op)
    assert report['consistent'] and report['ledger_integrity']['verified']
    assert report['tasks'][0]['original_request_id']==op
    assert report['tasks'][0]['reason']=='admitted_execution_held'
    assert report['tasks'][0]['execution_completed'] is False
    assert before==g._head and events==a._conn.execute('SELECT COUNT(*) FROM events').fetchone()[0]
    p.run_once(ACTOR)
    report=OperatorRecovery(a).diagnose(ACTOR,task_id=op)
    assert report['consistent'] and report['tasks'][0]['execution_completed']
    assert a.readiness()['ledger_consistent']


def test_guard_cannot_be_omitted_or_enroll_existing_store(env,tmp_path):
    a,p,g,issuer,actions,paths=env
    a.close()
    with pytest.raises(AuthorityError,match='ledger_checkpoint_required'):Authority(paths['db'])
    plain=Authority(tmp_path/'plain'/'db');plain.close()
    wrong=LedgerGuard(tmp_path/'other-anchors',SYNTHETIC_KEY,key(),initialize=True)
    with pytest.raises(AuthorityError,match='ledger_enrollment_required'):Authority(tmp_path/'plain'/'db',ledger=wrong)


def test_state_tamper_rejected_before_dispatch(env):
    a,p,g,issuer,actions,paths=env
    submit(p)
    a._conn.execute("UPDATE records SET data=replace(data,'operator fixture','tampered') WHERE kind='task'")
    with pytest.raises(AuthorityError,match='ledger_checkpoint_mismatch'):p.run_once(ACTOR)
    assert a._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_evidence'").fetchone()[0]==0


def test_rollback_against_external_checkpoint_rejected(env,tmp_path):
    a,p,g,issuer,actions,paths=env
    backup=sqlite3.connect(tmp_path/'old.sqlite');a._conn.backup(backup);backup.close()
    submit(p);a.close()
    old=sqlite3.connect(tmp_path/'old.sqlite');target=sqlite3.connect(paths['db']);old.backup(target);target.close();old.close()
    guard=LedgerGuard(paths['anchors'],SYNTHETIC_KEY,paths['store_id'])
    with pytest.raises(AuthorityError,match='ledger_checkpoint_mismatch'):Authority(paths['db'],ledger=guard)


@pytest.mark.parametrize('damage',['missing','hmac','gap','truncated'])
def test_checkpoint_damage_fails_closed(env,damage):
    a,p,g,issuer,actions,paths=env
    submit(p);a.close()
    file=sorted(paths['anchors'].glob('*.final.json'))[-1]
    if damage=='missing':
        # Synthetic disaster only: protected files are never deleted by product code.
        for entry in paths['anchors'].glob('*.json'):entry.unlink()
    elif damage=='hmac':
        raw=json.loads(file.read_text());raw['hmac_sha256']='0'*64;file.write_text(json.dumps(raw))
    elif damage=='gap':file.rename(file.with_name('00009999.final.json'))
    else:file.write_bytes(b'{')
    guard=LedgerGuard(paths['anchors'],SYNTHETIC_KEY,paths['store_id'])
    with pytest.raises(AuthorityError):Authority(paths['db'],ledger=guard)


def test_duplicate_does_not_advance_checkpoint(env):
    a,p,g,issuer,actions,paths=env
    op=key();expiry=(datetime.now(UTC)+timedelta(minutes=1)).isoformat()
    submit(p,request_id=op,expires_at=expiry);head=g._head.copy()
    assert submit(p,request_id=op,expires_at=expiry)['replayed']
    assert g._head==head
    with pytest.raises(AuthorityError,match='request_conflict'):submit(p,request_id=op,expires_at=expiry,goal='conflict')
    assert g._head==head


def test_export_requires_admission_and_immutable_manifest(env):
    a,p,g,issuer,actions,paths=env
    submit(p);p.run_once(ACTOR)
    export_id=key();payload={'export_id':export_id,'destination':str(paths['exports'])}
    token=permit(env,'export_ledger',payload,request_id=export_id)
    result=actions.export(ACTOR,export_id,paths['exports'],token)
    verified=actions.verify_export(ACTOR,paths['exports']/export_id)
    assert verified['verified'] and verified['audit_publication_verified']
    assert result['history_deleted'] is False
    assert SYNTHETIC_KEY not in (paths['exports']/export_id/'state.jsonl').read_bytes()
    assert actions.export(ACTOR,export_id,paths['exports'],token)['publication']['replayed']
    raw=paths['exports']/export_id/'state.jsonl'
    raw.write_bytes(raw.read_bytes()+b'{}\n')
    with pytest.raises(AuthorityError,match='export_integrity_failed'):g.verify_export(raw.parent)


def test_archive_preparation_preserves_unknown_held_and_receipts(env):
    a,p,g,issuer,actions,paths=env
    completed=submit(p)['request_id'];p.run_once(ACTOR)
    held=submit(p)['request_id']
    unknown=submit(p)['request_id']
    p._claim(ACTOR,unknown)
    p._unknown(ACTOR,unknown,a.generation,'test_uncertain')
    a.cancel(ACTOR,key(),unknown)
    plan=OperatorRecovery(a).retention_plan(ACTOR,older_than=(datetime.now(UTC)+timedelta(seconds=1)).isoformat())
    assert completed in plan['eligible_for_archive']
    assert held not in plan['eligible_for_archive'] and unknown not in plan['eligible_for_archive']
    assert not plan['deletion_authorized']
    assert OperatorRecovery(a).diagnose(ACTOR,task_id=unknown)['tasks'][0]['reason']=='cancellation_requested_effect_outcome_unestablished'


@pytest.mark.parametrize('changes',[
    {'expires_at':(datetime.now(UTC)-timedelta(seconds=1)).isoformat()},
    {'scope':'different'}, {'principal':''},
])
def test_bad_permits_cannot_mutate(env,changes):
    a,p,g,issuer,actions,paths=env
    submit(p)
    request_id=key();payload={'task_id':key()}
    try:token=permit(env,'publish_synthetic_evidence',payload,request_id=request_id,**changes)
    except AuthorityError:
        assert changes.get('principal')==''
        return
    head=g._head.copy()
    with pytest.raises(AuthorityError):actions.apply(ACTOR,request_id,'publish_synthetic_evidence',payload,token)
    assert g._head==head


def test_stale_permit_and_unsafe_action_refused(env):
    a,p,g,issuer,actions,paths=env
    payload={'task_id':key()}
    token=permit(env,'publish_synthetic_evidence',payload)
    submit(p)
    with pytest.raises(AuthorityError,match='stale_operator_permit'):
        actions.apply(ACTOR,token['body']['request_id'],'publish_synthetic_evidence',payload,token)
    with pytest.raises(AuthorityError,match='unsafe_recovery_action'):
        actions.apply(ACTOR,key(),'retry_unknown',{},token)


@pytest.mark.parametrize('mode,stage',[
    ('bootstrap','checkpoint_intent_durable'),
    ('mutation','checkpoint_intent_durable'),
    ('mutation','ledger_database_committed'),
    ('mutation','checkpoint_published'),
    ('export','export_row_written'),
    ('export','export_data_durable'),
    ('export','export_before_audit_publication'),
    ('retention','checkpoint_intent_durable'),
    ('retention','ledger_database_committed'),
    ('reconcile','before_commit'),
    ('reconcile','ledger_database_committed'),
])
def test_independent_process_crashes_preserve_evidence(tmp_path,mode,stage,monkeypatch):
    import subprocess,sys,time
    if not Path('/input/source').is_dir():pytest.skip('isolated runner required')
    state=tmp_path/'case';state.mkdir(mode=0o700)
    exports=state/'exports';exports.mkdir(mode=0o700)
    config={'mode':mode,'stage':stage,'db':str(state/'state'/'db.sqlite'),'anchors':str(state/'protected'),
            'exports':str(exports),'ready':str(state/'ready'),'store_id':key(),'task_id':key(),'request_id':key(),'export_id':key()}
    command=state/'command.json';command.write_text(json.dumps(config))
    with (state/'stdout').open('w') as out,(state/'stderr').open('w') as err:
        child=subprocess.Popen([sys.executable,'-I','-B','-S',str(Path(__file__).with_name('ledger_process_actor.py')),str(command)],stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,env={'LANG':'C.UTF-8'})
        try:
            deadline=time.monotonic()+4
            while not Path(config['ready']).exists() and child.poll() is None and time.monotonic()<deadline:time.sleep(.01)
            assert Path(config['ready']).exists(),(state/'stderr').read_text()
            child.kill();child.wait(timeout=1)
            assert child.returncode<0
        finally:
            if child.poll() is None:child.kill()
            child.wait(timeout=1)
    guard=LedgerGuard(config['anchors'],SYNTHETIC_KEY,config['store_id'])
    a=Authority(config['db'],allow_simulation=True,ledger=guard)
    try:
        actions=RecoveryActions(a,OperatorPermits(PERMIT_KEY))
        assert a.readiness()['ledger_integrity']['verified']
        if mode=='bootstrap':assert a.list_tasks(ACTOR)==[]
        if mode=='mutation':
            receipt=a.receipt(ACTOR,config['request_id'])
            assert (receipt is not None)==(stage!='checkpoint_intent_durable')
        if mode=='export':
            target=exports/config['export_id']
            if stage=='export_before_audit_publication':
                with pytest.raises(AuthorityError,match='export_audit_publication_missing'):actions.verify_export(ACTOR,target)
                # Future simulated clock makes original permit expired; durable
                # authenticated admission authorizes audit-only continuation.
                import app.agent.recovery as module
                class Future(datetime):
                    @classmethod
                    def now(cls,tz=None):return datetime.now(UTC)+timedelta(hours=1)
                monkeypatch.setattr(module,'datetime',Future)
                publication=actions.reconcile_admitted_export(ACTOR,config['export_id'],exports)
                assert publication['operation']=='operator_export_complete'
                assert actions.reconcile_admitted_export(ACTOR,config['export_id'],exports)['replayed']
                assert actions.verify_export(ACTOR,target)['audit_publication_verified']
            else:
                with pytest.raises(AuthorityError):actions.reconcile_admitted_export(ACTOR,config['export_id'],exports)
                assert a.receipt(ACTOR,phase_id(config['export_id'],'export_complete')) is None
            assert len(a.list_tasks(ACTOR))==1
        if mode=='retention':
            record=a._conn.execute("SELECT data FROM records WHERE kind='archive_preparation'").fetchall()
            assert bool(record)==(stage=='ledger_database_committed')
            assert len(a.list_tasks(ACTOR))==1
            assert a.get_task(ACTOR,config['task_id'])['status']=='simulated_completed'
            if record:assert json.loads(record[0][0])['history_deleted'] is False
        if mode=='reconcile':
            p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
            p.registry._executor.execute=lambda *args:(_ for _ in ()).throw(AssertionError('redispatch'))
            p.reconcile(ACTOR)
            assert a.get_task(ACTOR,config['task_id'])['status']=='simulated_completed'
            assert a._conn.execute('SELECT COUNT(*) FROM receipts WHERE request_id=?',(phase_id(config['task_id'],'publish'),)).fetchone()[0]==1
    finally:a.close()


def test_archive_mutation_has_verified_export_and_preserves_all_rows(env):
    a,p,g,issuer,actions,paths=env
    op=submit(p)['request_id'];p.run_once(ACTOR)
    export_id=key();token=permit(env,'export_ledger',{'export_id':export_id,'destination':str(paths['exports'])},request_id=export_id)
    result=actions.export(ACTOR,export_id,paths['exports'],token)
    cutoff=(datetime.now(UTC)+timedelta(seconds=1)).isoformat()
    request_id=key();payload={'export_id':export_id,'manifest_sha256':result['export']['manifest_sha256'],'older_than':cutoff}
    token=permit(env,'prepare_archive',payload,request_id=request_id)
    receipts=a._conn.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]
    prepared=actions.prepare_archive(ACTOR,request_id,paths['exports']/export_id,cutoff,token)
    assert prepared['result']['plan']['eligible_for_archive']==[op]
    assert not prepared['result']['history_deleted']
    assert a._conn.execute('SELECT COUNT(*) FROM receipts').fetchone()[0]==receipts+1
    assert a.get_task(ACTOR,op)['result']['output']=='evidence'


def test_readonly_offline_diagnosis_does_not_take_ownership(env):
    from app.agent.recovery import inspect_offline
    a,p,g,issuer,actions,paths=env
    submit(p)
    with pytest.raises(AuthorityError,match='owner_busy'):inspect_offline(paths['db'],ACTOR)
    a.close()
    before=paths['db'].read_bytes();journal={f.name:f.read_bytes() for f in paths['anchors'].iterdir()}
    report=inspect_offline(paths['db'],ACTOR,ledger=LedgerGuard(paths['anchors'],SYNTHETIC_KEY,paths['store_id']))
    assert report['consistent'] and report['tasks'][0]['status']=='pending'
    assert paths['db'].read_bytes()==before
    assert journal=={f.name:f.read_bytes() for f in paths['anchors'].iterdir()}


@pytest.mark.parametrize('damage',['receipt','event','outbox','invalid_identity','nested_execution','owner_order','created_at'])
def test_unprotected_corruption_is_explained_without_completion(tmp_path,damage):
    a=Authority(tmp_path/'state'/'db',allow_simulation=True)
    try:
        p=ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True)
        op=submit(p)['request_id']
        if damage=='receipt':a._conn.execute('DELETE FROM receipts WHERE request_id=?',(op,))
        elif damage=='event':a._conn.execute('DELETE FROM events WHERE request_id=?',(op,))
        elif damage=='outbox':a._conn.execute("UPDATE outbox SET state='simulated_completed' WHERE task_id=?",(op,))
        elif damage=='owner_order':a._conn.execute("UPDATE events SET data=replace(data,'\"generation\":1','\"generation\":0') WHERE seq=1")
        else:
            row=a._get('task',op,ACTOR.scope)
            if damage=='invalid_identity':row['task_id']='invalid'
            elif damage=='created_at':row['created_at']='invalid'
            else:row['execution']={}
            a._put('task',op,ACTOR.scope,row)
        report=OperatorRecovery(a).diagnose(ACTOR)
        assert not report['consistent'] and report['issues']
        assert not any(t['execution_completed'] for t in report['tasks'])
        with pytest.raises(AuthorityError,match='ledger_inconsistent'):a.readiness()
    finally:a.close()


def test_checkpoint_publication_io_failure_and_storage_exhaustion(env,monkeypatch):
    import app.agent.ledger as module
    a,p,g,issuer,actions,paths=env
    original=module.publish_file
    def exhausted(path,raw):
        if path.name.endswith('.final.json'):raise OSError(28,'synthetic ENOSPC')
        return original(path,raw)
    monkeypatch.setattr(module,'publish_file',exhausted)
    op=key()
    with pytest.raises(AuthorityError,match='ledger_commit_reconcile'):submit(p,request_id=op)
    with pytest.raises(AuthorityError,match='authority_unavailable'):a.readiness()
    a.close();monkeypatch.setattr(module,'publish_file',original)
    recovered=Authority(paths['db'],allow_simulation=True,ledger=LedgerGuard(paths['anchors'],SYNTHETIC_KEY,paths['store_id']))
    try:assert recovered.receipt(ACTOR,op)['result']['status']=='pending'
    finally:recovered.close()
