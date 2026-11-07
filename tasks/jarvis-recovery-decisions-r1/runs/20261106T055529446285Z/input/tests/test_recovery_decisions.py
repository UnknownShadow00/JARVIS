"""Real SQLite/guard/restore tests; execute only with the disposable offline runner."""
from datetime import UTC, datetime, timedelta
import copy
import errno
import hashlib
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import pytest

from app.agent.authority import AuthorityError
from app.agent.ledger import LedgerGuard, encode
from app.agent.enrollment import fingerprint
from app.agent.recovery import OperatorPermits
from app.agent.recovery_decisions import RecoveryRegistry, verify_receipt
from app.agent.runtime import SERVICE_ACTOR as ACTOR
from enrollment_fixtures import uid, KEY, OPKEY
from test_authority_enrollment import branch, env


def times(seconds=120):
    now=datetime.now(UTC)
    return (now-timedelta(seconds=1)).isoformat(),(now+timedelta(seconds=seconds)).isoformat()


def grant(g, request_id, command, payload, *, principal='synthetic-sprint5-reviewer', seconds=120):
    start,end=times(seconds)
    return OperatorPermits(OPKEY).issue(request_id=request_id,principal=principal,scope=ACTOR.scope,
        command='recovery_'+command,payload=payload,checkpoint=g.history()[0],issued_at=start,expires_at=end)


def reference(g):
    start,end=times()
    return g.trust_reference(valid_from=start,expires_at=end)


@pytest.fixture
def registry(branch):
    a,target,request,unknown,enrollment=branch;g=a._ledger
    root=target.parent.parent
    for name in ('registry-data','registry-custody'):(root/name).mkdir(mode=0o700)
    config={'format':'jarvis-recovery-registry-v1','registry_id':uid(),'store_id':g.store_id,'key_id':g.key_id,
            'database':str(root/'registry-data/registry.sqlite'),'custody':str(root/'registry-custody'),
            'checkpoints':str(g.directory),'initial_reference':reference(g),'capacity':128,'disposable_only':True}
    external={'registry_id':config['registry_id'],'sequence':0,'event_sha256':'0'*64,
              'witness':{'renewal_id':None,'checkpoint':config['initial_reference']}}
    service=RecoveryRegistry(g,config,external,OperatorPermits(OPKEY))
    op=uid();result=service.apply(ACTOR,op,'initialize',config,grant(g,op,'initialize',config),initialize=True)
    yield service,a,target,request,unknown,result


def publication_payload(g,target,request):
    from app.agent.branch_verification import BranchVerifier
    verified=BranchVerifier(g).verify(target,request)
    return {'directory':str(target),'verification_request':request,
            'verification_sha256':fingerprint({'proposal':verified['proposal'],'summary':verified['summary']})}


def proposal(env):
    s,a,target,r,unknown,_=env
    op=uid();payload=publication_payload(s.guard,target,r)
    p=grant(s.guard,op,'propose',payload)
    return op,payload,p,s.apply(ACTOR,op,'propose',payload,p)


def decision(s, proposal_id, state='APPROVED', previous=None, seconds=60):
    start,end=times(seconds)
    proposal=next(p for p in s.inspect()['proposals'] if p['proposal_id']==proposal_id)
    payload={'proposal_id':proposal_id,'proposal_sha256':fingerprint(proposal['proposal']),'state':state,'valid_from':start,'expires_at':end,'previous_decision_id':previous}
    op=uid();p=grant(s.guard,op,'decide',payload)
    return op,payload,p


def renew(s,a):
    external=s.inspect()['reference']
    s.reference=external
    # Use real protected generation rollover; no tasks or executor are resumed.
    a.submit(ACTOR,uid(),'held synthetic checkpoint advance')
    op=uid();payload={'previous_witness':external['witness'],'next_reference':reference(s.guard)}
    return op,payload,grant(s.guard,op,'renew',payload)


def test_restore_proposal_decision_receipt_restart(registry):
    s,a,target,r,unknown,_=registry
    op,payload,p,created=proposal(registry)
    before=a.get_task(ACTOR,unknown)
    status=s.inspect(op);assert status['proposals'][0]['state']=='PENDING'
    item=status['proposals'][0]['proposal']
    assert unknown in item['original_request_ids'] and item['source_manifest_sha256']
    assert item['original_occurrence_ids']==sorted(item['original_occurrence_ids'])
    d,body,permit=decision(s,op)
    result=s.apply(ACTOR,d,'decide',body,permit)
    evidence=result['receipt'];event=evidence['event']['body']
    assert verify_receipt(s.guard,evidence,registry_id=s.config['registry_id'],request_id=d,
        payload_sha256=fingerprint(body),event_sha256=fingerprint(evidence['event']),permits=OperatorPermits(OPKEY))['verified']
    restarted=RecoveryRegistry(s.guard,s.config,s.inspect()['reference'],OperatorPermits(OPKEY))
    assert restarted.inspect(d)['proposals'][0]['state']=='APPROVED'
    assert restarted.apply(ACTOR,d,'decide',body,permit)['replayed']
    assert a.get_task(ACTOR,unknown)==before
    assert event['result']['activation_authorized'] is False
    assert not restarted.inspect()['activation_authorized']
    from app.agent.authority import Authority
    with pytest.raises(AuthorityError,match='restore_activation_prohibited'):Authority(target/'state.sqlite')


def test_replay_identical_only_and_branch_duplicate(registry):
    s,*_=registry
    op,payload,p,result=proposal(registry)
    assert s.apply(ACTOR,op,'propose',payload,p)['receipt']==result['receipt']
    changed=copy.deepcopy(payload);changed['verification_request']['branch_id']=uid()
    with pytest.raises(AuthorityError,match='request_conflict'):s.apply(ACTOR,op,'propose',changed,p)
    changed=publication_payload(s.guard,registry[2],changed['verification_request'])
    op2=uid()
    with pytest.raises(AuthorityError,match='proposal_conflict'):s.apply(ACTOR,op2,'propose',payload,grant(s.guard,op2,'propose',payload))
    with pytest.raises(AuthorityError,match='proposal_conflict'):s.apply(ACTOR,op2,'propose',changed,grant(s.guard,op2,'propose',changed))


@pytest.mark.parametrize('state',['PENDING','REJECTED','APPROVED'])
def test_decision_states_and_revocation(registry,state):
    s,*_=registry;op,_,_,_=proposal(registry)
    d,payload,p=decision(s,op,state)
    s.apply(ACTOR,d,'decide',payload,p)
    assert s.inspect()['proposals'][0]['state']==state
    d2,p2,k2=decision(s,op,'REVOKED',d)
    if state=='REJECTED':
        with pytest.raises(AuthorityError,match='decision_conflict'):s.apply(ACTOR,d2,'decide',p2,k2)
    else:
        s.apply(ACTOR,d2,'decide',p2,k2)
        assert s.inspect()['proposals'][0]['state']=='REVOKED'
        d3,p3,k3=decision(s,op,'APPROVED',d2)
        with pytest.raises(AuthorityError,match='decision_conflict'):s.apply(ACTOR,d3,'decide',p3,k3)


@pytest.mark.parametrize('attack',['wrong_key','forged','missing','expired','wrong_operator_scope','outlives','wrong_checkpoint','future'])
def test_invalid_authorization_fails_before_admission(registry,attack):
    from app.agent.authority import Actor
    s,*_=registry;op,_,_,_=proposal(registry);d,body,p=decision(s,op)
    actor=ACTOR
    if attack=='wrong_key': p=OperatorPermits(b'x'*32).issue(**{k:v for k,v in p['body'].items() if k!='payload_hash'},payload=body)
    elif attack=='forged':p['body']['principal']='forged-identity'
    elif attack=='missing':p=None
    elif attack=='expired':
        start,end=times(-10);p=OperatorPermits(OPKEY).issue(request_id=d,principal='synthetic',scope=ACTOR.scope,command='recovery_decide',payload=body,checkpoint=s.guard.history()[0],issued_at=(datetime.now(UTC)-timedelta(seconds=30)).isoformat(),expires_at=end)
    elif attack=='wrong_operator_scope':actor=Actor('remote-client')
    elif attack=='outlives': body['expires_at']=(datetime.now(UTC)+timedelta(seconds=290)).isoformat();p=grant(s.guard,d,'decide',body)
    elif attack=='wrong_checkpoint':p=OperatorPermits(OPKEY).issue(request_id=d,principal='synthetic',scope=ACTOR.scope,command='recovery_decide',payload=body,checkpoint={},issued_at=p['body']['issued_at'],expires_at=p['body']['expires_at'])
    elif attack=='future':body['valid_from']=(datetime.now(UTC)+timedelta(seconds=5)).isoformat();p=grant(s.guard,d,'decide',body)
    before=s.inspect()['event_count']
    with pytest.raises(AuthorityError):s.apply(actor,d,'decide',body,p)
    assert s.inspect()['event_count']==before


@pytest.mark.parametrize('attack',['event','commit','wrong_key','wrong_request','wrong_digest'])
def test_forged_receipts(registry,attack):
    s,*_=registry;op,_,_,_=proposal(registry);d,body,p=decision(s,op)
    receipt=s.apply(ACTOR,d,'decide',body,p)['receipt'];digest=fingerprint(receipt['event']);expected=d
    permits=OperatorPermits(OPKEY)
    if attack=='event':receipt['event']['body']['result']['activation_authorized']=True
    elif attack=='commit':receipt['commit']['body']['sequence']+=1
    elif attack=='wrong_key':permits=OperatorPermits(b'wrong synthetic key'*3)
    elif attack=='wrong_request':expected=uid()
    else:digest='0'*64
    with pytest.raises(AuthorityError):verify_receipt(s.guard,receipt,registry_id=s.config['registry_id'],request_id=expected,payload_sha256=fingerprint(body),event_sha256=digest,permits=permits)


def test_concurrent_proposals_and_decisions(registry):
    s,*_=registry
    op=uid();payload=publication_payload(s.guard,registry[2],registry[3]);p=grant(s.guard,op,'propose',payload)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:s.apply(ACTOR,op,'propose',payload,p),range(2)))
    assert sum(x['replayed'] for x in results)==1
    requests=[decision(s,op,state) for state in ('APPROVED','REJECTED')]
    def apply(item):
        d,b,p=item
        try:s.apply(ACTOR,d,'decide',b,p);return 'won'
        except AuthorityError as exc:return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:out=list(pool.map(apply,requests))
    assert sorted(out)==['recovery_decision_conflict','won']


def test_witness_renewal_new_generation_restart_and_stale_substitution(registry):
    s,a,*_=registry;old=s.inspect()['reference']
    while s.guard._epoch==old['witness']['checkpoint']['epoch']:
        a.submit(ACTOR,uid(),'held generation advance')
    op,payload,p=renew(s,a)
    result=s.apply(ACTOR,op,'renew',payload,p)
    current=s.inspect()['reference']
    assert current['witness']['renewal_id']==op and current['witness']['checkpoint']['epoch']==1+old['witness']['checkpoint']['epoch']
    assert result['receipt']['event']['body']['result']['history_preserved']
    restarted=RecoveryRegistry(s.guard,s.config,current,OperatorPermits(OPKEY))
    assert restarted.inspect()['verified']
    bad=copy.deepcopy(payload);bad['next_reference']=reference(s.guard);op2=uid()
    with pytest.raises(AuthorityError,match='stale_substitution'):s.apply(ACTOR,op2,'renew',bad,grant(s.guard,op2,'renew',bad))
    assert s.apply(ACTOR,op,'renew',payload,p)['replayed']


@pytest.mark.parametrize('attack',['missing_custody','wrong_generation','wrong_key','rollback','missing_anchor','stale_external','expired'])
def test_witness_renewal_trust_attacks(registry,attack):
    s,a,*_=registry;op,body,p=renew(s,a)
    if attack=='missing_custody':
        with pytest.raises(AuthorityError,match='external_custody'):RecoveryRegistry(s.guard,s.config,None,s.permits)
        return
    if attack=='wrong_generation':body['next_reference']['epoch']+=1
    elif attack=='wrong_key':body['next_reference']['key_id']='0'*64
    elif attack=='rollback':body['next_reference']=s.config['initial_reference']
    elif attack=='missing_anchor':
        (s.guard._checkpoint_directory(1)/'00000001.final.json').unlink()
    elif attack=='stale_external':s.reference['witness']['renewal_id']=uid()
    elif attack=='expired':body['next_reference']['expires_at']=(datetime.now(UTC)-timedelta(seconds=1)).isoformat()
    with pytest.raises(AuthorityError):s.apply(ACTOR,op,'renew',body,grant(s.guard,op,'renew',body))


@pytest.mark.parametrize('damage',['missing_anchor','missing_row','corrupt_database','unknown_custody','external_ahead','missing_database','stale_guard'])
def test_registry_corruption_rollback_and_incomplete_history(registry,damage):
    s,*_=registry;op,_,_,_=proposal(registry)
    if damage=='missing_anchor':s._path(2,'intent').unlink()
    elif damage=='missing_row':
        conn=sqlite3.connect(s.database);conn.execute('DELETE FROM events WHERE sequence=2');conn.commit();conn.close()
    elif damage=='corrupt_database':
        with s.database.open('r+b') as f:f.write(b'not a SQLite database')
    elif damage=='unknown_custody':(s.custody/'unknown-partial').write_text('preserve')
    elif damage=='external_ahead':s.reference['sequence']=999
    elif damage=='missing_database':s.database.rename(s.database.with_suffix('.missing'))
    elif damage=='stale_guard':s.guard._pid=-1
    with pytest.raises((AuthorityError,sqlite3.Error)):s.inspect()


def test_enospc_preserves_admission_and_exact_retry(registry,monkeypatch):
    import app.agent.recovery_decisions as module
    s,*_=registry;op=uid();body=publication_payload(s.guard,registry[2],registry[3]);p=grant(s.guard,op,'propose',body)
    original=module.publish_file
    def full(path,raw):
        if path.name.endswith('.final.json'):raise OSError(errno.ENOSPC,'synthetic disk full')
        return original(path,raw)
    monkeypatch.setattr(module,'publish_file',full)
    with pytest.raises(OSError):s.apply(ACTOR,op,'propose',body,p)
    assert s.inspect(op)['operation_state']=='COMMITTED_ACKNOWLEDGMENT_UNKNOWN'
    monkeypatch.setattr(module,'publish_file',original)
    assert s.apply(ACTOR,op,'propose',body,p)['replayed']


def child_case(registry,command,stage):
    s,a,target,r,unknown,_=registry
    if command=='propose':
        op=uid();body=publication_payload(s.guard,target,r);p=grant(s.guard,op,command,body)
    elif command=='decide':
        pid,_,_,_=proposal(registry);op,body,p=decision(s,pid)
    else:op,body,p=renew(s,a)
    case={'config':s.config,'reference':s.reference,'trust':s.guard.trust_context,'command':command,
          'operation_id':op,'payload':body,'permit':p,'stage':stage,'root':str(s.directory.parent)}
    path=s.directory.parent/'child.json';path.write_text(json.dumps(case));path.chmod(0o600)
    a.close()
    process=subprocess.Popen([sys.executable,'-I','-B','-S','/input/tests/recovery_process_actor.py',str(path)])
    ready=s.directory.parent/'ready';end=time.monotonic()+8
    try:
        while not ready.exists() and time.monotonic()<end and process.poll() is None:time.sleep(.01)
        assert ready.exists(),process.poll()
        # A competing independent writer cannot acquire the protected journal.
        competitor=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True,trust_context=case['trust'])
        try:
            with pytest.raises(AuthorityError,match='owner_busy'):competitor.acquire(s.database)
        finally:competitor.close()
        process.kill();process.wait(timeout=5);assert process.returncode==-signal.SIGKILL
    finally:
        if process.poll() is None:process.kill();process.wait(timeout=5)
    g=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True,trust_context=case['trust'])
    g.acquire(s.database)
    restarted=RecoveryRegistry(g,s.config,s.reference,OperatorPermits(OPKEY))
    try:
        status=restarted.inspect(op)
        expected='NEVER_COMMITTED' if stage in {'recovery_intent_durable','recovery_before_sql_commit'} else 'COMMITTED_ACKNOWLEDGMENT_UNKNOWN' if stage=='recovery_sql_committed' else 'DURABLE_RECEIPT_ACKNOWLEDGMENT_UNKNOWN'
        assert status['operation_state']==expected
        result=restarted.apply(ACTOR,op,command,body,p)
        assert result['replayed'] and restarted.inspect(op)['verified']
        with pytest.raises(AuthorityError,match='request_conflict'):restarted.apply(ACTOR,op,command,{**body,'changed':True},p)
        record={'command':command,'stage':stage,'exitcode':process.returncode,'before':status['operation_state'],
                'after':restarted.inspect(op),'original_request_id':op,'payload_sha256':fingerprint(body)}
        evidence=Path('/work/CRASH-RECOVERY.jsonl')
        with evidence.open('a') as f:f.write(json.dumps(record)+'\n')
    finally:g.close()


@pytest.mark.parametrize('command',['propose','decide','renew'])
@pytest.mark.parametrize('stage',['recovery_intent_durable','recovery_before_sql_commit','recovery_sql_committed','recovery_receipt_durable'])
def test_independent_sigkill_registry_reconciliation(registry,command,stage):
    child_case(registry,command,stage)


def test_expired_decision_remains_historical_and_can_be_revoked(registry):
    s,*_=registry;op,_,_,_=proposal(registry)
    d,body,p=decision(s,op,seconds=.15)
    saved=s.apply(ACTOR,d,'decide',body,p)
    time.sleep(.18)
    assert s.inspect()['proposals'][0]['state']=='EXPIRED'
    # Replay acknowledges history and cannot refresh its authorization period.
    assert s.apply(ACTOR,d,'decide',body,p)['receipt']==saved['receipt']
    d2,b2,p2=decision(s,op,'REVOKED',d)
    s.apply(ACTOR,d2,'decide',b2,p2)
    assert s.inspect()['proposals'][0]['state']=='REVOKED'


def test_checkpoint_key_cannot_forge_operator_authorization_on_restart(registry):
    s,*_=registry;pid,_,_,_=proposal(registry);op,body,p=decision(s,pid)
    s.apply(ACTOR,op,'decide',body,p)
    event,_=s.guard._read(s._path(3,'intent'))
    event['permit']['body']['principal']='forged-with-only-checkpoint-key'
    # An attacker with the checkpoint key can sign a consistent SQL+journal
    # rewrite, but still lacks the separately custodied operator HMAC key.
    raw=encode(s.guard.signed(event));s._path(3,'intent').write_bytes(raw)
    commit=s.guard.signed(s.commit_body(event,fingerprint(s.guard.signed(event))))
    s._path(3,'final').write_bytes(encode(commit))
    conn=sqlite3.connect(s.database)
    conn.execute('UPDATE events SET envelope=? WHERE sequence=3',(json.dumps(s.guard.signed(event),sort_keys=True,separators=(',',':')),))
    conn.commit();conn.close()
    with pytest.raises(AuthorityError,match='operator_authentication_failed'):s.inspect()


def test_signed_decision_cannot_be_rebound_to_changed_proposal(registry):
    s,*_=registry;op,_,_,_=proposal(registry);d,body,p=decision(s,op)
    body['proposal_sha256']='0'*64
    with pytest.raises(AuthorityError,match='proposal_binding'):s.apply(ACTOR,d,'decide',body,grant(s.guard,d,'decide',body))


def test_sqlite_disk_full_transaction_rolls_back_and_reconciles(registry,monkeypatch):
    s,*_=registry;op=uid();body=publication_payload(s.guard,registry[2],registry[3]);p=grant(s.guard,op,'propose',body)
    original=s._connect
    def bounded(*,write=False):
        conn=original(write=write)
        if write:
            pages=conn.execute('PRAGMA page_count').fetchone()[0]
            conn.execute(f'PRAGMA max_page_count={pages}')
        return conn
    monkeypatch.setattr(s,'_connect',bounded)
    with pytest.raises(sqlite3.OperationalError,match='full'):s.apply(ACTOR,op,'propose',body,p)
    assert s.inspect(op)['operation_state']=='NEVER_COMMITTED'
    monkeypatch.setattr(s,'_connect',original)
    assert s.apply(ACTOR,op,'propose',body,p)['replayed']


def test_stale_custody_lock_before_commit_is_fenced(registry):
    s,*_=registry;op=uid();body=publication_payload(s.guard,registry[2],registry[3]);p=grant(s.guard,op,'propose',body)
    def replace(stage):
        if stage=='recovery_intent_durable':
            (s.custody/'journal.lock').rename(s.custody/'stale.lock')
            fd=os.open(s.custody/'journal.lock',os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600);os.close(fd)
    s._fault=replace
    with pytest.raises(AuthorityError,match='owner_stale'):s.apply(ACTOR,op,'propose',body,p)


def test_readonly_inspection_has_identical_storage_bytes(registry):
    s,*_=registry;proposal(registry)
    def image():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for root in (s.directory,s.custody,s.guard.directory) for p in root.rglob('*') if p.is_file()}
    before=image();s.inspect();assert image()==before


@pytest.mark.parametrize('stage',['recovery_initial_stage_created','recovery_initial_before_schema_commit','recovery_initial_schema_committed','recovery_database_published'])
def test_independent_sigkill_initialization_publication(branch,stage):
    a,target,r,unknown,_=branch;g=a._ledger;root=target.parent.parent
    for name in ('registry-data','registry-custody'):(root/name).mkdir(mode=0o700)
    config={'format':'jarvis-recovery-registry-v1','registry_id':uid(),'store_id':g.store_id,'key_id':g.key_id,
            'database':str(root/'registry-data/registry.sqlite'),'custody':str(root/'registry-custody'),
            'checkpoints':str(g.directory),'initial_reference':reference(g),'capacity':128,'disposable_only':True}
    ext={'registry_id':config['registry_id'],'sequence':0,'event_sha256':'0'*64,'witness':{'renewal_id':None,'checkpoint':config['initial_reference']}}
    s=RecoveryRegistry(g,config,ext,OperatorPermits(OPKEY))
    op=uid();p=grant(g,op,'initialize',config)
    case={'config':config,'reference':ext,'trust':g.trust_context,'command':'initialize','operation_id':op,
          'payload':config,'permit':p,'stage':stage,'root':str(root)}
    path=root/'child.json';path.write_text(json.dumps(case));path.chmod(0o600);a.close()
    proc=subprocess.Popen([sys.executable,'-I','-B','-S','/input/tests/recovery_process_actor.py',str(path)])
    try:
        end=time.monotonic()+8
        while not (root/'ready').exists() and time.monotonic()<end and proc.poll() is None:time.sleep(.01)
        assert (root/'ready').exists();proc.kill();proc.wait(timeout=5)
        assert proc.returncode==-signal.SIGKILL
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
    new=LedgerGuard(g.directory,KEY,g.store_id,rollover=True,epoch_capacity=4,recovery=True,trust_context=case['trust']);new.acquire(s.database)
    try:
        s=RecoveryRegistry(new,config,ext,OperatorPermits(OPKEY))
        assert s.inspect(op)['operation_state']=='NEVER_COMMITTED'
        assert s.apply(ACTOR,op,'initialize',config,p,initialize=True)['replayed']
        assert s.inspect()['verified']
        with Path('/work/CRASH-RECOVERY.jsonl').open('a') as f:f.write(json.dumps({'command':'initialize','stage':stage,'exitcode':proc.returncode,'after':s.inspect(),'original_request_id':op})+'\n')
    finally:new.close()


def test_empty_generation_witness_stays_valid_after_generation_grows(registry):
    s,a,*_=registry
    s.reference=s.inspect()['reference'];g=s.guard
    g._head=g.history()[0];g.rollover()
    nxt=reference(g);op=uid();body={'previous_witness':s.reference['witness'],'next_reference':nxt}
    s.apply(ACTOR,op,'renew',body,grant(g,op,'renew',body))
    assert s.inspect()['verified']
    g.trust_context=nxt
    a.submit(ACTOR,uid(),'first held checkpoint in renewed generation')
    assert s.inspect()['verified'] and a.readiness()['ledger_integrity']['verified']


def test_conflicting_concurrent_renewals_only_one_commits(registry):
    s,a,*_=registry;op,body,p=renew(s,a);op2=uid();p2=grant(s.guard,op2,'renew',body)
    def attempt(item):
        ident,permit=item
        try:s.apply(ACTOR,ident,'renew',body,permit);return 'committed'
        except AuthorityError as exc:return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(attempt,[(op,p),(op2,p2)]))
    assert sorted(results)==['committed','recovery_witness_stale_substitution']


@pytest.mark.parametrize('phase',['intent','final'])
def test_independent_sigkill_during_partial_witness_publication(registry,phase):
    s,a,*_=registry;op,body,p=renew(s,a)
    case={'config':s.config,'reference':s.reference,'trust':s.guard.trust_context,'command':'renew',
          'operation_id':op,'payload':body,'permit':p,'stage':'partial_'+phase,'root':str(s.directory.parent)}
    path=s.directory.parent/'child.json';path.write_text(json.dumps(case));path.chmod(0o600);a.close()
    proc=subprocess.Popen([sys.executable,'-I','-B','-S','/input/tests/recovery_process_actor.py',str(path)])
    try:
        end=time.monotonic()+8
        while not (s.directory.parent/'ready').exists() and time.monotonic()<end and proc.poll() is None:time.sleep(.01)
        assert (s.directory.parent/'ready').exists();proc.kill();proc.wait(timeout=5)
        assert proc.returncode==-signal.SIGKILL
    finally:
        if proc.poll() is None:proc.kill();proc.wait(timeout=5)
    g=LedgerGuard(s.guard.directory,KEY,s.guard.store_id,rollover=True,epoch_capacity=4,recovery=True,trust_context=case['trust']);g.acquire(s.database)
    try:
        restarted=RecoveryRegistry(g,s.config,s.reference,OperatorPermits(OPKEY))
        partial=s.custody/'.stage-interrupted-witness';before=partial.read_bytes()
        with pytest.raises(AuthorityError,match='incomplete_history'):restarted.inspect()
        assert partial.read_bytes()==before and before
        with Path('/work/CRASH-RECOVERY.jsonl').open('a') as f:f.write(json.dumps({'command':'renew','stage':case['stage'],'exitcode':proc.returncode,'result':'REFUSED_PRESERVED_PARTIAL_MANUAL_QUARANTINE','original_request_id':op})+'\n')
    finally:g.close()


def test_registry_capacity_is_bounded_without_deletion(registry):
    original,a,target,r,*_=registry
    root=original.directory.parent
    for name in ('bounded-data','bounded-custody'):(root/name).mkdir(mode=0o700)
    config={**original.config,'registry_id':uid(),'capacity':4,'database':str(root/'bounded-data/state.sqlite'),'custody':str(root/'bounded-custody')}
    ext={'registry_id':config['registry_id'],'sequence':0,'event_sha256':'0'*64,'witness':{'renewal_id':None,'checkpoint':config['initial_reference']}}
    s=RecoveryRegistry(original.guard,config,ext,OperatorPermits(OPKEY));op=uid()
    s.apply(ACTOR,op,'initialize',config,grant(s.guard,op,'initialize',config),initialize=True)
    pid=uid();body=publication_payload(s.guard,target,r);s.apply(ACTOR,pid,'propose',body,grant(s.guard,pid,'propose',body))
    pending,pb,pp=decision(s,pid,'PENDING');s.apply(ACTOR,pending,'decide',pb,pp)
    approved,ab,ap=decision(s,pid,'APPROVED',pending);s.apply(ACTOR,approved,'decide',ab,ap)
    rid,rb,rp=decision(s,pid,'REVOKED',approved)
    with pytest.raises(AuthorityError,match='capacity'):s.apply(ACTOR,rid,'decide',rb,rp)
    assert s.inspect()['event_count']==4 and len(list(s.custody.glob('*.final.json')))==4
