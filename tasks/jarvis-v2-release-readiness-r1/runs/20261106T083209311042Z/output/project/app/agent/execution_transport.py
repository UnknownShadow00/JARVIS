"""Disabled-by-default synthetic AF_UNIX transport integrated with Authority.

Only fixed pure synthetic endpoints exist. No path, URL, subprocess, tool plugin,
Proxmox action or real executor is accepted. The co-located endpoint uses the SAME
Authority transaction writer for durable replay protection; this exercises IPC and
independent operator authorization, not OS privilege separation or live transport.
"""
from datetime import UTC, datetime
import hashlib
from functools import wraps
import hmac
import os
import socket
import struct
import time

from app.agent.authority import Actor, AuthorityError, canonical
from app.agent.ledger import encode, strict_json
from app.agent.execution import SyntheticExecutor, phase_id
from app.agent.recovery import OperatorPermits

ENDPOINTS = {'synthetic.local.echo-v1': frozenset({'synthetic.echo'}),
             'synthetic.local.hash-v1': frozenset({'synthetic.sha256'})}
MAX_FRAME = 32768


def boundary_errors(method):
    @wraps(method)
    def checked(*args,**kwargs):
        try:return method(*args,**kwargs)
        except (KeyError,TypeError,ValueError,IndexError,OverflowError,RecursionError) as exc:
            raise AuthorityError('transport_evidence_invalid') from exc
    return checked


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def _sign(key, body):
    return {'body':body,'hmac_sha256':hmac.new(key,encode(body),hashlib.sha256).hexdigest()}


def _authenticate(key, envelope):
    if type(envelope) is not dict or set(envelope)!={'body','hmac_sha256'}:
        raise AuthorityError('transport_signature_invalid')
    signature=envelope['hmac_sha256']
    if type(signature) is not str or len(signature)!=64 or not hmac.compare_digest(signature,_sign(key,envelope['body'])['hmac_sha256']):
        raise AuthorityError('transport_signature_invalid')
    return envelope['body']


def _remaining(deadline):
    seconds=(datetime.fromisoformat(deadline)-datetime.now(UTC)).total_seconds()
    if seconds<=0:raise AuthorityError('transport_deadline_expired')
    return min(seconds,60)


def _send(channel, value, deadline):
    raw=encode(value)
    if len(raw)>MAX_FRAME:raise AuthorityError('transport_frame_bound')
    channel.settimeout(_remaining(deadline));channel.sendall(struct.pack('!I',len(raw))+raw)


def _receive(channel, deadline):
    def read(size):
        result=bytearray();until=time.monotonic()+_remaining(deadline)
        while len(result)<size:
            left=min(_remaining(deadline),until-time.monotonic())
            if left<=0:raise AuthorityError('transport_deadline_expired')
            channel.settimeout(left);chunk=channel.recv(size-len(result))
            if not chunk:raise AuthorityError('transport_partial_frame')
            result.extend(chunk)
        return bytes(result)
    size=struct.unpack('!I',read(4))[0]
    if not 0<size<=MAX_FRAME:raise AuthorityError('transport_frame_bound')
    return strict_json(read(size))


class SyntheticTransport:
    def __init__(self, endpoint_id, operator_verifier, request_key, response_key, *, enabled=False, fault_hook=None):
        if enabled is not True:raise AuthorityError('transport_disabled')
        if type(endpoint_id) is not str or endpoint_id not in ENDPOINTS:
            raise AuthorityError('transport_endpoint_not_allowlisted')
        if type(operator_verifier) is not OperatorPermits:
            raise AuthorityError('transport_operator_verifier_required')
        keys=(operator_verifier._key,request_key,response_key)
        if any(type(k) is not bytes or len(k)<32 for k in keys) or len(set(keys))!=3:
            raise AuthorityError('transport_independent_keys_required')
        self.endpoint_id,self.permits=endpoint_id,operator_verifier
        self._request_key,self._response_key=request_key,response_key
        self._fault=fault_hook or (lambda _:None)
        self._pid,self._uid=os.getpid(),os.getuid()
        self.invocations=0

    def configure(self, authority):
        if (not authority.allow_simulation or authority._ledger is None
            or authority._enrollment_status.get('state')!='VERIFIED' or authority._recovery_registry is None):
            raise AuthorityError('transport_verified_authority_and_recovery_required')
        if any(hmac.compare_digest(authority._ledger._key,k) for k in (self.permits._key,self._request_key,self._response_key)):
            raise AuthorityError('transport_independent_keys_required')
        self.ready(authority)
        if getattr(authority,'_transport_verifier',self) is not self:
            raise AuthorityError('transport_already_configured')
        authority._transport_verifier=self

    def _custody_ready(self, authority):
        authority._fence()
        if (os.getpid(),os.getuid())!=(self._pid,self._uid):raise AuthorityError('transport_owner_stale')
        status=authority.recovery_decision_status()
        if not status.get('configured') or not status.get('verified'):
            raise AuthorityError('recovery_reconciliation_required')
        return {'configured':True,'mode':'synthetic_socketpair_only','endpoint_id':self.endpoint_id,
                'independent_authorization_required':True,'real_execution_enabled':False}

    @boundary_errors
    def ready(self, authority):
        with authority._mutex:
            status=self._custody_ready(authority)
            rows=authority._conn.execute("SELECT id,scope FROM records WHERE kind='execution_transport_grant' ORDER BY id LIMIT 129").fetchall()
            if len(rows)>128:raise AuthorityError('transport_history_capacity')
            for op,scope in rows:
                actor=Actor(scope);task=authority._get('task',op,scope)
                self._grant(authority,actor,task,fresh=False)
                try:reply=authority._get('execution_transport_report',op,scope)
                except AuthorityError as exc:
                    if exc.code!='not_found':raise
                    reply=None
                if reply is not None:self.verify_evidence(authority,actor,task,reply)
                if task['status'] in {'simulated_completed','simulated_failed'}:
                    evidence=authority._get('execution_evidence',op,scope)
                    if self.verify_evidence(authority,actor,task,evidence['transport_receipt'])!=evidence['response']:
                        raise AuthorityError('transport_history_evidence_invalid')
            return {**status,'history_verified':True,'historical_grants':len(rows)}

    def binding(self, authority, actor, request_id, goal, spec):
        return {'format':'jarvis-synthetic-transport-grant-v1','store_id':authority._ledger.store_id,
                'scope':authority._scope(actor),'operation_id':request_id,'goal_sha256':digest(goal),
                'endpoint_id':self.endpoint_id,'spec':{k:spec[k] for k in ('capability','payload','expires_at','timeout_seconds')}}

    @boundary_errors
    def authorize(self, authority, actor, request_id, goal, spec, permit):
        self.ready(authority)
        if authority._conn.execute("SELECT COUNT(*) FROM records WHERE kind='execution_transport_grant'").fetchone()[0]>=128:
            raise AuthorityError('transport_history_capacity')
        if spec['capability'] not in ENDPOINTS[self.endpoint_id]:raise AuthorityError('transport_capability_denied')
        binding=self.binding(authority,actor,request_id,goal,spec)
        auth=self.permits.verify(permit,actor,request_id,'dispatch_synthetic_transport',binding)
        if auth['checkpoint']!=authority._ledger._head:raise AuthorityError('transport_stale_authorization')
        return {'binding':binding,'permit':strict_json(encode(permit)),'authorization':auth}

    @boundary_errors
    def _grant(self, authority, actor, task, *, fresh):
        self._custody_ready(authority)
        op=task['task_id'];spec=task['execution'];meta=spec['transport']
        grant=authority._get('execution_transport_grant',op,authority._scope(actor))
        binding=self.binding(authority,actor,op,task['goal'],spec)
        if (meta!={'endpoint_id':self.endpoint_id,'grant_sha256':digest(grant)}
            or grant['binding']!=binding or spec['capability'] not in ENDPOINTS[self.endpoint_id]):
            raise AuthorityError('transport_grant_binding_invalid')
        auth=self.permits.verify(grant['permit'],actor,op,'dispatch_synthetic_transport',binding) if fresh else self.permits.authenticate(grant['permit'])
        start=datetime.fromisoformat(auth['issued_at']);end=datetime.fromisoformat(auth['expires_at'])
        if not 0<(end-start).total_seconds()<=300:raise AuthorityError('transport_authorization_expired')
        if auth!=grant['authorization'] or (auth['request_id'],auth['scope'],auth['command'],auth['payload_hash'])!=(op,authority._scope(actor),'dispatch_synthetic_transport',digest(binding)):
            raise AuthorityError('transport_grant_binding_invalid')
        if auth['checkpoint'] not in authority._ledger.history()[2]:raise AuthorityError('transport_authority_rollback')
        return grant

    def check_task(self, authority, actor, task):
        self._grant(authority,actor,task,fresh=True)

    def _wire(self, authority, actor, task, generation):
        grant=self._grant(authority,actor,task,fresh=True)
        return {'format':'jarvis-synthetic-request-v1','operation_id':task['task_id'],
                'endpoint_id':self.endpoint_id,'store_id':authority._ledger.store_id,
                'scope':authority._scope(actor),'generation':generation,
                'nonce':phase_id(task['task_id'],'transport_nonce'),'deadline':task['execution']['deadline'],
                'grant_sha256':digest(grant),'spec_sha256':digest(grant['binding']['spec'])}

    def _live(self, authority, actor, wire):
        task=authority._get('task',wire['operation_id'],authority._scope(actor))
        if wire!=self._wire(authority,actor,task,wire['generation']):raise AuthorityError('transport_request_binding_invalid')
        row=authority._conn.execute('SELECT state,claim_id,generation FROM outbox WHERE task_id=?',(task['task_id'],)).fetchone()
        if tuple(row)!=('execution_claimed',task['task_id'],authority.generation) or wire['generation']!=authority.generation:
            raise AuthorityError('transport_stale_claim')
        if task['cancel_requested']:raise AuthorityError('transport_cancelled_before_dispatch')
        _remaining(wire['deadline'])
        return task

    @boundary_errors
    def _serve(self, authority, actor, channel, deadline):
        peer=struct.unpack('3i',channel.getsockopt(socket.SOL_SOCKET,socket.SO_PEERCRED,12))
        if peer[:2]!=(self._pid,self._uid):raise AuthorityError('transport_peer_identity_invalid')
        envelope=_receive(channel,deadline);wire=_authenticate(self._request_key,envelope)
        self._fault('transport_before_reserve')
        def reserve(scope):
            task=self._live(authority,actor,wire)
            if authority._get('execution_transport_grant',task['task_id'],scope)['binding']['endpoint_id']!=self.endpoint_id:
                raise AuthorityError('transport_endpoint_not_allowlisted')
            authority._create('execution_transport_reservation',task['task_id'],scope,
                              {'request_sha256':digest(envelope),'generation':authority.generation,'endpoint_id':self.endpoint_id})
            return {'operation_id':task['task_id'],'request_sha256':digest(envelope),'endpoint_id':self.endpoint_id,'state':'RESERVED_SYNTHETIC'}
        reserved=authority._mutate(actor,phase_id(wire['operation_id'],'transport_reserve'),
                                  'transport_reserve',{'request_sha256':digest(envelope)},reserve)
        if reserved['replayed']:raise AuthorityError('transport_replay_refused')
        self._fault('transport_reserved')
        with authority._mutex:
            authority._fence();task=self._live(authority,actor,wire)
        self.invocations+=1
        response=SyntheticExecutor().execute(task['task_id'],task['execution'])
        self._fault('transport_computed')
        reply=_sign(self._response_key,{'format':'jarvis-synthetic-response-v1','request_sha256':digest(envelope),
                                      'request':wire,'response':response,'reported_at':datetime.now(UTC).isoformat()})
        def report(scope):
            self._live(authority,actor,wire)
            authority._create('execution_transport_report',task['task_id'],scope,reply)
            return {'operation_id':task['task_id'],'endpoint_id':self.endpoint_id,'response_sha256':digest(reply),
                    'state':'REPORTED_SYNTHETIC_NOT_PUBLISHED'}
        authority._mutate(actor,phase_id(task['task_id'],'transport_report'),'transport_report',{'response_sha256':digest(reply)},report)
        self._fault('transport_reported')
        _send(channel,reply,deadline)

    @boundary_errors
    def execute(self, authority, actor, task, generation):
        wire=self._wire(authority,actor,task,generation)
        envelope=_sign(self._request_key,wire)
        left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            _send(left,envelope,wire['deadline'])
            self._serve(authority,actor,right,wire['deadline'])
            reply=_receive(left,wire['deadline'])
            self.verify_evidence(authority,actor,task,reply,require_current=True)
            self._fault('transport_reply_received')
            return reply
        finally:left.close();right.close()

    @boundary_errors
    def verify_evidence(self, authority, actor, task, reply, *, require_current=False):
        grant=self._grant(authority,actor,task,fresh=require_current)
        body=_authenticate(self._response_key,reply)
        if type(body) is not dict or set(body)!={'format','request_sha256','request','response','reported_at'} or body['format']!='jarvis-synthetic-response-v1':
            raise AuthorityError('transport_response_invalid')
        wire=body['request'];spec=task['execution'];op=task['task_id']
        if (set(wire)!={'format','operation_id','endpoint_id','store_id','scope','generation','nonce','deadline','grant_sha256','spec_sha256'}
            or wire['format']!='jarvis-synthetic-request-v1' or wire['operation_id']!=op
            or wire['endpoint_id']!=self.endpoint_id or wire['store_id']!=authority._ledger.store_id
            or wire['scope']!=authority._scope(actor) or wire['nonce']!=phase_id(op,'transport_nonce')
            or wire['deadline']!=spec['deadline'] or wire['grant_sha256']!=digest(grant)
            or wire['spec_sha256']!=digest(grant['binding']['spec'])
            or body['request_sha256']!=digest(_sign(self._request_key,wire))
            or canonical(body['response'])!=canonical(SyntheticExecutor().execute(op,spec))):
            raise AuthorityError('transport_response_binding_invalid')
        row=authority._conn.execute('SELECT claim_id,generation FROM outbox WHERE task_id=?',(op,)).fetchone()
        if tuple(row)!=(op,wire['generation']):raise AuthorityError('transport_stale_claim')
        reservation=authority._get('execution_transport_reservation',op,authority._scope(actor))
        report=authority._get('execution_transport_report',op,authority._scope(actor))
        if reservation['request_sha256']!=body['request_sha256'] or report!=reply:
            raise AuthorityError('transport_missing_durable_report')
        at=datetime.fromisoformat(body['reported_at']);auth=grant['authorization']
        if not datetime.fromisoformat(auth['issued_at'])<=at<min(datetime.fromisoformat(auth['expires_at']),datetime.fromisoformat(spec['deadline'])):
            raise AuthorityError('transport_evidence_expired')
        return body['response']


def verify_transport_evidence(authority, actor, task, evidence):
    if (task.get('execution') or {}).get('transport') is None:return
    verifier=getattr(authority,'_transport_verifier',None)
    if type(verifier) is not SyntheticTransport:raise AuthorityError('transport_verifier_required')
    if verifier.verify_evidence(authority,actor,task,evidence['transport_receipt'])!=evidence['response']:
        raise AuthorityError('transport_response_binding_invalid')


def verify_history_readonly(conn, ledger, registry, verifier):
    """Key verification on an existing mode=ro connection; no writer facade."""
    from types import SimpleNamespace
    from app.agent.authority import Authority
    def get(kind, ident, scope=None):
        row=conn.execute('SELECT scope,data FROM records WHERE kind=? AND id=?',(kind,ident)).fetchone()
        if row is None or scope is not None and row[0]!=scope:raise AuthorityError('not_found')
        return strict_json(row[1])
    view=SimpleNamespace(_mutex=ledger._operation_mutex,_conn=conn,_ledger=ledger,_get=get,
        _scope=Authority._scope,_fence=lambda:ledger.verify(conn),
        recovery_decision_status=lambda:{'configured':True,**registry.inspect()})
    return verifier.ready(view)
