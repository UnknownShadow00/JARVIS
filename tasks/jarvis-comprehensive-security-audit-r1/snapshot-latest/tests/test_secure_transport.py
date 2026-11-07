"""Actual Authority/registry/IPC tests, guarded disposable runner only."""
from datetime import UTC,datetime,timedelta
import copy
import hashlib
import json
import os
from pathlib import Path
import socket
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
import pytest
from app.agent.authority import AuthorityError,Actor
from app.agent.execution import ExecutorRegistry,SyntheticExecutor,ExecutionPipeline,SimulatedPolicy,phase_id
from app.agent.execution_transport import SyntheticTransport,_sign,_authenticate,_receive,_send,digest,MAX_FRAME
from app.agent.recovery import OperatorRecovery,OperatorPermits
from app.agent.runtime import SERVICE_ACTOR as ACTOR
from transport_fixtures import provision,opened,request,uid,times,EXEC_KEY,REQUEST_KEY,RESPONSE_KEY


@pytest.fixture
def env(tmp_path):
    state=provision(tmp_path/'state');a,p,t=opened(state)
    yield state,a,p,t
    a.close()


def test_actual_ipc_signed_evidence_single_writer_and_public_metadata(env):
    state,a,p,t=env;r=request(p);submitted=p.submit(ACTOR,**r)
    assert submitted['result']['status']=='pending' and 'hmac_sha256' not in json.dumps(submitted)
    done=p.run_once(ACTOR);op=r['request_id']
    assert done['result']['status']=='simulated_completed' and t.invocations==1
    assert done['result']['result']['operation_id']==op and done['result']['result']['output']=='synthetic-safe'
    assert p.run_once(ACTOR) is None
    evidence=a._get('execution_evidence',op,ACTOR.scope)
    assert evidence['source']=='synthetic_authenticated_transport'
    assert t.verify_evidence(a,ACTOR,a.get_task(ACTOR,op),evidence['transport_receipt'])==evidence['response']
    diag=OperatorRecovery(a).diagnose(ACTOR)
    assert diag['consistent'] and diag['tasks'][0]['transport']['report_present']
    assert a.readiness()['recovery_decisions']['verified']
    assert p.submit(ACTOR,**r)['replayed'] and t.invocations==1
    assert 'hmac_sha256' not in json.dumps(a.receipt(ACTOR,op))
    assert a._conn.execute('SELECT count(*) FROM events WHERE request_id=?',(phase_id(op,'transport_reserve'),)).fetchone()[0]==1


@pytest.mark.parametrize('attack',['wrong_operator_key','forged','scope','id','payload','capability','goal','checkpoint','expiry','endpoint'])
def test_invalid_transport_grants_never_admit_or_invoke(env,attack):
    _,a,p,t=env;r=request(p);permit=r['transport_permit']
    if attack=='wrong_operator_key':permit['hmac_sha256']='0'*64
    elif attack=='forged':permit['body']['principal']='forged-operator'
    elif attack=='scope':permit['body']['scope']='outside'
    elif attack=='id':r['request_id']=uid()
    elif attack=='payload':r['payload']['value']='changed'
    elif attack=='capability':r['capability']='shell.exec'
    elif attack=='goal':r['goal']='changed'
    elif attack=='checkpoint':a.submit(ACTOR,uid(),'makes grant stale')
    elif attack=='expiry':r['expires_at']=(datetime.now(UTC)-timedelta(seconds=1)).isoformat()
    else:r['transport_permit']['body']['payload_hash']=digest({'endpoint_id':'https://not-allowed'})
    with pytest.raises(AuthorityError):p.submit(ACTOR,**r)
    assert a.receipt(ACTOR,r['request_id']) is None and t.invocations==0


@pytest.mark.parametrize('endpoint',['https://example.invalid','/run/g6k-pve-broker/request.sock','proxmox.inspect','synthetic.local.echo-v2'])
def test_no_arbitrary_or_real_destination(endpoint):
    with pytest.raises(AuthorityError,match='allowlisted'):SyntheticTransport(endpoint,OperatorPermits(EXEC_KEY),REQUEST_KEY,RESPONSE_KEY,enabled=True)


def test_disabled_by_default_sealed_types_and_independent_keys(env):
    _,a,_,_=env
    with pytest.raises(AuthorityError,match='transport_disabled'):SyntheticTransport('synthetic.local.echo-v1',OperatorPermits(EXEC_KEY),REQUEST_KEY,RESPONSE_KEY)
    with pytest.raises(AuthorityError,match='independent_keys'):SyntheticTransport('synthetic.local.echo-v1',OperatorPermits(EXEC_KEY),EXEC_KEY,RESPONSE_KEY,enabled=True)
    class Tool:
        def execute(self,*args):raise AssertionError('real tool must never be called')
    with pytest.raises(AuthorityError,match='real_execution_disabled'):ExecutorRegistry(enabled=True).register(Tool())
    with pytest.raises(AuthorityError,match='real_execution_disabled'):ExecutionPipeline(a,SimulatedPolicy(ACTOR.scope),enabled=True,transport=Tool())


@pytest.mark.parametrize('damage',['response_signature','request_signature','response_payload','operation_id','generation','partial_frame','oversized','duplicate_json'])
def test_protocol_forgery_and_bounded_frames(env,damage,monkeypatch):
    _,a,p,t=env;r=request(p);p.submit(ACTOR,**r)
    if damage=='request_signature':
        import app.agent.execution_transport as module
        original=module._authenticate
        def bad(key,envelope):
            if key==REQUEST_KEY:envelope=copy.deepcopy(envelope);envelope['hmac_sha256']='0'*64
            return original(key,envelope)
        monkeypatch.setattr(module,'_authenticate',bad)
    elif damage in {'partial_frame','oversized','duplicate_json'}:
        left,right=socket.socketpair()
        try:
            end=times()[1]
            if damage=='partial_frame':left.sendall(struct.pack('!I',5)+b'{}');left.shutdown(socket.SHUT_WR)
            elif damage=='oversized':left.sendall(struct.pack('!I',MAX_FRAME+1))
            else:
                raw=b'{"request_id":1,"request_id":2}';left.sendall(struct.pack('!I',len(raw))+raw)
            with pytest.raises(AuthorityError):_receive(right,end)
        finally:left.close();right.close()
        return
    else:
        original=t.verify_evidence
        def forged(authority,actor,task,reply,**options):
            reply=copy.deepcopy(reply)
            if damage=='response_signature':reply['hmac_sha256']='0'*64
            elif damage=='response_payload':reply['body']['response']['output']='forged'
            elif damage=='operation_id':reply['body']['response']['operation_id']=uid()
            else:reply['body']['request']['generation']+=1
            return original(authority,actor,task,reply,**options)
        monkeypatch.setattr(t,'verify_evidence',forged)
    result=p.run_once(ACTOR)
    assert result['result']['status']=='unknown'
    assert a.receipt(ACTOR,phase_id(r['request_id'],'publish')) is None


@pytest.mark.parametrize('stage',['transport_before_reserve','transport_reserved','transport_computed','transport_reported','transport_reply_received'])
def test_cancel_and_deadline_during_handoff_remain_conservative(env,stage):
    _,a,p,t=env;r=request(p);p.submit(ACTOR,**r)
    def fault(point):
        if point==stage:
            a.cancel(ACTOR,uid(),r['request_id'])
            raise TimeoutError('synthetic boundary interruption')
    t._fault=fault
    result=p.run_once(ACTOR)
    assert result['result']['status']=='unknown' and result['result']['cancel_requested']
    assert p.run_once(ACTOR) is None
    if stage in {'transport_before_reserve','transport_reserved'}:assert t.invocations==0


def test_duplicate_concurrent_submissions_and_dispatch(env):
    _,a,p,t=env;r=request(p)
    with ThreadPoolExecutor(max_workers=2) as pool:receipts=list(pool.map(lambda _:p.submit(ACTOR,**r),range(2)))
    assert sum(x['replayed'] for x in receipts)==1
    def dispatch(_):
        try:return p.run_once(ACTOR)
        except AuthorityError as exc:return exc.code
    with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(dispatch,range(2)))
    assert t.invocations==1 and a.get_task(ACTOR,r['request_id'])['status']=='simulated_completed'


def test_recovery_witness_failure_blocks_each_boundary(env):
    _,a,p,t=env;r=request(p);p.submit(ACTOR,**r)
    def revoke_witness(stage):
        if stage=='transport_before_reserve':a._recovery_registry._path(1,'final').rename(a._recovery_registry.custody/'missing-final')
    t._fault=revoke_witness
    try:
        assert p.run_once(ACTOR)['result']['status']=='unknown'
        with pytest.raises(AuthorityError):a.readiness()
        assert t.invocations==0
    finally:(a._recovery_registry.custody/'missing-final').rename(a._recovery_registry._path(1,'final'))


def test_expired_queued_permit_is_terminal_and_does_not_stall_next_task(env):
    _,a,p,t=env;r=request(p,seconds=.15);p.submit(ACTOR,**r);time.sleep(.18)
    second=request(p,value='next-safe');p.submit(ACTOR,**second)
    assert p.run_once(ACTOR)['result']['status']=='timed_out'
    assert p.run_once(ACTOR)['result']['status']=='simulated_completed'
    assert t.invocations==1 and a.get_task(ACTOR,r['request_id'])['error']=='transport_authorization_expired_no_dispatch'


@pytest.mark.parametrize('key',['operator','request','response'])
def test_restart_wrong_independent_key_refuses_historical_completion(env,key):
    state,a,p,t=env;r=request(p);p.submit(ACTOR,**r);p.run_once(ACTOR)
    if key=='operator':t.permits=OperatorPermits(b'wrong synthetic operator key'*2)
    elif key=='request':t._request_key=b'wrong synthetic request key'*2
    else:t._response_key=b'wrong synthetic response key'*2
    with pytest.raises(AuthorityError):a.readiness()


@pytest.mark.parametrize('kind',['execution_transport_grant','execution_transport_reservation','execution_transport_report'])
def test_diagnostics_rejects_empty_or_orphan_transport_history(env,kind):
    from app.agent.recovery import snapshot,analyze
    _,a,p,t=env;r=request(p);p.submit(ACTOR,**r);p.run_once(ACTOR)
    image=snapshot(a)
    row=next(x for x in image['records'] if x['kind']==kind);row['data']='{}'
    assert not analyze(image,ACTOR.scope)['consistent']


def test_authenticated_recovery_records_existing_signed_report_without_invoking(env):
    from app.agent.recovery import RecoveryActions
    from enrollment_fixtures import OPKEY
    _,a,p,t=env;r=request(p);p.submit(ACTOR,**r)
    def fault(stage):
        if stage=='transport_reported':raise OSError('synthetic response lost')
    t._fault=fault
    assert p.run_once(ACTOR)['result']['status']=='unknown' and t.invocations==1
    actions=RecoveryActions(a,OperatorPermits(OPKEY));payload={'task_id':r['request_id']}
    def grant(op,command):
        start,end=times()
        return OperatorPermits(OPKEY).issue(request_id=op,principal='synthetic-recovery-operator',scope=ACTOR.scope,
            command=command,payload=payload,checkpoint=a._ledger.history()[0],issued_at=start,expires_at=end)
    op=uid()
    with pytest.raises(AuthorityError):actions.apply(ACTOR,op,'reconcile_synthetic_transport_report',payload,{})
    result=actions.apply(ACTOR,op,'reconcile_synthetic_transport_report',payload,grant(op,'reconcile_synthetic_transport_report'))
    assert result['result']['state']=='EVIDENCE_RECORDED_NOT_PUBLISHED' and t.invocations==1
    assert a.get_task(ACTOR,r['request_id'])['status']=='unknown'
    op=uid();actions.apply(ACTOR,op,'publish_synthetic_evidence',payload,grant(op,'publish_synthetic_evidence'))
    assert a.get_task(ACTOR,r['request_id'])['status']=='simulated_completed' and t.invocations==1
