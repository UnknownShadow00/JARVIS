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
    token=permit(env,'publish_synthetic_evidence',{'task_id':key()})
    submit(p)
    with pytest.raises(AuthorityError,match='stale_operator_permit'):
        actions.apply(ACTOR,token['body']['request_id'],'publish_synthetic_evidence',{'task_id':key()},token)
    with pytest.raises(AuthorityError,match='unsafe_recovery_action'):
        actions.apply(ACTOR,key(),'retry_unknown',{},token)
