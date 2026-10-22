from __future__ import annotations
import asyncio, hmac, json, secrets, time, uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from .authority import Authority
from .contracts import Bindings, LegacyRelease, ProviderRequest, ProviderResult, Refused, StepContract, ViewStatus, canonical, decode, digest, strict_json
from .storage import Store, checkpoint, verify_checkpoint

ORIGINAL_INPUTS = ('Hello. Reply briefly.', 'What is two plus two?', 'Name one primary colour.', 'Please give a brief friendly greeting.')

class Provider(Protocol):
    async def request(self, request: ProviderRequest) -> ProviderResult: ...

class Delivery(Protocol):
    async def send(self, envelope: dict) -> bool: ...

@dataclass
class Session:
    id: str
    transport: str
    created: float
    used: float
    history: list[dict] = field(default_factory=list, repr=False)

class Runtime:
    """Dependency-injected isolated owner; no legacy handler, HTTP client or service registration."""
    def __init__(self, store: Store, bindings: Bindings, legacy: LegacyRelease,
                 granite: StepContract, authority: Authority, provider: Provider,
                 backups: Path, *, commitment_key: bytes, observer, view_status, clock=time.monotonic, legacy_policy=None, acceptance_guard=None, evidence_bridge=None, checkpoint_writer=None):
        self.evidence_bridge,self.checkpoint_writer=evidence_bridge,checkpoint_writer
        legacy.validate()
        self.legacy_policy, self.acceptance_guard = legacy_policy, acceptance_guard
        if type(commitment_key) is not bytes or len(commitment_key)<32:raise Refused('COMMITMENT_KEY')
        if json.loads(store.db.execute("SELECT value FROM meta WHERE key='bindings'").fetchone()[0])!=bindings.as_dict():raise Refused('PERSISTED_BINDINGS')
        if store.db.execute('SELECT child FROM lineage').fetchone()[0]!=bindings.epoch:raise Refused('EPOCH_BINDING')
        self.store,self.bindings,self.legacy,self.granite,self.authority,self.provider=store,bindings,legacy,granite,authority,provider
        self.backups,self.key,self.clock=backups,commitment_key,clock
        self.observer,self.view_status=observer,view_status
        self.sessions={};self.busy=False;self.stop_event=asyncio.Event();self.pending=set();self.last_checkpoint=None;self.delivery_record_failures=set()
        self.state='CLOSED_RECOVERY_HOLD' if store.db.execute('SELECT 1 FROM control').fetchone() or store.count() else 'CLOSED_INITIAL'
        if store.terminal():self.state=store.terminal()

    def new_session(self,transport):
        """Core-owner preparation only; not a public endpoint or an admission grant."""
        if self.store.terminal() or transport not in ('REST','WS'):raise Refused('SESSION_TRANSPORT')
        now=self.clock()
        self.sessions={k:v for k,v in self.sessions.items() if now-v.used<300 and now-v.created<1800}
        if len(self.sessions)>=2:raise Refused('SESSION_CAPACITY')
        token=secrets.token_urlsafe(32);session=Session(uuid.uuid4().hex,transport,now,now);self.sessions[token]=session
        return token,session.id

    def session(self,token,transport):
        if type(token) is not str or len(token)!=43:raise Refused('CONTINUATION')
        s=self.sessions.get(token);now=self.clock()
        if s is None or s.transport!=transport or now-s.used>=300 or now-s.created>=1800:raise Refused('CONTINUATION')
        return s

    def commitment(self,message):
        if type(message) is not str:raise Refused('REQUEST_TYPE')
        try:raw=message.encode('utf-8')
        except UnicodeError:raise Refused('REQUEST_UTF8') from None
        if not raw or len(raw)>8192:raise Refused('REQUEST_LIMIT')
        return hmac.digest(self.key,raw,'sha256').hex()

    def _checkpoint(self):
        root=(self.checkpoint_writer(self.store,self.backups) if self.checkpoint_writer is not None else checkpoint(self.store,self.backups));self.last_checkpoint=root;return root

    def control(self,raw,signature,peer,verb):
        a=self.authority.check(raw,signature,peer,verb)
        return self._apply_control(a,verb)

    def apply_protected_command(self,nonce):
        # Explicit owner invocation only; never exposed by REST/WS Bearer routes.
        from .authority_client import ServiceAuthorityClient
        if type(self.acceptance_guard) is not ServiceAuthorityClient:raise Refused('PROTECTED_GRAPH_REQUIRED')
        a=self.acceptance_guard.command(nonce)
        return self._apply_control(a,a['verb'])

    def _apply_control(self,a,verb):
        if verb not in ('OPEN_HOLD','AUTHORIZE_ONE','TERMINAL_STOP'):raise Refused('CONTROL_VERB')
        # One-use authority is checked against durable state before ANY effect,
        # including the in-memory stop; the PRIMARY KEY remains the commit-time guard.
        if self.store.db.execute('SELECT 1 FROM control WHERE nonce=?',(a['nonce'],)).fetchone():raise Refused('CONTROL_REPLAY')
        if verb=='TERMINAL_STOP':
            if hasattr(self.acceptance_guard,'approved'):self.acceptance_guard.approved(a)
            self.stop_event.set()
            try:
                self.store.stop('SIGNED_TERMINAL_STOP',approval=a)
                if self.acceptance_guard is not None:self.acceptance_guard.terminal(self.store)
            finally:self.state=self.store.terminal() or 'CLOSED_RECOVERY_HOLD'
            return
        if self.last_checkpoint is None:raise Refused('CHECKPOINT_REQUIRED')
        m=verify_checkpoint(self.last_checkpoint)
        actual_digest=digest((self.last_checkpoint/'manifest.json').read_bytes())
        recorded=self.store.db.execute('SELECT manifest_digest FROM checkpoints WHERE id=?',(self.last_checkpoint.name,)).fetchone()
        if m['purpose']!='READY' or m['accepted']!=self.store.count() or recorded!=(actual_digest,) or a['checkpoint']!=actual_digest:raise Refused('STALE_CHECKPOINT')
        # Next-permit eligibility re-proves the whole coordinated chain, not only the
        # local controller checkpoint: evidence storage health, protected high-water
        # and a coordinated bundle bound to this exact controller checkpoint.
        if self.checkpoint_writer is not None:
            from .checkpoints import validate_coordinated
            last=self.checkpoint_writer.last
            if last is None or validate_coordinated(last,minimum_accepted=self.store.count())['controller_checkpoint']!=actual_digest:raise Refused('COORDINATED_CHECKPOINT_STALE')
        if self.evidence_bridge is not None:self.evidence_bridge.validate()
        if self.acceptance_guard is not None:self.acceptance_guard.check(self.store)
        if verb=='OPEN_HOLD':
            if self.state!='CLOSED_INITIAL':raise Refused('OPEN_STATE')
            if hasattr(self.acceptance_guard,'approved'):self.acceptance_guard.approved(a)
            self.store.opening(a);self.state='OPEN_HOLD'
        else:
            if self.state not in ('OPEN_HOLD','CHECKPOINT_HOLD') or self.busy:raise Refused('ARM_STATE')
            p=a['payload']
            if not any(s.id==p['session'] and s.transport==p['transport'] for s in self.sessions.values()):raise Refused('PERMIT_SESSION')
            if type(p['request_commitment']) is not str or len(p['request_commitment'])!=64:raise Refused('PERMIT_COMMITMENT')
            if hasattr(self.acceptance_guard,'approved'):self.acceptance_guard.approved(a)
            self.store.arm(a);self.state='ARMED_ONE'

    def stop(self,reason):
        self.stop_event.set();self.store.stop(reason);self.state=self.store.terminal()
        if self.acceptance_guard is not None:self.acceptance_guard.terminal(self.store)
        self.state=self.store.terminal()

    async def drain(self,seconds=30,*,mechanism='LIFESPAN_SHUTDOWN'):
        if type(seconds) not in (int,float) or not 0<=seconds<=30:raise Refused('DRAIN_BOUND')
        if mechanism not in ('LIFESPAN_SHUTDOWN','SIGUSR1_CONTROL'):raise Refused('STOP_MECHANISM')
        started=time.monotonic()
        self.stop(mechanism)
        for task in self.pending:task.cancel()
        if self.pending:await asyncio.wait(tuple(self.pending),timeout=seconds)
        pending=sum(not t.done() for t in self.pending)
        final=None
        closer=getattr(self.provider,'aclose',None)
        if not pending and closer is not None:
            task=asyncio.create_task(closer());self.pending.add(task)
            done,_=await asyncio.wait((task,),timeout=max(0,seconds-(time.monotonic()-started)))
            if task not in done:
                task.cancel();task.add_done_callback(self._retire_task);pending=1
                self.store.stop('FINAL_CHECKPOINT_FAILED');self.state=self.store.terminal()
                if self.acceptance_guard is not None:self.acceptance_guard.terminal(self.store)
            else:
                failure=task.exception();self._retire_task(task)
                if failure is not None:
                    self.store.stop('FINAL_CHECKPOINT_FAILED');self.state=self.store.terminal()
                    if self.acceptance_guard is not None:self.acceptance_guard.terminal(self.store)
        if not pending:final=self._final_checkpoint()
        return {'pending':pending,'terminal':self.store.terminal(),'ownership_clean':self.store.clean(),'final_checkpoint':None if final is None else final.name}

    def _final_checkpoint(self):
        try:
            if self.checkpoint_writer is not None:
                self.checkpoint_writer(self.store,self.backups,final=True)
                return self.checkpoint_writer.last
            return checkpoint(self.store,self.backups,forensic=not self.store.clean() or bool(self.delivery_record_failures) or not self.store.ready())
        except Exception:
            self.store.stop('FINAL_CHECKPOINT_FAILED');self.state=self.store.terminal()
            if self.acceptance_guard is not None:self.acceptance_guard.terminal(self.store)
            return None

    def _retire_task(self,task):
        self.pending.discard(task)
        if not task.cancelled():task.exception()  # consume late exception, never late-replay/evaluate

    async def _generate(self,aid,kind,contract,messages,capture=None,native_options=None):
        if self.stop_event.is_set():raise Refused('STOPPED')
        body=canonical({'model':contract.resource.model,'messages':messages,'stream':False,'think':False,
                        'keep_alive':contract.limits.keep_alive,'options':{'num_ctx':contract.limits.context,'num_predict':contract.limits.output,**dict(contract.native_options),**(native_options or {})}})
        if len(body)>contract.limits.request_bytes:raise Refused('SERIALIZED_REQUEST_LIMIT')
        if capture is not None:self.observer.check_request(capture,body,contract)
        # Known D06 conflicts refuse before a possible-send exists, so refusal
        # counts stay truthful; races after this point remain conservatively unknown.
        precheck=getattr(self.provider,'precheck',None)
        if precheck is not None:precheck(contract.resource)
        sid=self.store.begin(aid,kind,contract.resource,digest(body))
        if hasattr(self.acceptance_guard,'possible_send'):
            self.acceptance_guard.possible_send(self.store,aid,kind,contract,digest(body))
        req=ProviderRequest(aid,sid,contract.resource,body,digest(body),self.clock()+contract.limits.deadline)
        if self.stop_event.is_set():
            # Possible-send was recorded conservatively; no fabricated release on interrupted ordering.
            self.store.unknown(sid);raise Refused('STOPPED')
        task=asyncio.create_task(self.provider.request(req));self.pending.add(task)
        waiter=asyncio.create_task(self.stop_event.wait())
        try:
            done,_=await asyncio.wait((task,waiter),timeout=contract.limits.deadline,return_when=asyncio.FIRST_COMPLETED)
            if task not in done or self.stop_event.is_set():raise Refused('PROVIDER_UNCERTAIN')
            result=task.result()
            if (type(result) is not ProviderResult or result.known_terminal is not True or (result.attempt,result.substep,result.resource,result.request_digest)!=(aid,sid,contract.resource,digest(body))):raise Refused('PROVIDER_ASSOCIATION')
            self.store.known_terminal(sid)
            if hasattr(self.acceptance_guard,'settle'):self.acceptance_guard.settle()
            value=decode(result.body,contract.limits.native_bytes)
            return value['message']['content'],sid,digest(result.body),result.body
        except BaseException:
            # known-terminal parse/proposal failures retain terminal ownership; otherwise unknown.
            self.store.unknown(sid)
            if not task.done():task.cancel()
            raise
        finally:
            waiter.cancel()
            await asyncio.gather(waiter,return_exceptions=True)
            if task.done():self._retire_task(task)
            else:task.add_done_callback(self._retire_task)

    def _append(self,s,message):
        s.history.append(message)
        while s.history and (len(s.history)>8 or sum(len(m['content'].encode()) for m in s.history)>8192):s.history.pop(0)

    async def _deliver(self,delivery,envelope,aid,session,legacy):
        task=asyncio.create_task(delivery.send(envelope));self.pending.add(task)
        def record_completion(done):
            # Local send completion remains true even after timeout/stop. No continuation/reopen.
            if not done.cancelled() and done.exception() is None and done.result() is True:
                try:
                    self.store.delivery(aid,'LOCAL_SEND_COMPLETED')
                    if self.evidence_bridge is not None:self.evidence_bridge.delivery(aid,'LOCAL_SEND_COMPLETED')
                    self._append(session,{'role':'assistant','content':legacy})
                except Exception:
                    # Never leak callback exception/response or reopen after failed audit persistence.
                    self.delivery_record_failures.add(aid);self.stop_event.set();self.state='CLOSED_RECOVERY_HOLD'
        task.add_done_callback(record_completion)
        waiter=asyncio.create_task(self.stop_event.wait())
        try:
            done,_=await asyncio.wait((task,waiter),timeout=self.legacy.delivery_deadline,return_when=asyncio.FIRST_COMPLETED)
            if task not in done or task.result() is not True:raise Refused('DELIVERY_INTERRUPTED')
        finally:
            waiter.cancel();await asyncio.gather(waiter,return_exceptions=True)
            if task.done():self._retire_task(task)
            else:task.cancel();task.add_done_callback(self._retire_task)

    async def request(self,*,transport,token,message,authenticated,delivery: Delivery):
        if self.busy:
            self.stop('CONCURRENT_INGRESS');raise Refused('BUSY_NO_QUEUE')
        if authenticated is not True:
            self.stop('AUTHENTICATION_MISMATCH');raise Refused('AUTHENTICATION_MISMATCH')
        try:
            s=self.session(token,transport);commitment=self.commitment(message)
            if self.state!='ARMED_ONE':raise Refused('ADMISSION_CLOSED')
            if self.acceptance_guard is not None:self.acceptance_guard.before_accept(self.store,transport,s.id,commitment)
            aid=self.store.accept(transport,s.id,commitment,now=self.authority.clock())
            if self.acceptance_guard is not None:self.acceptance_guard.after_accept(self.store)
        except Exception:
            self.stop('INGRESS_REFUSAL');raise Refused('INGRESS_REFUSAL') from None
        self.busy=True;self.state='INFLIGHT';history=list(s.history);s.used=self.clock();self._append(s,{'role':'user','content':message})
        try:
            capture=self.observer.capture(s.id,message,history,transport)
            if self.legacy_policy is None:raise Refused('LEGACY_POLICY_UNAVAILABLE')
            result,responder=await self.legacy_policy.route(self,aid,message)
            confidence=result.confidence
            messages=self.legacy_policy.messages(responder,message)
            legacy,_,_,_=await self._generate(aid,'LEGACY_RESPONDER',responder,messages)
            if self.legacy_policy is not None:legacy=self.legacy_policy.clean(legacy)
            if self.stop_event.is_set():raise Refused('STOPPED')
            status=self.view_status()
            if type(status) is not ViewStatus:raise Refused('VIEW_STATUS_BINDING')
            envelope={'reply':legacy,'intent':'respond','confidence':confidence,'dry_run':status.dry_run,'active':status.active}
            if transport=='WS':envelope={'type':'reply',**envelope}
            try:
                await self._deliver(delivery,envelope,aid,s,legacy)
            except BaseException:
                self.store.delivery(aid,'INTERRUPTED_UNKNOWN');raise
            # Completion callback records delivery before observation; errors never imply delivery.
            if self.store.db.execute('SELECT delivery FROM attempts WHERE id=?',(aid,)).fetchone()!=('LOCAL_SEND_COMPLETED',):raise Refused('DELIVERY_RECORD_FAILED')
            # Granite sees pre-turn bounded history, never its own output in future history.
            _,sid,native_digest,native=await self._generate(aid,'GRANITE',self.granite,[{'role':'system','content':self.granite.system_prompt},*history,{'role':'user','content':message}],capture=capture)
            observation=self.observer.observe(capture,native)
            if self.evidence_bridge is not None:
                self.evidence_bridge.commit(aid,sid,observation)
            self.store.receipt(aid,sid,native_digest,observation);self.store.settle(aid);self.state='SETTLING'
            self._checkpoint()
            if self.stop_event.is_set() or self.store.terminal():raise Refused('STOPPED_DURING_CHECKPOINT')
            self.state='CHECKPOINT_HOLD'
            if self.store.count()==4:
                self.stop('CAP_COMPLETE')
                if self.checkpoint_writer is not None and self._final_checkpoint() is None:raise Refused('FINAL_CHECKPOINT_FAILED')
            return {'attempt':aid,'legacy_delivery':'LOCAL_SEND_COMPLETED','granite':'OBSERVED','checkpoint':self.last_checkpoint.name}
        except asyncio.CancelledError:
            self.stop('CLIENT_DISCONNECT');raise
        except Exception:
            self.stop('ATTEMPT_FAILURE');raise Refused('ATTEMPT_FAILED') from None
        finally:self.busy=False
