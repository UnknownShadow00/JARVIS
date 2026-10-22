"""Offline Gate6E: all responses below are explicit synthetic transport fixtures.
They are not predictions of classifier output or approved experimental bindings.
"""
import asyncio,dataclasses,hashlib,hmac,json,os,socket,struct,threading,time,uuid
from pathlib import Path
import pytest,httpx
from candidate_v3.contracts import *
from candidate_v3.legacy import RulesFirstL1
from candidate_v3.source_legacy import *
from candidate_v3.transport import NativeTransport
from candidate_v3.ownership import OwnedProvider,OwnershipBinding
from candidate_v3.domain_ledger import DomainLedger
from candidate_v3.topology import HostAttestation,qualify_topology
from candidate_v3.lineage import HighWater,PredecessorProof
from tests.execution.v3_successor_support import fresh_fixture_proof,reserve_fixture
from candidate_v3.evidence import EvidenceBridge
from candidate_v3.checkpoints import CheckpointWriter,validate_coordinated,restore_for_review
from candidate_v3.application import build_isolated_app
from candidate_v3.local_control import LocalControl
from candidate_v3.observation import CanonicalObserver
from candidate_v3.runtime import ORIGINAL_INPUTS
from app.brain.model_ownership import ModelOwnershipCoordinatorV1,ModelResourceKeyV1
from app.brain.prompts import P7_SHADOW_PROMPT_V1
from app.execution.shadow_provider_ollama import RESOURCE,PROFILE_ID
from app.execution.permissions import ApprovalMode
from app.execution.registry_metadata import snapshot_registry_metadata
from tests.execution.v3_candidate_test import Fixture,Sink,KEY

class BytesStream(httpx.AsyncByteStream):
    def __init__(self,chunks):self.chunks=chunks
    async def __aiter__(self):
        for chunk in self.chunks:
            if isinstance(chunk,BaseException):raise chunk
            yield chunk

class Integrated(Fixture):
    def __init__(self,base,predecessor_proof=None):
        proof=fresh_fixture_proof(predecessor_proof or PredecessorProof('predecessor','a'*64,0,'b'*64))
        pred=dict(epoch=proof.epoch,status='CLOSED_COMPLETE',accepted=0,complete=True,unknown=False,retirement='EXPLICIT_ZERO_USE_RETIREMENT',archive=proof.archive_digest)
        super().__init__(base,predecessor=pred)
        self.calls=[];self.block=None;self.entered=asyncio.Event();self.router_result={'intent':'respond','confidence':0.9,'suggested_tool':'','reasoning':'Synthetic fixture classification.'}
        endpoint='http://192.0.2.10:11434'
        self.router=StepContract(Resource(endpoint,'gemma3:4b','fixture-router-v1'),Limits(4096,64,16384,16384,20,60),ROUTER_PROMPT,'OFFLINE_ROUTER',(('temperature',0.1),))
        self.trivial=StepContract(Resource(endpoint,'gemma3:4b','fixture-trivial-v1'),Limits(4096,80,16384,16384,180,60),RESPONDER_PROMPT,'OFFLINE_RESPONDER')
        self.normal=StepContract(Resource(endpoint,'qwen3-nothink','fixture-normal-v1'),Limits(8192,150,16384,16384,180,60),RESPONDER_PROMPT,'OFFLINE_RESPONDER')
        self.granite=StepContract(Resource(RESOURCE.endpoint,RESOURCE.model,PROFILE_ID),Limits(64000,128,16384,16384,180,60),P7_SHADOW_PROMPT_V1,'CANONICAL_OFFLINE')
        contracts=(self.router,self.trivial,self.normal,self.granite)
        async def handler(req):
            v=strict_json(req.content);self.calls.append((str(req.url),v));self.entered.set()
            if self.block==v['model']:await asyncio.Event().wait()
            text=canonical(self.router_result).decode() if v['messages'][0]['content']==ROUTER_PROMPT else 'GRANITE_MUST_NOT_BE_VISIBLE' if v['model']==RESOURCE.model else '**Legacy fixture response, sir.**'
            raw=canonical({'model':v['model'],'done':True,'done_reason':'stop','message':{'role':'assistant','content':text}})
            return httpx.Response(200,headers={'content-type':'application/json','content-length':str(len(raw))},stream=BytesStream([raw[:10],raw[10:]]))
        self.native=NativeTransport(contracts,transport=httpx.MockTransport(handler));self.ownership=[]
        for i,c in enumerate(contracts):
            owner=ModelOwnershipCoordinatorV1(base/f'd06-{i}')
            owner.provision(ModelResourceKeyV1('ollama',c.resource.endpoint,c.resource.model),legacy_endpoints=('http://192.0.2.254:11434',))
            self.ownership.append(OwnershipBinding(c.resource,owner,('explicit-fixture-gpu-domain',)))
        for n in ('domains','highwater','evidence','coordinated'):(base/n).mkdir(mode=0o700)
        self.domains=DomainLedger(base/'domains',create=True);self.high=HighWater(base/'highwater',create=True)
        reserve_fixture(self.high,proof,self.bind.as_dict()) # explicitly synthetic signed authority
        self.evidence=EvidenceBridge(base/'evidence',create=True)
        self.writer=CheckpointWriter(base/'coordinated',evidence=self.evidence,domains=self.domains,highwater=self.high,ownership=self.ownership)
        r=self.runtime;r.legacy_policy=RulesFirstL1(self.router,{'trivial':self.trivial,'normal':self.normal},'gemma3:4b','qwen3-nothink',0.75,'')
        r.granite=self.granite;r.observer=CanonicalObserver(snapshot_registry_metadata(),ApprovalMode.BALANCED)
        # Gate6F: the isolated graph requires an attested topology. These attestations are
        # explicitly OFFLINE_FIXTURE values, never evidence about the real AI host.
        self.attestations=(HostAttestation(endpoint,'fixture-legacy-host','fixture-legacy-gpu','fixture-legacy-ollama','OFFLINE_FIXTURE'),
                           HostAttestation(RESOURCE.endpoint,'fixture-ai-host','fixture-ai-gpu','fixture-ai-ollama','OFFLINE_FIXTURE'))
        self.topology=qualify_topology((self.router.resource,self.trivial.resource,self.normal.resource),self.granite.resource,self.attestations)
        r.provider=OwnedProvider(self.native,self.store,self.ownership,domain_ledger=self.domains,topology=self.topology)
        r.acceptance_guard=self.high;r.evidence_bridge=self.evidence;r.checkpoint_writer=self.writer
        r.legacy=dataclasses.replace(r.legacy,delivery_deadline=1.0)
        r._checkpoint()
        self.app=build_isolated_app(r,api_token=b'DUMMY_API',allowed_origins={b'http://localhost:8000'},qualification='OFFLINE_EVALUATION_ONLY')
    def close(self):
        self.store.close();self.domains.close();self.high.close();self.evidence.close()

@pytest.fixture
def integrated(tmp_path):
    f=Integrated(tmp_path)
    yield f
    f.close()

@pytest.mark.asyncio
async def test_rules_first_integrated_four_turns(integrated):
    f=integrated;f.opened()
    for t,m in zip(('REST','REST','WS','WS'),ORIGINAL_INPUTS):
        _,sink=await f.turn(t,m)
        assert sink.messages[0]['reply']=='Legacy fixture response, sir.'
        assert 'GRANITE' not in str(sink.messages)
        validate_coordinated(f.writer.last,minimum_accepted=f.store.count())
    assert len(f.calls)==11
    assert [v['options']['num_predict'] for _,v in f.calls]==[64,80,128,150,128,64,150,128,64,150,128]
    assert f.store.count()==4 and f.evidence.validate()==4
    assert all(b.coordinator.snapshot().state is None for b in f.ownership)
    assert f.runtime.state=='CLOSED_COMPLETE'
    assert 'GRANITE' not in str([s.history for s in f.runtime.sessions.values()])

@pytest.mark.parametrize('message,intent', [('run bash','use_tool'),('delete everything','confirm_action'),('remember yesterday','retrieve_memory'),('design a system','deep_reasoning'),('take a screenshot','use_tool'),('weather today','use_tool')])
@pytest.mark.asyncio
async def test_rules_reject_before_any_model(integrated,message,intent):
    f=integrated;assert classify_rules(message).intent==intent;f.opened()
    with pytest.raises(Refused):await f.turn(message=message)
    assert not f.calls and f.store.count()==1 and f.store.terminal()=='CLOSED_INCOMPLETE'

@pytest.mark.parametrize('change',[{'confidence':True},{'confidence':0.2},{'suggested_tool':'shell'},{'intent':'use_tool'},{'reasoning':''},{'extra':'value'},{'confidence':1.1}])
@pytest.mark.asyncio
async def test_classifier_strict_no_fallback(integrated,change):
    f=integrated;f.router_result.update(change);f.opened()
    with pytest.raises(Refused):await f.turn()
    assert len(f.calls)==1 and f.store.count()==1

@pytest.mark.parametrize('text,tier,model,output,think',[(ORIGINAL_INPUTS[0],'trivial','gemma3:4b',80,False),(ORIGINAL_INPUTS[1],'normal','qwen3-nothink',150,False),(ORIGINAL_INPUTS[2],'normal','qwen3-nothink',150,False),(ORIGINAL_INPUTS[3],'normal','qwen3-nothink',150,False),('explain why stars form','deep','qwen3:14b',700,True)])
def test_exact_source_complexity(text,tier,model,output,think):
    d=ComplexityRouter('gemma3:4b','qwen3-nothink').decide(text)
    assert (d.tier,d.model,d.num_predict,d.think)==(tier,model,output,think)

@pytest.mark.asyncio
async def test_deep_branch_unapproved(integrated):
    f=integrated;f.opened()
    with pytest.raises(Refused):await f.turn(message='explain why stars form')
    assert f.calls==[]

async def asgi_call(app,scope,frames,*,on_send=None):
    queue=asyncio.Queue()
    for f in frames:queue.put_nowait(f)
    out=[]
    async def send(frame):
        out.append(frame)
        if on_send:await on_send(frame,queue)
    work=asyncio.create_task(app(scope,queue.get,send))
    return work,queue,out

def scope(kind,token=None,headers=()):
    return {'type':kind,'asgi':{'version':'3.0'},'http_version':'1.1','scheme':'http' if kind=='http' else 'ws','path':'/chat' if kind=='http' else '/ws','raw_path':b'/chat' if kind=='http' else b'/ws','root_path':'','query_string':b'','method':'POST','server':('offline',8000),'client':('offline',1),'headers':[(b'authorization',b'Bearer DUMMY_API'),*([(b'x-jarvis-continuation',token.encode())] if token else []),*headers]}

@pytest.mark.asyncio
async def test_actual_fastapi_rest_envelope(integrated):
    f=integrated;f.opened();token=f.arm()
    task,q,out=await asgi_call(f.app,scope('http',token),[{'type':'http.request','body':canonical({'message':ORIGINAL_INPUTS[0]}),'more_body':False}])
    await asyncio.wait_for(task,3)
    assert out[0]['status']==200 and (b'x-jarvis-continuation',token.encode()) in out[0]['headers']
    body=strict_json(out[1]['body']);assert set(body)=={'reply','intent','confidence','dry_run','active'}
    assert body['reply']=='Legacy fixture response, sir.' and f.evidence.validate()==1

@pytest.mark.parametrize('headers', [[],[(b'authorization',b'Bearer WRONG')],[(b'authorization',b'Bearer DUMMY_API'),(b'authorization',b'Bearer DUMMY_API')]])
@pytest.mark.asyncio
async def test_fastapi_auth_before_body(integrated,headers):
    f=integrated;s=scope('http');s['headers']=headers
    async def forbidden():raise AssertionError('body read before authentication')
    out=[]
    async def send(v):out.append(v)
    await f.app(s,forbidden,send)
    assert out[0]['status']==401 and not f.calls and f.store.count()==0

@pytest.mark.asyncio
async def test_ws_origin_before_accept(integrated):
    f=integrated;task,q,out=await asgi_call(f.app,scope('websocket',headers=[(b'origin',b'https://evil.invalid')]),[])
    await task
    assert out==[{'type':'websocket.close','code':1008}] and not f.calls

@pytest.mark.asyncio
async def test_disconnect_during_classifier_holds_d06(integrated):
    f=integrated;f.opened();token=f.arm();f.block='gemma3:4b'
    task,q,out=await asgi_call(f.app,scope('http',token),[{'type':'http.request','body':canonical({'message':ORIGINAL_INPUTS[0]})}])
    await asyncio.wait_for(f.entered.wait(),2);q.put_nowait({'type':'http.disconnect'});await asyncio.wait_for(task,2)
    assert f.store.count()==1 and not f.store.clean() and f.store.terminal()=='CLOSED_INCOMPLETE'
    assert f.domains.db.execute('SELECT DISTINCT state FROM holds').fetchall()==[('REMOTE_UNKNOWN',)]
    assert f.ownership[0].coordinator.snapshot().state is not None

@pytest.mark.asyncio
async def test_stop_granite_preserves_delivery(integrated):
    f=integrated;f.opened();f.block=RESOURCE.model
    task=asyncio.create_task(f.turn())
    async with asyncio.timeout(3):
        while len(f.calls)<3:await asyncio.sleep(0)
    f.runtime.stop('OPERATOR_STOP')
    with pytest.raises(Refused):await task
    assert f.store.db.execute('SELECT delivery FROM attempts').fetchone()==('LOCAL_SEND_COMPLETED',)
    assert f.evidence.db.execute('SELECT disposition FROM deliveries').fetchone()==('LOCAL_SEND_COMPLETED',)
    assert not f.store.clean() and len(f.calls)==3

@pytest.mark.parametrize('status,headers,chunks',[(302,{'content-type':'application/json'},[b'{}']),(200,{'content-type':'text/plain'},[b'{}']),(200,{'content-type':'application/json'},[b'x'*16385]),(200,{'content-type':'application/json','content-length':'100'},[b'{}']),(200,{'content-type':'application/json','content-length':'2','transfer-encoding':'chunked'},[b'{}']),(200,{'content-type':'application/json'},[b'{']), (200,{'content-type':'application/json'},[httpx.ReadError('PRIVATE')]),(200,{'content-type':'application/json','content-encoding':'gzip'},[b'{}'])])
@pytest.mark.asyncio
async def test_native_failures_hold_unknown(integrated,status,headers,chunks):
    f=integrated
    def handler(req):return httpx.Response(status,headers=headers,stream=BytesStream(chunks))
    f.native.transport=httpx.MockTransport(handler);f.opened()
    with pytest.raises(Refused,match='ATTEMPT_FAILED'):await f.turn()
    assert not f.store.clean() and f.domains.db.execute('SELECT count(*) FROM holds').fetchone()[0]>0

@pytest.mark.asyncio
async def test_cross_endpoint_same_domain_exclusion(integrated):
    f=integrated;f.domains.acquire('external-fixture',('explicit-fixture-gpu-domain',));f.opened()
    with pytest.raises(Refused):await f.turn()
    assert not f.calls

@pytest.mark.asyncio
async def test_highwater_reservation_crash_never_refunded(integrated):
    f=integrated;f.opened();token=f.arm();s=f.runtime.sessions[token]
    f.high.before_accept(f.store,'REST',s.id,f.runtime.commitment(ORIGINAL_INPUTS[0]))
    with pytest.raises(Refused):f.high.check(f.store)
    assert f.high.db.execute('SELECT count(*) FROM accepted').fetchone()==(1,)
    with pytest.raises(Refused):await f.runtime.request(transport='REST',token=token,message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink())
    assert f.calls==[]

def test_successor_duplicate_refused(integrated):
    f=integrated
    with pytest.raises(Refused):reserve_fixture(f.high,fresh_fixture_proof(PredecessorProof('predecessor','a'*64,0,'b'*64)),dict(f.bind.as_dict(),epoch='another'))

def test_afunix_kernel_peer_dummy_signer_and_replay(integrated):
    f=integrated;f.authority.peer_uid=os.getuid();control=LocalControl(f.runtime,operator_uid=os.getuid())
    raw,sig=f.approval('OPEN_HOLD');packet=canonical({'body':strict_json(raw),'signature':sig.hex()})
    def run():
        a,b=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
        try:
            # handle uses SQLite in creator thread; peer writes are prebuffered.
            b.sendall(struct.pack('!I',len(packet))+packet);control.handle(a)
            n=struct.unpack('!I',b.recv(4))[0];return strict_json(b.recv(n))
        finally:a.close();b.close()
    assert run()=={'accepted':True}
    assert run()['accepted'] is False
    assert f.store.count()==0

@pytest.mark.asyncio
async def test_checkpoint_stale_restore_refused(integrated,tmp_path):
    f=integrated;old=f.writer.last;f.opened();await f.turn()
    with pytest.raises(Refused):restore_for_review(old,tmp_path/'restored',minimum_accepted=1)
    assert not (tmp_path/'restored').exists()

@pytest.mark.asyncio
async def test_receipt_join_fault_retains_uncertainty(integrated):
    f=integrated;f.opened()
    def fail(point):
        if point=='d04_appended_before_join':raise OSError('SIMULATED_FAULT')
    f.evidence.fault=fail
    with pytest.raises(Refused):await f.turn()
    with pytest.raises(Refused):f.evidence.validate()
    assert f.evidence.db.execute('SELECT state FROM submissions').fetchone()==('COMMIT_UNCERTAIN',)
    assert f.store.count()==1 and f.store.terminal()=='CLOSED_INCOMPLETE'

@pytest.mark.asyncio
async def test_fastapi_ws_actual_handshake_reply(integrated):
    f=integrated;f.opened()
    await f.turn('REST',ORIGINAL_INPUTS[0]);await f.turn('REST',ORIGINAL_INPUTS[1]);token=f.arm('WS',ORIGINAL_INPUTS[2])
    task,q,out=await asgi_call(f.app,scope('websocket',headers=[(b'origin',b'http://localhost:8000')]),[
        {'type':'websocket.connect'}, {'type':'websocket.receive','text':canonical({'type':'jarvis.continuation','version':1,'token':token}).decode()},
        {'type':'websocket.receive','text':ORIGINAL_INPUTS[2]}])
    async with asyncio.timeout(3):
        while f.store.count()!=3 or f.runtime.busy:await asyncio.sleep(0)
    q.put_nowait({'type':'websocket.disconnect','code':1000});await asyncio.wait_for(task,2)
    replies=[strict_json(v['text']) for v in out if v['type']=='websocket.send']
    assert out[0]['type']=='websocket.accept' and len(replies)==1
    assert replies[0]['reply']=='Legacy fixture response, sir.' and replies[0]['type']=='reply'
    assert f.evidence.validate()==3

@pytest.mark.parametrize('frame',[{'type':'websocket.receive','bytes':b'bad'}, {'type':'websocket.receive','text':'{bad'}, {'type':'websocket.receive','text':'x','bytes':b'x'}, {'type':'other','text':'x'}])
@pytest.mark.asyncio
async def test_ws_malformed_no_acceptance(integrated,frame):
    f=integrated;task,q,out=await asgi_call(f.app,scope('websocket'),[{'type':'websocket.connect'},frame]);await task
    assert out[-1]=={'type':'websocket.close','code':1008} and f.store.count()==0 and not f.calls

@pytest.mark.parametrize('change',[{'model':'wrong'},{'done':False},{'done':1},{'message':{'role':'user','content':'x'}},{'error':'PRIVATE'}])
@pytest.mark.asyncio
async def test_native_terminal_correlation_failure(integrated,change):
    f=integrated
    def handler(req):
        v={'model':'gemma3:4b','done':True,'message':{'role':'assistant','content':'x'}};v.update(change)
        return httpx.Response(200,headers={'content-type':'application/json'},stream=BytesStream([canonical(v)]))
    f.native.transport=httpx.MockTransport(handler);f.opened()
    with pytest.raises(Refused):await f.turn()
    assert not f.store.clean()

@pytest.mark.parametrize('fault',[httpx.ConnectTimeout,httpx.WriteTimeout,httpx.ReadTimeout,httpx.PoolTimeout,httpx.RemoteProtocolError])
@pytest.mark.asyncio
async def test_transport_phase_exceptions_no_retry(integrated,fault):
    f=integrated;calls=[]
    def handler(req):calls.append(1);raise fault('PRIVATE_MUST_NOT_ESCAPE')
    f.native.transport=httpx.MockTransport(handler);f.opened()
    with pytest.raises(Refused,match='ATTEMPT_FAILED'):await f.turn()
    assert calls==[1] and not f.store.clean()

@pytest.mark.asyncio
async def test_unauthorized_endpoint_never_reaches_transport(integrated):
    f=integrated;c=f.router;body=canonical({'model':c.resource.model,'messages':[]})
    req=ProviderRequest('a','b',Resource('http://192.0.2.99:11434',c.resource.model,c.resource.profile),body,digest(body),time.monotonic()+1)
    with pytest.raises(Refused,match='TRANSPORT_RESOURCE'):await f.native.request(req)
    assert not f.calls

@pytest.mark.asyncio
async def test_same_endpoint_profile_cannot_bypass_domains(integrated):
    f=integrated;f.domains.acquire('other-operation',('endpoint:'+f.router.resource.endpoint,));f.opened()
    with pytest.raises(Refused):await f.turn()
    assert not f.calls

def test_competing_domain_writers(tmp_path):
    root=tmp_path/'domains';root.mkdir(mode=0o700);first=DomainLedger(root,create=True);second=DomainLedger(root);results=[]
    def acquire(owner,operation):
        try:owner.acquire(operation,('shared',));results.append('accepted')
        except Refused:results.append('refused')
    threads=[threading.Thread(target=acquire,args=(first,'one')),threading.Thread(target=acquire,args=(second,'two'))]
    try:
        for t in threads:t.start()
        for t in threads:t.join()
        assert sorted(results)==['accepted','refused']
    finally:first.close();second.close()

@pytest.mark.parametrize('point',['checkpoint_component_synced','checkpoint_before_publish','checkpoint_after_publish'])
@pytest.mark.asyncio
async def test_checkpoint_failure_never_grants_next_permit(integrated,point):
    f=integrated;f.opened();old=f.writer.last
    def fail(p):
        if p==point:raise OSError('DISPOSABLE_FILESYSTEM_FAULT')
    f.writer.fault=fail
    with pytest.raises(Refused):await f.turn()
    assert f.store.count()==1 and f.store.terminal()=='CLOSED_INCOMPLETE' and f.writer.last==old
    with pytest.raises(Refused):f.arm()

@pytest.mark.parametrize('member',['manifest.json','controller.sqlite3','domains.sqlite3','highwater.sqlite3','d04-d09.sqlite3'])
def test_coordinated_corruption_refused(integrated,member):
    f=integrated;p=f.writer.last/member;p.write_bytes(b'broken')
    with pytest.raises(Refused):validate_coordinated(f.writer.last,minimum_accepted=0)

@pytest.mark.parametrize('member',['manifest.json','controller.sqlite3','domains.sqlite3'])
def test_coordinated_symlink_refused(integrated,member,tmp_path):
    f=integrated;p=f.writer.last/member;target=tmp_path/'dummy';target.write_bytes(p.read_bytes());p.unlink();p.symlink_to(target)
    with pytest.raises(Refused):validate_coordinated(f.writer.last,minimum_accepted=0)

@pytest.mark.asyncio
async def test_coordinated_disk_full_keeps_accepted(integrated,monkeypatch):
    import candidate_v3.checkpoints as cp
    f=integrated;f.opened();original=cp.os.write
    def fail(fd,body):
        if b'"controller_checkpoint"' in body:raise OSError(28,'simulated disk full')
        return original(fd,body)
    monkeypatch.setattr(cp.os,'write',fail)
    with pytest.raises(Refused):await f.turn()
    assert f.store.count()==1 and f.store.terminal()=='CLOSED_INCOMPLETE'

@pytest.mark.asyncio
async def test_native_action_proposal_never_visible(integrated):
    f=integrated;original=f.native.transport
    async def handler(req):
        r=await original.handle_async_request(req)
        if strict_json(req.content)['messages'][0]['content']==RESPONDER_PROMPT:
            raw=canonical({'model':'gemma3:4b','done':True,'message':{'role':'assistant','content':'[ACTION:SHELL:bad]'}})
            return httpx.Response(200,headers={'content-type':'application/json'},stream=BytesStream([raw]))
        return r
    f.native.transport=httpx.MockTransport(handler);f.opened();sink=Sink()
    with pytest.raises(Refused):await f.turn(sink=sink)
    assert not sink.messages and f.store.count()==1 and f.store.clean()

@pytest.mark.parametrize('retired',[True,False])
def test_v2_archive_schema_validator(tmp_path,retired):
    from tests.execution.shadow_pilot_backup_test import isolated
    from app.execution import shadow_backup as backup
    from candidate_v3.lineage import validate_v2_archive
    controller,owner,data=isolated(tmp_path)
    try:
        if retired:
            controller._db.execute("INSERT INTO pilot_events(attempt,code) VALUES(NULL,'OPERATOR_STOP')")
            controller._db.execute("UPDATE epochs SET status='CLOSED_COMPLETE',input_complete=1")
        bundle=backup.create_bundle(controller,owner,data,tmp_path/'archive/one')
        m=backup.validate_bundle(bundle);epoch=m['associations']['epochs'][0][0]
        if retired:
            proof=validate_v2_archive(bundle,epoch=epoch,implementation_hashes=m['source']['implementation_sha256'])
            assert proof.accepted==0 and proof.epoch==epoch
        else:
            with pytest.raises(Refused):validate_v2_archive(bundle,epoch=epoch,implementation_hashes=m['source']['implementation_sha256'])
    finally:controller.close()

@pytest.mark.asyncio
async def test_final_checkpoint_after_zero_use_stop(integrated):
    f=integrated;result=await f.runtime.drain()
    assert result['terminal']=='CLOSED_COMPLETE' and result['final_checkpoint']
    m=validate_coordinated(f.writer.last,minimum_accepted=0)
    assert m['terminal']=='CLOSED_COMPLETE' and m['purpose']=='READY'
    with pytest.raises(Refused):f.opened()

@pytest.mark.asyncio
async def test_final_checkpoint_failure_is_incomplete(integrated):
    f=integrated
    def fail(point):raise OSError('SIMULATED_CHECKPOINT_FAILURE')
    f.writer.fault=fail;result=await f.runtime.drain()
    assert result['terminal']=='CLOSED_INCOMPLETE' and result['final_checkpoint'] is None
    assert f.high.db.execute('SELECT terminal FROM root').fetchone()==('CLOSED_INCOMPLETE',)

@pytest.mark.asyncio
async def test_final_checkpoint_unknown_is_forensic(integrated):
    f=integrated;f.opened();f.block='gemma3:4b';task=asyncio.create_task(f.turn());await f.entered.wait()
    f.runtime.stop('OPERATOR_STOP')
    with pytest.raises(Refused):await task
    result=await f.runtime.drain()
    assert result['terminal']=='CLOSED_INCOMPLETE' and result['final_checkpoint']
    m=validate_coordinated(f.writer.last,minimum_accepted=1)
    assert m['purpose']=='FORENSIC_INCOMPLETE'

@pytest.mark.parametrize('point',['reservation','checkpoint_before_publish','checkpoint_after_publish'])
def test_process_crash_highwater_and_checkpoint(tmp_path,point):
    import subprocess,sys,sqlite3
    root=tmp_path/'child';root.mkdir(mode=0o700)
    program='''import os,asyncio,sys
from pathlib import Path
from tests.execution.v3_integration_test import Integrated
from candidate_v3.runtime import ORIGINAL_INPUTS
f=Integrated(Path(sys.argv[1]));point=sys.argv[2];f.opened()
if point=='reservation':
 token=f.arm();s=f.runtime.sessions[token]
 f.high.before_accept(f.store,'REST',s.id,f.runtime.commitment(ORIGINAL_INPUTS[0]));os._exit(73)
def crash(p):
 if p==point:os._exit(73)
f.writer.fault=crash
asyncio.run(f.turn())
'''
    result=subprocess.run([sys.executable,'-c',program,str(root),point],timeout=15,capture_output=True)
    assert result.returncode==73,result.stderr.decode()[-1000:]
    high=HighWater(root/'highwater')
    from candidate_v3.storage import Store
    store=Store(root/'state')
    try:
        assert high.db.execute('SELECT count(*) FROM accepted').fetchone()==(1,)
        if point=='reservation':
            assert store.count()==0
            with pytest.raises(Refused):high.check(store)
        else:
            assert store.count()==1;high.check(store)
            published=[p for p in (root/'coordinated').iterdir() if not p.name.startswith('.')]
            assert len(published)==(2 if point=='checkpoint_after_publish' else 1)
            assert store.db.execute('SELECT delivery FROM attempts').fetchone()==('LOCAL_SEND_COMPLETED',)
    finally:store.close();high.close()

@pytest.mark.asyncio
async def test_joined_receipt_cannot_be_duplicated(integrated):
    f=integrated;f.opened();await f.turn()
    row=f.evidence.db.execute('SELECT attempt,step FROM submissions').fetchone()
    # Unique submission association fails before append, never creates another D04 row.
    before=(f.evidence.root/'observations.jsonl').read_bytes()
    observation=f.runtime.observer.observe(f.runtime.observer.capture('synthetic-session','fixture text',[],'REST'),canonical({'model':RESOURCE.model,'done':True,'done_reason':'stop','message':{'role':'assistant','content':'fixture'}}))
    with pytest.raises(Exception):f.evidence.commit(*row,observation)
    assert (f.evidence.root/'observations.jsonl').read_bytes()==before and f.evidence.validate()==1

def test_completed_domain_operation_cannot_replay(tmp_path):
    root=tmp_path/'domains';root.mkdir(mode=0o700);ledger=DomainLedger(root,create=True)
    try:
        ledger.acquire('same',('endpoint',));ledger.finish('same',known=True)
        with pytest.raises(Refused):ledger.acquire('same',('endpoint',))
        assert ledger.db.execute('SELECT * FROM holds').fetchall()==[]
    finally:ledger.close()

@pytest.mark.asyncio
async def test_borrowed_transport_reusable_and_explicitly_closed(integrated):
    f=integrated;transport=f.native.transport;closed=[]
    async def close():closed.append(1)
    transport.aclose=close;f.opened();await f.turn()
    assert not closed and len(f.calls)==3
    await f.native.aclose();assert closed==[1]

@pytest.mark.asyncio
async def test_stop_during_checkpoint_does_not_return_open_hold(integrated):
    f=integrated;f.opened()
    def stop(point):
        if point=='checkpoint_before_publish':f.runtime.stop('OPERATOR_STOP')
    f.writer.fault=stop
    with pytest.raises(Refused):await f.turn()
    assert f.runtime.state in ('CLOSED_COMPLETE','CLOSED_INCOMPLETE') and f.store.terminal()
    with pytest.raises(Refused):f.arm()

@pytest.mark.asyncio
async def test_native_direct_call_requires_actual_lease(integrated):
    f=integrated;c=f.router;body=b'{}'
    request=ProviderRequest('a'*32,'b'*32,c.resource,body,digest(body),time.monotonic()+1)
    with pytest.raises(Refused,match='TRANSPORT_OWNERSHIP_REQUIRED'):await f.native.request(request)
    assert not f.calls

@pytest.mark.parametrize('headers', [[(b'content-length',b'2'),(b'content-length',b'2')],[(b'transfer-encoding',b'chunked')],[(b'content-type',b'text/plain')],[(b'content-length',b'-1')]])
@pytest.mark.asyncio
async def test_asgi_smuggling_metadata_refused(integrated,headers):
    f=integrated;f.opened();token=f.arm()
    task,q,out=await asgi_call(f.app,scope('http',token,headers),[{'type':'http.request','body':b'{}'}]);await task
    assert out[0]['status']==400 and f.store.count()==0 and not f.calls

def test_competing_successor_writers(integrated):
    f=integrated;second=HighWater(f.high.root)
    try:
        with pytest.raises(Refused):reserve_fixture(second,fresh_fixture_proof(PredecessorProof('different-root','c'*64,0,'d'*64)),dict(f.bind.as_dict(),epoch='duplicate'))
        assert second.db.execute('SELECT successor FROM root').fetchall()==[('successor',)]
    finally:second.close()

def test_source_prompt_hashes_and_rule_equivalence():
    import ast,re,collections
    profiles=strict_json(Path('candidate_v3/source_profiles.json').read_bytes())
    for n,h in profiles['source_files'].items():assert digest((Path('app/brain')/n).read_bytes())==h
    assert digest(ROUTER_PROMPT.encode())==profiles['router_prompt'] and digest(RESPONDER_PROMPT.encode())==profiles['responder_prompt']
    tree=ast.parse(Path('app/brain/router.py').read_text());node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_classify_by_rules')
    namespace={'re':re,'RouterResult':collections.namedtuple('RouterResult','intent confidence suggested_tool reasoning')}
    exec(compile(ast.Module(body=[node],type_ignores=[]),'reviewed-rules','exec'),namespace)
    samples=(*ORIGINAL_INPUTS,'delete x','run bash','remember yesterday','weather tomorrow','open an app','what is time','design a system')
    for text in samples:
        a=classify_rules(text);b=namespace['_classify_by_rules'](None,text)
        assert (None if a is None else dataclasses.asdict(a))==(None if b is None else b._asdict())

@pytest.mark.asyncio
async def test_validated_v2_archive_consumed_by_integrated_graph(tmp_path):
    from tests.execution.shadow_pilot_backup_test import isolated
    from app.execution import shadow_backup as backup
    from candidate_v3.lineage import validate_v2_archive
    prior=tmp_path/'prior';prior.mkdir(mode=0o700);controller,owner,data=isolated(prior)
    try:
        controller._db.execute("INSERT INTO pilot_events(attempt,code) VALUES(NULL,'OPERATOR_STOP')")
        controller._db.execute("UPDATE epochs SET status='CLOSED_COMPLETE',input_complete=1")
        bundle=backup.create_bundle(controller,owner,data,prior/'archive/one');m=backup.validate_bundle(bundle)
        proof=validate_v2_archive(bundle,epoch=m['associations']['epochs'][0][0],implementation_hashes=m['source']['implementation_sha256'])
    finally:controller.close()
    new=tmp_path/'new';new.mkdir(mode=0o700);f=Integrated(new,predecessor_proof=proof)
    try:
        f.opened();await f.turn();assert f.store.count()==1
        assert f.high.db.execute('SELECT predecessor,archive FROM root').fetchone()==(proof.epoch,proof.archive_digest)
    finally:f.close()

def test_global_root_must_match_controller_predecessor(integrated):
    f=integrated;f.high.db.execute("UPDATE root SET archive=?",('c'*64,))
    with pytest.raises(Refused,match='HIGHWATER_PREDECESSOR_ASSOCIATION'):f.high.check(f.store)

@pytest.mark.parametrize('mutation',['state','marker','operations','lineage'])
def test_rehashed_incoherent_checkpoint_rejected(integrated,mutation):
    f=integrated;root=f.writer.last
    if mutation=='state':
        p=root/'d06-0-state.json';v=strict_json(p.read_bytes());v['current']={'bad':'shape'};p.write_bytes(canonical(v))
    elif mutation=='marker':
        p=root/'d06-0-ownership.managed';v=strict_json(p.read_bytes());v['scope_digest']='f'*64;p.write_bytes(canonical(v))
    elif mutation=='lineage':
        p=root/'lineage.json';v=strict_json(p.read_bytes());v['archive']='e'*64;p.write_bytes(canonical(v))
    else:
        import sqlite3
        p=root/'domains.sqlite3';db=sqlite3.connect(p);db.execute("INSERT INTO operations VALUES('orphan','KNOWN_TERMINAL')");db.commit();db.close()
    manifest=root/'manifest.json';m=strict_json(manifest.read_bytes());m['files'][p.name]=digest(p.read_bytes());manifest.write_bytes(canonical(m))
    with pytest.raises(Refused):validate_coordinated(root,minimum_accepted=0)

@pytest.mark.asyncio
async def test_drain_closes_local_transport_without_clearing_remote_unknown(integrated):
    f=integrated;closed=[]
    async def close():closed.append(True)
    f.native.transport.aclose=close
    f.opened();f.block='gemma3:4b';task=asyncio.create_task(f.turn());await f.entered.wait();f.runtime.stop('OPERATOR_STOP')
    with pytest.raises(Refused):await task
    result=await f.runtime.drain()
    assert closed==[True] and not result['ownership_clean'] and result['terminal']=='CLOSED_INCOMPLETE'
