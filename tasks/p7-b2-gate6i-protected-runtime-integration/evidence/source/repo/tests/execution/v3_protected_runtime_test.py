"""Real accept/connect sockets, SAME kernel UID. Dummy keys and fake providers only."""
import asyncio,dataclasses,json,os,socket,struct,sys,tempfile,threading,time,uuid
from pathlib import Path
import pytest
sys.path.append('/usr/lib/python3/dist-packages')
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from candidate_v3.contracts import Refused,canonical,digest,strict_json
from candidate_v3.authority import Authority,SUCCESSOR_VERB
from candidate_v3.protected_authority import Ed25519Verifier
from candidate_v3.runtime_authority import RuntimeJournal,ControllerReader,AuthorityService,token
from candidate_v3.authority_client import ServiceAuthorityClient
from candidate_v3.local_control import UnixAuthorityServer,UnixAuthorityConnection,OperatorCommandClient,ProcessPin,MAX_FRAME
from candidate_v3.lineage import successor_payload,PredecessorProof
from candidate_v3.application import build_protected_isolated_app
from candidate_v3.checkpoints import CheckpointWriter
from candidate_v3.runtime import ORIGINAL_INPUTS
from tests.execution.v3_successor_support import fresh_fixture_proof
from tests.execution.v3_integration_test import Integrated,asgi_call,scope
from tests.execution.v3_candidate_test import Sink

class ProtectedIntegrated(Integrated):
    def __init__(self,base):
        super().__init__(base)
        self.old_high=self.high
        from candidate_v3.source_memory import procedural_snapshot
        memory=procedural_snapshot((Path(__file__).parents[2]/'skills.md').read_bytes(),expected_sha256='3a61af6054795cad154b5de00e4185063d32e08e592aba315bc8ef1560e6d4a2')
        self.runtime.legacy_policy=dataclasses.replace(self.runtime.legacy_policy,memory_snapshot=memory)
        self.key=Ed25519PrivateKey.generate();public=self.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
        self.authority=Authority(self.bind,Ed25519Verifier(public,operator_id='dummy-human'),clock=lambda:100.,operator_id='dummy-human',peer_uid=os.getuid())
        self.runtime.authority=self.authority
        root=base/'protected';root.mkdir(mode=0o700)
        self.proof=fresh_fixture_proof(PredecessorProof('predecessor','a'*64,0,'b'*64))
        self.contracts=dict(legacy_router=self.router,legacy_trivial=self.trivial,legacy_normal=self.normal,granite=self.granite)
        self.journal=RuntimeJournal(root,owner_uid=os.getuid(),service_uid=os.getuid(),authority=self.authority,predecessor_reader=lambda:self.proof,identity_reader=self.bind.as_dict,provider_resources={r:digest(canonical(dataclasses.asdict(c))) for r,c in self.contracts.items()},create=True)
        self.witness=set()
        async def witnessed(request):
            result=await self.native_original(request)
            # Independent synthetic provider witness, not the runtime's clean flag.
            if result.known_terminal and (result.attempt,result.substep,result.resource,result.request_digest)==(request.attempt,request.substep,request.resource,request.request_digest):self.witness.add(request.request_digest)
            return result
        self.native_original=self.runtime.provider.request;self.runtime.provider.request=witnessed
        self.reader=ControllerReader(self.store.root,base/'coordinated',service_uid=os.getuid())
        def terminal(pending):return dict(terminal=pending['request'] in self.witness,association=pending)
        self.service=AuthorityService(self.journal,self.reader,terminal_reader=terminal,contracts=self.contracts)
        self.socket_dir=Path(tempfile.mkdtemp(prefix='u',dir=os.environ.get('P7_OFFLINE_STAGE',str(base))))
        self.pin=ProcessPin.capture(os.getuid(),os.getpid());self.servers=[];self.threads=[]
        for channel in ('operator','service'):
            server=UnixAuthorityServer(self.socket_dir/channel,self.service,channel=channel,peer_pin=self.pin,seconds=0.5)
            thread=threading.Thread(target=server.serve,daemon=True);thread.start();self.servers.append(server);self.threads.append(thread)
        self.operator=OperatorCommandClient(UnixAuthorityConnection(self.socket_dir/'operator',authority_pin=self.pin))
        self.high=ServiceAuthorityClient(UnixAuthorityConnection(self.socket_dir/'service',authority_pin=self.pin),contracts=self.contracts)
        p=successor_payload(self.proof,self.bind.as_dict())
        raw,sig=self.approval(SUCCESSOR_VERB,p,checkpoint=digest(canonical(p)))
        self.operator.submit(raw,sig)
        self.runtime.acceptance_guard=self.high
        self.writer=CheckpointWriter(base/'coordinated',evidence=self.evidence,domains=self.domains,highwater=self.high,ownership=self.ownership)
        self.runtime.checkpoint_writer=self.writer;self.runtime._checkpoint()
        self.app=build_protected_isolated_app(self.runtime,api_token=b'DUMMY_API',allowed_origins={b'http://localhost:8000'},qualification='OFFLINE_EVALUATION_ONLY')

    def approval(self,verb,payload=None,**changes):
        a=dict(verb=verb,nonce=uuid.uuid4().hex,expires=130.,bindings=self.bind.as_dict(),checkpoint=digest((self.runtime.last_checkpoint/'manifest.json').read_bytes()),payload=payload or {});a.update(changes)
        raw=canonical(a);return raw,self.key.sign(raw)

    def control(self,verb,payload=None,**changes):
        raw,sig=self.approval(verb,payload,**changes)
        self.operator.submit(raw,sig)
        self.runtime.apply_protected_command(strict_json(raw)['nonce'])
        return raw,sig

    def close(self):
        for s in self.servers:s.close()
        for t in self.threads:t.join(2)
        self.journal.close();self.old_high.close();self.store.close();self.domains.close();self.evidence.close()
        self.socket_dir.rmdir()

@pytest.fixture
def protected(tmp_path):
    f=ProtectedIntegrated(tmp_path)
    yield f
    f.close()

@pytest.mark.asyncio
async def test_protected_actual_four_turn_graph(protected):
    f=protected;assert f.runtime.state=='CLOSED_INITIAL' and not f.calls
    assert not hasattr(f.high,'db') and not hasattr(f.high,'journal') and not hasattr(f.high,'key')
    f.opened()
    for t,m in zip(('REST','REST','WS','WS'),ORIGINAL_INPUTS):
        _,sink=await f.turn(t,m)
        assert sink.messages[0]['reply']=='Legacy fixture response, sir.' and 'GRANITE' not in str(sink.messages)
    s=f.journal.read()
    assert len(s['accepted'])==4 and len(s['sends'])==11 and s['pending'] is None and s['terminal_status']=='CLOSED_COMPLETE'
    assert f.store.count()==4 and f.evidence.validate()==4
    assert f.store.db.execute('SELECT DISTINCT origin FROM attempts').fetchall()==[('OFFLINE_FIXTURE',)]
    assert all(v['options']['num_ctx']==8192 for _,v in f.calls if v['model']=='qwen3-nothink')
    assert 'GRANITE' not in str([s.history for s in f.runtime.sessions.values()])
    with pytest.raises(Refused):f.arm('WS',ORIGINAL_INPUTS[-1])

@pytest.mark.asyncio
async def test_protected_rest_ingress(protected):
    f=protected;f.opened();token_=f.arm()
    work,_,out=await asgi_call(f.app,scope('http',token_),[{'type':'http.request','body':canonical({'message':ORIGINAL_INPUTS[0]})}])
    await asyncio.wait_for(work,5)
    assert out[0]['status']==200 and len(f.journal.read()['accepted'])==1
    assert 'GRANITE' not in str(out)

@pytest.mark.parametrize('kind',['http','websocket'])
@pytest.mark.asyncio
async def test_protected_authentication_before_request(protected,kind):
    f=protected;s=scope(kind);s['headers']=[(b'authorization',b'Bearer WRONG')]
    work,_,out=await asgi_call(f.app,s,[]);await work
    assert not f.calls and not f.journal.read()['accepted']
    assert out[0].get('status',out[0].get('code')) in (401,1008)

@pytest.mark.asyncio
async def test_protected_closed_refuses(protected):
    f=protected;token_,_=f.runtime.new_session('REST')
    with pytest.raises(Refused):await f.runtime.request(transport='REST',token=token_,message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink())
    assert not f.calls and not f.journal.read()['accepted']


def test_signing_via_service_interface_refuses(protected):
    f=protected;raw,sig=f.approval('OPEN_HOLD')
    with pytest.raises(Refused):f.high.connection.call('SIGNED',dict(body=strict_json(raw),signature=sig.hex()))
    with pytest.raises(Refused):f.runtime.control(raw,sig,(os.getuid(),os.getpid()),'OPEN_HOLD')
    assert not f.journal.read()['opened']


def test_approval_is_not_acceptance_and_replay_refuses(protected):
    f=protected;raw,sig=f.control('OPEN_HOLD');f.arm()
    assert f.journal.read()['accepted']==[] and f.store.count()==0
    with pytest.raises(Refused):f.operator.submit(raw,sig)

@pytest.mark.parametrize('bad',['signature','binding','expiry','verb'])
def test_signed_command_binding(protected,bad):
    f=protected;changes={'binding':dict(bindings=dict(f.bind.as_dict(),source='stale')),'expiry':dict(expires=99),'verb':{}} .get(bad,{})
    raw,sig=f.approval('EXEC' if bad=='verb' else 'OPEN_HOLD',**changes)
    if bad=='signature':sig=b'x'*64
    with pytest.raises(Refused):f.operator.submit(raw,sig)
    assert not f.journal.read()['opened']

@pytest.mark.asyncio
async def test_consumed_permit_burns_before_d09_failure(protected):
    f=protected;f.opened();tok=f.arm();session=f.runtime.sessions[tok]
    f.high.before_accept(f.store,'REST',session.id,f.runtime.commitment(ORIGINAL_INPUTS[0]))
    assert len(f.journal.read()['accepted'])==1 and f.store.count()==0
    with pytest.raises(Refused):f.high.check(f.store)
    with pytest.raises(Refused):await f.runtime.request(transport='REST',token=tok,message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink())
    assert not f.calls

@pytest.mark.asyncio
async def test_uncertain_provider_preserves_protected_send(protected):
    f=protected;f.opened();f.block='gemma3:4b'
    task=asyncio.create_task(f.turn());await asyncio.wait_for(f.entered.wait(),3)
    f.runtime.stop('OPERATOR_STOP')
    with pytest.raises(Refused):await task
    s=f.journal.read();assert len(s['accepted'])==1 and s['pending'] is not None
    assert not f.store.clean() and f.domains.db.execute('SELECT DISTINCT state FROM holds').fetchall()==[('REMOTE_UNKNOWN',)]
    assert s['terminal_status']=='CLOSED_INCOMPLETE'

@pytest.mark.asyncio
async def test_terminal_requires_independent_fixture_witness(protected):
    f=protected;f.service.terminal_reader=lambda p:dict(terminal=False,association=p);f.opened()
    with pytest.raises(Refused):await f.turn()
    assert len(f.calls)==1 and f.journal.read()['pending'] is not None

@pytest.mark.parametrize('phase',['before_commit','after_commit'])
def test_successor_or_permit_commit_ack_crash(protected,phase):
    f=protected;f.opened();f.arm();s=f.high.read()
    p=f.store.db.execute('SELECT nonce FROM permits').fetchone()[0]
    def crash(point):
        if point==phase:raise RuntimeError('dummy crash')
    f.journal.fault=crash
    with pytest.raises(Refused):f.high._call('CONSUME',permit=p)
    f.journal.fault=lambda _:None
    assert len(f.journal.read()['accepted'])==(phase=='after_commit')
    if phase=='after_commit':
        f.high.read()
        with pytest.raises(Refused):f.high._call('CONSUME',permit=p)

@pytest.mark.asyncio
async def test_controller_and_whole_service_rollback_detected(protected):
    f=protected
    import sqlite3
    backup=sqlite3.connect(':memory:');f.store.db.backup(backup)
    f.opened();await f.turn()
    backup.backup(f.store.db);backup.close()
    with pytest.raises(Refused):f.high.check(f.store)
    assert len(f.journal.read()['accepted'])==1


def test_process_pin_is_kernel_derived_and_stale_refuses(protected):
    f=protected;client=UnixAuthorityConnection(f.socket_dir/'service',authority_pin=dataclasses.replace(f.pin,start='stale'))
    with pytest.raises(Refused):client.call('READ',{})
    f.servers[1].pin=dataclasses.replace(f.pin,uid=f.pin.uid+1)
    with pytest.raises(Refused):f.high.read()


def packet(f,raw,parts=None):
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
        conn.settimeout(2);conn.connect(str(f.socket_dir/'service'))
        if parts:
            for part in parts:conn.sendall(part)
        else:conn.sendall(struct.pack('!I',len(raw))+raw)
        n=struct.unpack('!I',conn.recv(4))[0];body=b''
        while len(body)<n:body+=conn.recv(n-len(body))
        return strict_json(body)

@pytest.mark.parametrize('raw',[b'{',b'{"version":1,"version":1}',canonical(dict(version=2,operation='READ',arguments={})),canonical(dict(version=1,operation='EXEC',arguments={})),canonical(dict(version=1,operation='READ',arguments={'uid':0})),canonical(dict(version=True,operation='READ',arguments={})),b'x'*(MAX_FRAME+1)])
def test_wire_schema_refusals(protected,raw):
    assert packet(protected,raw)['accepted'] is False


def test_partial_frame_and_concurrent_clients(protected):
    f=protected;raw=canonical(dict(version=1,operation='READ',arguments={}));wire=struct.pack('!I',len(raw))+raw
    assert packet(f,raw,parts=[bytes([c]) for c in wire])['accepted'] is True
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(lambda _:f.high.connection.call('READ',{}),range(12)))
    assert all(r['accepted']==[] for r in results)


def test_trickle_and_broken_pipe_do_not_hold_listener(protected):
    f=protected
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
        conn.connect(str(f.socket_dir/'service'));conn.sendall(b'\x00');time.sleep(0.6)
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
        conn.connect(str(f.socket_dir/'service'));raw=canonical(dict(version=1,operation='READ',arguments={}));conn.sendall(struct.pack('!I',len(raw))+raw)
    assert f.high.read()['accepted']==[]


def test_descriptor_injection_refused(protected):
    import array
    f=protected;fd=os.open('/dev/null',os.O_RDONLY)
    try:
        with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as conn:
            conn.connect(str(f.socket_dir/'service'));raw=canonical(dict(version=1,operation='READ',arguments={}))
            conn.sendmsg([struct.pack('!I',len(raw))+raw],[(socket.SOL_SOCKET,socket.SCM_RIGHTS,array.array('i',[fd]))])
            n=struct.unpack('!I',conn.recv(4))[0];assert strict_json(conn.recv(n))['accepted'] is False
    finally:os.close(fd)


def test_missing_authority_never_reinitialized(protected):
    f=protected;f.journal.path.rename(f.journal.path.with_suffix('.saved'))
    with pytest.raises(Refused):f.high.read()
    assert not f.journal.path.exists()


def test_socket_path_replacement_refuses(protected):
    f=protected;p=f.socket_dir/'service';p.unlink();p.write_text('dummy replacement');p.chmod(0o660)
    with pytest.raises(Refused):f.high.read()
    p.unlink()

@pytest.mark.asyncio
async def test_protected_ws_handshake_and_delivery(protected):
    from tests.execution.v3_integration_test import test_fastapi_ws_actual_handshake_reply
    await test_fastapi_ws_actual_handshake_reply(protected)

@pytest.mark.parametrize('message',['run bash','delete everything','remember yesterday','design a system','take a screenshot','weather today'])
@pytest.mark.asyncio
async def test_protected_rules_never_dispatch(protected,message):
    f=protected;f.opened()
    with pytest.raises(Refused):await f.turn(message=message)
    assert not f.calls and len(f.journal.read()['accepted'])==1

@pytest.mark.parametrize('change',[{'confidence':0.2},{'intent':'use_tool'},{'suggested_tool':'shell'},{'extra':'unexpected'}])
@pytest.mark.asyncio
async def test_protected_classifier_no_fallback(protected,change):
    f=protected;f.router_result.update(change);f.opened()
    with pytest.raises(Refused):await f.turn()
    assert len(f.calls)==1 and len(f.journal.read()['sends'])==1


def test_protected_open_replay_after_controller_rollback(protected):
    import sqlite3
    f=protected;copy=sqlite3.connect(':memory:');f.store.db.backup(copy)
    raw,sig=f.control('OPEN_HOLD');copy.backup(f.store.db);copy.close();f.runtime.state='CLOSED_INITIAL'
    with pytest.raises(Refused):f.runtime.control(raw,sig,(os.getuid(),os.getpid()),'OPEN_HOLD')
    with pytest.raises(Refused):f.high.check(f.store)


def test_mandatory_protected_factory_and_memory(protected):
    f=protected;f.runtime.acceptance_guard=f.old_high
    with pytest.raises(Refused,match='PROTECTED_GRAPH'):build_protected_isolated_app(f.runtime,api_token=b'DUMMY',allowed_origins=set(),qualification='OFFLINE_EVALUATION_ONLY')
    f.runtime.acceptance_guard=f.high
    f.runtime.legacy_policy=dataclasses.replace(f.runtime.legacy_policy,memory_snapshot='')
    with pytest.raises(Refused,match='MEMORY'):build_protected_isolated_app(f.runtime,api_token=b'DUMMY',allowed_origins=set(),qualification='OFFLINE_EVALUATION_ONLY')

@pytest.mark.parametrize('kind',['CLAIM','ACCEPT','BIND','SEND','SETTLE','CHECKPOINT'])
@pytest.mark.parametrize('boundary',['before_commit','after_commit'])
@pytest.mark.asyncio
async def test_runtime_durable_boundary_failure(protected,kind,boundary):
    f=protected;f.opened();triggered=[]
    def fault(point):
        if point==boundary and f.journal.db.execute('SELECT kind FROM events ORDER BY seq DESC LIMIT 1').fetchone()==(kind,):
            triggered.append(kind);raise RuntimeError('DISPOSABLE_FAULT')
    f.journal.fault=fault
    with pytest.raises(Refused):await f.turn()
    f.journal.fault=lambda _:None
    assert triggered
    s=f.journal.read()
    assert len(s['accepted'])==(0 if kind=='CLAIM' or kind=='ACCEPT' and boundary=='before_commit' else 1)
    assert f.runtime.state!='ARMED_ONE' or kind=='CLAIM'
    calls=len(f.calls)
    with pytest.raises(Refused):await f.turn()
    assert len(f.calls)==calls
    if kind=='SEND' and boundary=='after_commit':assert s['pending'] is not None and not f.calls

@pytest.mark.parametrize('point',['possible_send_committed','provider_terminal_committed','receipt_append_before_join','receipt_joined'])
@pytest.mark.asyncio
async def test_controller_boundary_failure_cannot_refund(protected,point):
    f=protected;f.opened();triggered=[]
    def fault(p):
        if p==point:triggered.append(p);raise OSError('DISPOSABLE_FAULT')
    f.store.fault=fault
    with pytest.raises(Refused):await f.turn()
    f.store.fault=lambda _:None
    assert triggered and len(f.journal.read()['accepted'])==1 and f.store.count()==1
    with pytest.raises(Refused):f.arm()

@pytest.mark.parametrize('point',['checkpoint_before_publish','checkpoint_after_publish'])
@pytest.mark.asyncio
async def test_coordinated_publish_failure_holds(protected,point):
    f=protected;f.opened()
    def fault(p):
        if p==point:raise OSError('DISPOSABLE_FAULT')
    f.writer.fault=fault
    with pytest.raises(Refused):await f.turn()
    assert len(f.journal.read()['accepted'])==1 and f.journal.read()['checkpoint'] is None


def test_concurrent_operator_permits_exactly_one(protected):
    from concurrent.futures import ThreadPoolExecutor
    f=protected;f.opened();_,sid=f.runtime.new_session('REST')
    packets=[f.approval('AUTHORIZE_ONE',dict(transport='REST',session=sid,request_commitment=f.runtime.commitment(ORIGINAL_INPUTS[0]))) for _ in range(2)]
    def submit(packet):
        try:f.operator.submit(*packet);return True
        except Refused:return False
    with ThreadPoolExecutor(2) as pool:out=list(pool.map(submit,packets))
    assert sorted(out)==[False,True] and f.journal.read()['accepted']==[]


def test_concurrent_consumption_exactly_one(protected):
    from concurrent.futures import ThreadPoolExecutor
    f=protected;f.opened();f.arm();s=f.high.read();p=f.store.db.execute('SELECT nonce FROM permits').fetchone()[0]
    def consume(_):
        try:f.high.connection.call('CONSUME',dict(expected=token(s),permit=p));return True
        except Refused:return False
    with ThreadPoolExecutor(2) as pool:out=list(pool.map(consume,range(2)))
    assert sorted(out)==[False,True] and len(f.journal.read()['accepted'])==1


def test_restart_authority_preserves_commands(protected):
    f=protected;raw,sig=f.control('OPEN_HOLD');previous=f.journal.read();old=f.journal
    old.close()
    f.journal=RuntimeJournal(old.root,owner_uid=os.getuid(),service_uid=os.getuid(),authority=f.authority,predecessor_reader=lambda:f.proof,identity_reader=f.bind.as_dict,provider_resources=old.provider_resources)
    f.service.journal=f.journal
    assert f.high.read()==previous
    with pytest.raises(Refused):f.operator.submit(raw,sig)


def test_invocation_drift_refuses_restart(protected):
    f=protected;f.journal.identity_reader=lambda:dict(f.bind.as_dict(),invocation='new-unapproved')
    with pytest.raises(Refused):f.high.read()
    assert not f.calls


def test_protected_root_corruption_refuses(protected):
    f=protected;f.journal.db.execute('PRAGMA user_version=99')
    with pytest.raises(Refused):f.high.read()


def test_no_unprotected_send_association(protected):
    f=protected;f.opened();tok=f.arm();session=f.runtime.sessions[tok]
    f.high.before_accept(f.store,'REST',session.id,f.runtime.commitment(ORIGINAL_INPUTS[0]));f.store.accept('REST',session.id,f.runtime.commitment(ORIGINAL_INPUTS[0]),now=100);f.high.after_accept(f.store)
    with pytest.raises(Refused):f.high._call('SEND',ordinal=1,role='legacy_router',request_digest='b'*64)
    assert f.journal.read()['pending'] is None

@pytest.mark.asyncio
async def test_signed_stop_while_unknown_never_settles(protected):
    f=protected;f.opened();f.block='gemma3:4b';task=asyncio.create_task(f.turn())
    await asyncio.wait_for(f.entered.wait(),3);f.control('TERMINAL_STOP')
    with pytest.raises(Refused):await task
    assert f.journal.read()['pending'] is not None and f.journal.read()['terminal_status']=='CLOSED_INCOMPLETE'


def test_nonreading_client_and_shutdown_during_partial_request(protected):
    f=protected
    peers=[]
    try:
        for _ in range(3):
            c=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM);c.connect(str(f.socket_dir/'service'));c.sendall(b'\x00');peers.append(c)
        started=time.monotonic();f.servers[1].close()
        assert time.monotonic()-started<1.5
        with pytest.raises(Refused):f.high.read()
    finally:
        for c in peers:c.close()

@pytest.mark.parametrize('kind',['source','config','process','symlink','hardlink'])
def test_fixed_release_identity_reader(protected,tmp_path,kind):
    from candidate_v3.runtime_authority import ReleaseIdentityReader
    from candidate_v3.contracts import Bindings
    f=protected;root=tmp_path/'release';root.mkdir(mode=0o700);source=root/'module.py';source.write_text('# disposable\n');source.chmod(0o600)
    config=root/'config.json';config.write_text('{}');config.chmod(0o600)
    inv={'module.py':digest(source.read_bytes())};cfg=digest(config.read_bytes())
    b=dataclasses.replace(f.bind,source=digest(canonical(inv)),config=cfg,pid=str(f.pin.pid),start=f.pin.start,boot=f.pin.boot)
    read=ReleaseIdentityReader(root,inv,config,cfg,b,f.pin,owner_uid=os.getuid());assert read()==b.as_dict()
    if kind=='source':source.write_text('# changed')
    elif kind=='config':config.write_text('{"changed":true}')
    elif kind=='process':read.pin=dataclasses.replace(f.pin,start='old')
    elif kind=='symlink':source.unlink();source.symlink_to(config)
    else:os.link(source,root/'another.py')
    with pytest.raises(Refused):read()

@pytest.mark.parametrize('verb',['CONSUME','BIND','SEND','SETTLE'])
@pytest.mark.parametrize('boundary',['before_commit','after_commit'])
def test_runtime_journal_real_process_crash(protected,verb,boundary):
    import subprocess
    f=protected;f.opened();tok=f.arm();session=f.runtime.sessions[tok];commitment=f.runtime.commitment(ORIGINAL_INPUTS[0])
    permit=f.store.db.execute('SELECT nonce FROM permits').fetchone()[0]
    if verb!='CONSUME':
        f.high.before_accept(f.store,'REST',session.id,commitment);aid=f.store.accept('REST',session.id,commitment,now=100)
    if verb in ('SEND','SETTLE'):
        f.high.after_accept(f.store);f.store.begin(aid,'LEGACY_ROUTER',f.router.resource,'b'*64)
    if verb=='SETTLE':f.high.possible_send(f.store,aid,'LEGACY_ROUTER',f.router,'b'*64)
    state=f.journal.read();expected=token(state)
    pub=f.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    actions={
        'CONSUME':f"j.consume(peer=peer,expected=expected,permit={permit!r},snapshot_reader=reader.check)",
        'BIND':"j.bind(peer=peer,expected=expected,snapshot_reader=reader.check)",
        'SEND':"j.possible_send(peer=peer,expected=expected,ordinal=1,role='legacy_router',request_digest='b'*64)",
        'SETTLE':f"j.settle(peer=peer,expected=expected,terminal_reader=lambda:dict(terminal=True,association={state['pending']!r}))"}
    script=f'''import os,sys
sys.path.append('/usr/lib/python3/dist-packages')
from candidate_v3.runtime_authority import *
from candidate_v3.contracts import Bindings
from candidate_v3.authority import Authority
from candidate_v3.protected_authority import Ed25519Verifier
b=Bindings(**{f.bind.as_dict()!r})
a=Authority(b,Ed25519Verifier({pub!r},operator_id='dummy-human'),clock=lambda:100.,operator_id='dummy-human',peer_uid=os.getuid())
def fault(point):
 if point=={boundary!r}:os._exit(77)
j=RuntimeJournal({str(f.journal.root)!r},owner_uid=os.getuid(),service_uid=os.getuid(),authority=a,predecessor_reader=lambda:None,identity_reader=b.as_dict,provider_resources={f.journal.provider_resources!r},fault=fault)
reader=ControllerReader({str(f.store.root)!r},{str(f.writer.root)!r},service_uid=os.getuid())
peer=(os.getuid(),os.getpid());expected={expected!r}
{actions[verb]}
'''
    result=subprocess.run([sys.executable,'-c',script],capture_output=True)
    assert result.returncode==77,result.stderr.decode()
    new=f.journal.read();assert new['seq']==state['seq']+(boundary=='after_commit')
    if verb=='CONSUME':assert len(new['accepted'])==(boundary=='after_commit')
    if verb=='SEND':assert (new['pending'] is not None)==(boundary=='after_commit')
    if verb=='SETTLE':assert (new['pending'] is None)==(boundary=='after_commit')


def test_missing_authority_stop_is_incomplete(protected):
    f=protected;f.servers[1].close();f.runtime.stop('OPERATOR_STOP')
    assert f.runtime.state==f.store.terminal()=='CLOSED_INCOMPLETE'


def test_nonreading_complete_request_bounded_write(protected):
    f=protected;original=f.service.dispatch
    f.service.dispatch=lambda *args:{'large':'x'*60000}
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as c:
        c.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,1024);c.connect(str(f.socket_dir/'service'))
        raw=canonical(dict(version=1,operation='READ',arguments={}));c.sendall(struct.pack('!I',len(raw))+raw)
        time.sleep(0.65)
        with f.servers[1].lock:assert not f.servers[1].workers
    f.service.dispatch=original
    assert f.high.read()['accepted']==[]

@pytest.mark.parametrize('attack',['symlink','hardlink','oversize','digest','atime','fifo'])
def test_authority_snapshot_reader_file_boundary(tmp_path,attack,monkeypatch):
    import sqlite3
    from candidate_v3.storage import read_snapshot_db
    p=tmp_path/'db';db=sqlite3.connect(p);db.execute('CREATE TABLE fixture(value)');db.commit();db.close();p.chmod(0o600)
    sha=digest(p.read_bytes())
    if attack=='symlink':p.rename(tmp_path/'target');p.symlink_to(tmp_path/'target')
    elif attack=='hardlink':os.link(p,tmp_path/'other')
    elif attack=='oversize':
        with p.open('r+b') as out:out.truncate(8*1024*1024+1)
    elif attack=='digest':sha='b'*64
    elif attack=='fifo':p.unlink();os.mkfifo(p,0o600)
    else:
        from types import SimpleNamespace
        real=os.fstat;calls=[]
        def fstat(fd):
            original=real(fd);calls.append(True)
            values={key:getattr(original,key) for key in dir(original) if key.startswith('st_')};values['st_atime']=len(calls)
            return SimpleNamespace(**values)
        monkeypatch.setattr(os,'fstat',fstat)
        db=read_snapshot_db(p,owner_uid=os.getuid(),expected_digest=sha);db.close();assert len(calls)==2;return
    with pytest.raises((Refused,OSError)):read_snapshot_db(p,owner_uid=os.getuid(),expected_digest=sha)


def test_disposable_runner_refuses_unapproved_current_uid(tmp_path):
    import importlib.util
    p=Path(__file__).parents[3]/'disposable/qualify_multi_uid.py'
    spec=importlib.util.spec_from_file_location('future_disposable',p);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    # This test never grants root or creates users; it verifies the current boundary.
    assert os.geteuid()!=0
    with pytest.raises(RuntimeError,match='OPERATOR_PROVISIONED_ROOT_RUN_REQUIRED'):module.main()

@pytest.mark.asyncio
async def test_replace_all_service_writable_files_keeps_protected_burn(protected,tmp_path):
    import shutil
    from candidate_v3.storage import Store
    from candidate_v3.domain_ledger import DomainLedger
    from candidate_v3.evidence import EvidenceBridge
    f=protected;old=tmp_path/'old-service';old.mkdir(mode=0o700)
    names=['state','backups','domains','evidence','coordinated','highwater',*[f'd06-{i}' for i in range(4)],'lineage-reservation.json']
    for name in names:
        src=tmp_path/name;dest=old/name
        if src.is_dir():shutil.copytree(src,dest)
        else:shutil.copy2(src,dest)
    f.opened();await f.turn();before=f.journal.read()
    f.store.close();f.domains.close();f.evidence.close();f.old_high.close()
    for name in names:
        src=old/name;dest=tmp_path/name
        if src.is_dir():shutil.rmtree(dest);shutil.copytree(src,dest)
        else:shutil.copy2(src,dest)
    f.store=Store(tmp_path/'state');f.domains=DomainLedger(tmp_path/'domains');f.evidence=EvidenceBridge(tmp_path/'evidence')
    f.runtime.store=f.store;f.runtime.provider.store=f.store
    assert f.store.count()==0
    with pytest.raises(Refused):f.high.check(f.store)
    with pytest.raises(Refused):build_protected_isolated_app(f.runtime,api_token=b'DUMMY',allowed_origins=set(),qualification='OFFLINE_EVALUATION_ONLY')
    assert f.journal.read()==before and len(before['accepted'])==1

@pytest.mark.asyncio
async def test_old_coordinated_backup_cannot_authorize_progress(protected):
    f=protected;old=f.writer.last;f.opened();await f.turn();current=f.high.read()
    with pytest.raises(Refused):f.high.connection.call('CHECKPOINT',dict(expected=token(current),bundle=old.name))
    assert f.journal.read()==current


def test_socket_directory_write_permission_rejected(protected):
    f=protected;f.socket_dir.chmod(0o770)
    try:
        with pytest.raises(Refused):f.high.read()
    finally:f.socket_dir.chmod(0o700)


def test_explicit_owner_applies_only_remote_approved_commands(protected):
    f=protected
    with pytest.raises(Refused):f.runtime.apply_protected_command(uuid.uuid4().hex)
    raw,sig=f.approval('OPEN_HOLD');f.operator.submit(raw,sig)
    assert f.runtime.state=='CLOSED_INITIAL'  # no automatic opening on approval
    f.runtime.apply_protected_command(strict_json(raw)['nonce'])
    assert f.runtime.state=='OPEN_HOLD'
    with pytest.raises(Refused):f.runtime.apply_protected_command(strict_json(raw)['nonce'])
    assert not f.calls
