"""Gate 6F offline release qualification.

Every provider response here is an explicitly named synthetic MockTransport
fixture; classifier outputs are fixture values, not predictions. No real Ollama,
credential, production path or network is used. Size/timing measurements are
written to $P7_OFFLINE_STAGE/g6f-artifacts for the sealed evidence bundle.
"""
import ast,asyncio,json,os,resource,shutil,socket,sqlite3,struct,subprocess,sys,threading,time,uuid
from pathlib import Path
import pytest,httpx
from candidate_v3.contracts import *
from candidate_v3.legacy import RulesFirstL1
from candidate_v3.source_legacy import ROUTER_PROMPT,RESPONDER_PROMPT,classify_rules,ComplexityRouter
from candidate_v3.source_memory import procedural_snapshot
from candidate_v3.topology import HostAttestation,qualify_topology,SHARED_RESIDENCY_APPROVAL
from candidate_v3.ownership import OwnedProvider
from candidate_v3.lineage import HighWater,PredecessorProof,validate_v2_archive
from candidate_v3.evidence import EvidenceBridge
from candidate_v3.domain_ledger import DomainLedger
from candidate_v3.storage import Store,checkpoint,verify_checkpoint
from candidate_v3.application import build_isolated_app
from candidate_v3.local_control import LocalControl
from candidate_v3 import local_control
from candidate_v3.runtime import ORIGINAL_INPUTS,Runtime
from app.execution.shadow_provider_ollama import RESOURCE,PROFILE_ID
from tests.execution.v3_integration_test import Integrated,BytesStream
from tests.execution.v3_candidate_test import Fixture,Sink,KEY
from tests.execution.v3_successor_support import fresh_fixture_proof,reserve_fixture

SKILLS_SHA256='3a61af6054795cad154b5de00e4185063d32e08e592aba315bc8ef1560e6d4a2'  # tracked skills.md == production copy
CAP=16384

def artifact(name,value):
    stage=os.environ.get('P7_OFFLINE_STAGE')
    if stage:
        out=Path(stage)/'g6f-artifacts';out.mkdir(mode=0o700,exist_ok=True)
        (out/name).write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')

def source_snapshot():
    return procedural_snapshot(Path('skills.md').read_bytes(),expected_sha256=SKILLS_SHA256)

def with_memory(f,snapshot):
    f.runtime.legacy_policy=RulesFirstL1(f.router,{'trivial':f.trivial,'normal':f.normal},'gemma3:4b','qwen3-nothink',0.75,snapshot)

def kind_of(v):
    if v['model']==RESOURCE.model:return 'GRANITE'
    return 'LEGACY_ROUTER' if v['messages'][0]['content']==ROUTER_PROMPT else 'LEGACY_RESPONDER'

def fail_model(f,model,status=500):
    """Synthetic failure for one model; still records the call it received."""
    original=f.native.transport.handler
    async def handler(req):
        v=strict_json(req.content)
        if v['model']==model:
            f.calls.append((str(req.url),v));return httpx.Response(status,headers={'content-type':'application/json'},content=b'{}')
        return await original(req)
    f.native.transport.handler=handler

@pytest.fixture
def integrated(tmp_path):
    f=Integrated(tmp_path)
    yield f
    f.close()

# ---------------------------------------------------------------- Part A: L1 source fidelity

def test_prompt_construction_matches_original_build_prompt():
    from app.brain import prompts,router
    from app.memory.procedural import ProceduralMemory
    assert RESPONDER_PROMPT==prompts.JARVIS_SYSTEM_PROMPT and ROUTER_PROMPT==router._SYSTEM_PROMPT
    snap=source_snapshot()
    assert snap==ProceduralMemory(Path('skills.md')).prompt_context() and snap
    f_router=StepContract(Resource('http://192.0.2.10:11434','gemma3:4b','fixture-router-v1'),Limits(4096,64,CAP,CAP,20,60),ROUTER_PROMPT,'OFFLINE_ROUTER',(('temperature',0.1),))
    normal=StepContract(Resource('http://192.0.2.10:11434','qwen3-nothink','fixture-normal-v1'),Limits(8192,150,CAP,CAP,180,60),RESPONDER_PROMPT,'OFFLINE_RESPONDER')
    trivial=StepContract(Resource('http://192.0.2.10:11434','gemma3:4b','fixture-trivial-v1'),Limits(4096,80,CAP,CAP,180,60),RESPONDER_PROMPT,'OFFLINE_RESPONDER')
    l1=RulesFirstL1(f_router,{'trivial':trivial,'normal':normal},'gemma3:4b','qwen3-nothink',0.75,snap)
    for m in ORIGINAL_INPUTS:
        assert l1.messages(normal,m)==prompts.build_prompt(m)  # exact original system+user, no prior turns

def test_memory_snapshot_is_pinned_and_never_truncated(tmp_path):
    raw=Path('skills.md').read_bytes()
    with pytest.raises(Refused,match='MEMORY_SOURCE_DIGEST'):procedural_snapshot(raw+b'\n- new live skill\n',expected_sha256=SKILLS_SHA256)
    big=('\n'.join('- '+'x'*900 for _ in range(12))).encode();import hashlib
    with pytest.raises(Refused,match='MEMORY_SNAPSHOT_LIMIT'):procedural_snapshot(big,expected_sha256=hashlib.sha256(big).hexdigest())

def test_original_lifespan_writes_operator_stop_on_any_shutdown():
    """Source proof for G6F-SEC-01: V2 cannot attribute OPERATOR_STOP to an operator."""
    tree=ast.parse(Path('app/server.py').read_text())
    life=next(n for n in ast.walk(tree) if isinstance(n,ast.AsyncFunctionDef) and n.name=='lifespan')
    calls=[n for n in ast.walk(life) if isinstance(n,ast.Call) and getattr(n.func,'attr','')=='stop_admissions']
    assert calls and all(not c.args and not c.keywords for c in calls)
    pilot=ast.parse(Path('app/execution/shadow_pilot.py').read_text())
    defaults={n.args.defaults[0].value for n in ast.walk(pilot) if isinstance(n,ast.FunctionDef) and n.name=='stop_admissions'}
    assert defaults=={'OPERATOR_STOP'}

@pytest.mark.asyncio
async def test_four_inputs_with_source_memory_fit_bounds_and_record_sizes(integrated):
    f=integrated;with_memory(f,source_snapshot());f.opened();sizes=[];timings=[]
    for t,m in zip(('REST','REST','WS','WS'),ORIGINAL_INPUTS):
        before=len(f.calls);rule=classify_rules(m)
        start=time.perf_counter();_,sink=await f.turn(t,m);elapsed=time.perf_counter()-start
        new=f.calls[before:]
        sizes.append({'input':ORIGINAL_INPUTS.index(m)+1,'transport':t,'rule_intent':None if rule is None else rule.intent,
            'operations':[{'kind':kind_of(v),'model':v['model'],'num_ctx':v['options']['num_ctx'],'num_predict':v['options']['num_predict'],
                           'keep_alive':v['keep_alive'],'request_bytes':len(canonical(v)),'history_messages':len(v['messages'])-2,'url_path':u.split('11434',1)[1]} for u,v in new]})
        timings.append(elapsed)
        assert sink.messages[0]['reply']=='Legacy fixture response, sir.' and 'GRANITE' not in json.dumps(sink.messages)
        assert [kind_of(v) for _,v in new]==(['LEGACY_RESPONDER','GRANITE'] if rule else ['LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE'])
    ops=[o for s in sizes for o in s['operations']]
    assert all(o['request_bytes']<=CAP for o in ops) and len(ops)==11
    assert {o['url_path'] for o in ops}=={'/api/chat'}  # no discovery, load, unload or ps call
    assert [s['rule_intent'] for s in sizes]==[None,'respond',None,None]
    assert [o['model'] for s in sizes for o in s['operations'] if o['kind']=='LEGACY_RESPONDER']==['gemma3:4b','qwen3-nothink','qwen3-nothink','qwen3-nothink']
    assert max(o['history_messages'] for o in ops if o['kind']=='GRANITE')==2 and max(o['history_messages'] for o in ops if o['kind']!='GRANITE')==0
    artifact('request-size-fit.json',{'cap_bytes':CAP,'memory_snapshot_bytes':len(source_snapshot().encode()),'turns':sizes,
        'max_by_kind':{k:max(o['request_bytes'] for o in ops if o['kind']==k) for k in ('LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE')},
        'offline_turn_seconds_including_checkpoint':timings,'qualification':'OFFLINE_FIXTURE_MOCK_TRANSPORT'})

@pytest.mark.asyncio
async def test_oversize_responder_request_refused_without_truncation(integrated):
    f=integrated;with_memory(f,source_snapshot());f.opened()
    message='Name one primary colour. '+'"'*7000  # JSON escaping doubles the quotes
    assert classify_rules(message) is None and ComplexityRouter('gemma3:4b','qwen3-nothink').decide(message).tier=='normal'
    with pytest.raises(Refused):await f.turn(message=message)
    assert [kind_of(v) for _,v in f.calls]==['LEGACY_ROUTER']           # router fit and ran
    assert f.store.db.execute('SELECT kind FROM steps').fetchall()==[('LEGACY_ROUTER',)]  # no responder possible-send
    assert f.store.count()==1 and f.store.terminal()=='CLOSED_INCOMPLETE'  # accepted attempt is burned, never refunded

def test_max_admissible_message_bytes_per_operation():
    snap=source_snapshot()
    def body(system,message,ctx,out,extra=None):
        return len(canonical({'model':'qwen3-nothink','messages':[{'role':'system','content':system},{'role':'user','content':message}],'stream':False,'think':False,'keep_alive':60,'options':{'num_ctx':ctx,'num_predict':out,**(extra or {})}}))
    result={}
    for name,system in (('router',ROUTER_PROMPT),('responder_with_memory',RESPONDER_PROMPT+'\n\n'+snap),('responder_without_memory',RESPONDER_PROMPT)):
        overhead=body(system,'',32768,150,{'temperature':0.1} if name=='router' else None)
        result[name]={'overhead_bytes':overhead,'ascii_message_headroom':CAP-overhead,'ingress_message_limit':8192,
                      'worst_case_escaped_headroom_bytes':(CAP-overhead)//6}
    assert all(v['ascii_message_headroom']>8192 for v in result.values())  # any 8 KiB plain message fits
    artifact('message-headroom.json',result)

# ---------------------------------------------------------------- Part A: provider operation accounting

@pytest.mark.parametrize('variant,message,expected',[
    ('rules_refusal','run bash',[]),
    ('classifier_refusal',ORIGINAL_INPUTS[0],['LEGACY_ROUTER']),
    ('responder_failure',ORIGINAL_INPUTS[1],['LEGACY_RESPONDER']),
    ('delivery_failure',ORIGINAL_INPUTS[0],['LEGACY_ROUTER','LEGACY_RESPONDER']),
    ('granite_failure',ORIGINAL_INPUTS[2],['LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE']),
    ('success_rule_path',ORIGINAL_INPUTS[1],['LEGACY_RESPONDER','GRANITE']),
    ('success_classifier_path',ORIGINAL_INPUTS[3],['LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE'])])
@pytest.mark.asyncio
async def test_operation_counts_decrease_truthfully(integrated,variant,message,expected):
    f=integrated;f.opened();sink=Sink('fail' if variant=='delivery_failure' else 'ok')
    if variant=='classifier_refusal':f.router_result['confidence']=0.2
    if variant=='responder_failure':fail_model(f,'qwen3-nothink')
    if variant=='granite_failure':fail_model(f,RESOURCE.model)
    if variant.startswith('success'):await f.turn(message=message,sink=sink)
    else:
        with pytest.raises(Refused):await f.turn(message=message,sink=sink)
    steps=f.store.db.execute('SELECT kind,model,state FROM steps ORDER BY rowid').fetchall()
    assert [kind_of(v) for _,v in f.calls]==expected==[s[0] for s in steps]   # one recorded possible-send per transmission
    assert [v['model'] for _,v in f.calls]==[s[1] for s in steps]
    assert f.store.count()==1                                                 # never refunded
    if not variant.startswith('success'):
        assert f.store.terminal()=='CLOSED_INCOMPLETE'
        with pytest.raises(Refused):f.arm('REST',ORIGINAL_INPUTS[1])           # no next permit after failure
    if variant=='granite_failure':
        assert f.store.db.execute('SELECT delivery FROM attempts').fetchone()==('LOCAL_SEND_COMPLETED',)
        assert steps[-1][2]=='REMOTE_UNKNOWN' and 'GRANITE' not in json.dumps(sink.messages)

@pytest.mark.asyncio
async def test_no_model_operation_without_accepted_attempt(integrated):
    f=integrated;f.opened()
    with pytest.raises(Refused):await f.runtime._generate(uuid.uuid4().hex,'LEGACY_RESPONDER',f.normal,[{'role':'user','content':'x'}])
    assert f.calls==[] and f.store.db.execute('SELECT count(*) FROM steps').fetchone()==(0,)

def test_conditional_time_envelope():
    """Arithmetic over proposed per-operation deadlines only; no hidden overall deadline."""
    router,responder,granite=20,180,180
    per_input={1:router+responder+granite,2:responder+granite,3:router+responder+granite,4:router+responder+granite}
    envelope={'per_input_provider_seconds':per_input,'provider_seconds_total':sum(per_input.values()),
        'provider_operations':{'LEGACY_ROUTER':3,'LEGACY_RESPONDER':4,'GRANITE':4,'total':11},'accepted_attempts':4,
        'excluded':'delivery deadline (unapproved), human permit latency, checkpoint cost (see request-size-fit timings)',
        'local_drain_seconds_max':30,'remote_completion_after_drain':'NOT GUARANTEED'}
    assert envelope['provider_seconds_total']==1500 and sum(envelope['provider_operations'][k] for k in ('LEGACY_ROUTER','LEGACY_RESPONDER','GRANITE'))==11
    artifact('time-envelope.json',envelope)

# ---------------------------------------------------------------- Part B: topology and D06

LEG=Resource('http://192.0.2.10:11434','gemma3:4b','fixture-router-v1')
LEG2=Resource('http://192.0.2.10:11434','qwen3-nothink','fixture-normal-v1')
GRA=Resource(RESOURCE.endpoint,RESOURCE.model,PROFILE_ID)

def att(endpoint,host,gpu,service,source='OFFLINE_FIXTURE'):return HostAttestation(endpoint,host,gpu,service,source)

def test_topology_a_separate_hosts():
    t=qualify_topology((LEG,LEG2),GRA,(att(LEG.endpoint,'h1','g1','s1'),att(GRA.endpoint,'h2','g2','s2')))
    assert t.kind=='A_SEPARATE_HOSTS' and t.source=='OFFLINE_FIXTURE'

@pytest.mark.parametrize('legacy_endpoint,host,gpu,service,kind',[
    ('http://192.168.0.200:11435','ai','gpu0','other-ollama','B_SAME_HOST_SEPARATE_SERVICES'),
    ('http://192.0.2.10:11434','other-host','gpu0','other-ollama','B_SAME_HOST_SEPARATE_SERVICES'),
    (RESOURCE.endpoint,'ai','gpu0','ai-ollama','C_SAME_SERVICE'),
    ('http://ai-alias.invalid:11434','ai','gpu0','ai-ollama','C_SAME_SERVICE')])
def test_topology_shared_requires_explicit_residency_approval(legacy_endpoint,host,gpu,service,kind):
    leg=Resource(legacy_endpoint,'gemma3:4b','fixture-router-v1');a=(att(legacy_endpoint,host,gpu,service),att(GRA.endpoint,'ai','gpu0','ai-ollama'))
    with pytest.raises(Refused,match='SHARED_RESOURCE_RESIDENCY_UNAPPROVED'):qualify_topology((leg,),GRA,a)
    assert qualify_topology((leg,),GRA,a,residency_approval=SHARED_RESIDENCY_APPROVAL).kind==kind

@pytest.mark.parametrize('attestations,code',[
    ((),'TOPOLOGY_UNVERIFIED'),
    ((att(GRA.endpoint,'ai','gpu0','ai-ollama'),),'TOPOLOGY_UNVERIFIED'),
    ((att(LEG.endpoint,'h1','g1','s1','HUMAN_ATTESTED'),att(GRA.endpoint,'h2','g2','s2')),'TOPOLOGY_MIXED_SOURCE'),
    ((att(LEG.endpoint,'h1','g1','s1'),att(LEG.endpoint,'h9','g1','s1'),att(GRA.endpoint,'h2','g2','s2')),'TOPOLOGY_CONFLICTING_ATTESTATION'),
    ((att(LEG.endpoint,'h1','g1','shared'),att(GRA.endpoint,'h2','g2','shared')),'TOPOLOGY_CONFLICTING_ATTESTATION')])
def test_topology_d_unverified_fails_closed(attestations,code):
    with pytest.raises(Refused,match=code):qualify_topology((LEG,LEG2),GRA,attestations)

def test_attestation_source_and_values_are_strict():
    for bad in [('http://x:1','h','g','s','GUESSED'),('http://x:1','h h','g','s','OFFLINE_FIXTURE'),('http://x:1/','h','g','s','OFFLINE_FIXTURE'),('http://x','h','g','s','OFFLINE_FIXTURE')]:
        with pytest.raises(Refused):HostAttestation(*bad)

def test_isolated_graph_requires_topology(integrated):
    f=integrated;f.runtime.provider=OwnedProvider(f.native,f.store,f.ownership,domain_ledger=f.domains)
    with pytest.raises(Refused,match='INCOMPLETE_ISOLATED_GRAPH'):build_isolated_app(f.runtime,api_token=b'DUMMY_API',allowed_origins=set(),qualification='OFFLINE_EVALUATION_ONLY')

@pytest.mark.asyncio
async def test_same_host_other_port_conflicts_through_attested_domain(integrated):
    """Topology B: an operation held on the AI host's other service blocks legacy before any possible-send."""
    f=integrated
    a=(att(f.router.resource.endpoint,'ai','gpu0','legacy-ollama'),att(RESOURCE.endpoint,'ai','gpu0','ai-ollama'))
    t=qualify_topology((f.router.resource,f.trivial.resource,f.normal.resource),f.granite.resource,a,residency_approval=SHARED_RESIDENCY_APPROVAL)
    f.runtime.provider=OwnedProvider(f.native,f.store,f.ownership,domain_ledger=f.domains,topology=t)
    f.domains.acquire('external-granite-window',('gpu:gpu0',))  # e.g. Granite residency/unknown on that GPU
    f.opened()
    with pytest.raises(Refused):await f.turn()
    assert f.calls==[] and f.store.db.execute('SELECT count(*) FROM steps').fetchone()==(0,)
    assert f.domains.db.execute("SELECT count(*) FROM operations WHERE state='REMOTE_UNKNOWN'").fetchone()==(0,)

@pytest.mark.asyncio
async def test_known_conflict_refuses_before_possible_send(integrated):
    f=integrated;f.domains.acquire('external-fixture',('explicit-fixture-gpu-domain',));f.opened()
    with pytest.raises(Refused):await f.turn()
    assert f.calls==[] and f.store.db.execute('SELECT count(*) FROM steps').fetchone()==(0,) and f.store.clean()

@pytest.mark.asyncio
async def test_remote_unknown_is_never_released_automatically(integrated):
    f=integrated;f.opened();fail_model(f,'gemma3:4b')
    with pytest.raises(Refused):await f.turn()
    assert f.domains.db.execute("SELECT DISTINCT state FROM holds").fetchall()==[('REMOTE_UNKNOWN',)]
    with pytest.raises(Refused):f.runtime.provider.precheck(f.normal.resource)
    with pytest.raises(Refused):f.runtime.provider.lifecycle('unload')
    result=await f.runtime.drain()
    assert result['ownership_clean'] is False and f.domains.db.execute('SELECT count(*) FROM holds').fetchone()[0]>0

# ---------------------------------------------------------------- Part C: operator authority and lineage

@pytest.mark.parametrize('verb',['OPEN_HOLD','AUTHORIZE_ONE','TERMINAL_STOP'])
@pytest.mark.asyncio
async def test_replayed_control_has_no_effect(tmp_path,verb):
    f=Fixture(tmp_path)
    try:
        if verb=='OPEN_HOLD':
            raw,sig=f.control('OPEN_HOLD')
        elif verb=='AUTHORIZE_ONE':
            f.opened();f.arm();await f.runtime.request(transport='REST',token=f.tokens['REST'][0],message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink())
            raw=None
        else:
            raw,sig=f.approval('TERMINAL_STOP');f.store.control(dict(strict_json(raw),_signed_digest=digest(raw),_verified_operator='dummy-human'))
        if raw is None:
            row=f.store.db.execute("SELECT nonce FROM control WHERE verb='AUTHORIZE_ONE'").fetchone()
            payload=dict(transport='REST',session=f.tokens['REST'][1],request_commitment=f.runtime.commitment(ORIGINAL_INPUTS[0]))
            raw,sig=f.approval('AUTHORIZE_ONE',payload,nonce=row[0])
        before=(f.runtime.state,f.runtime.stop_event.is_set(),f.store.db.execute('SELECT count(*) FROM control').fetchone())
        with pytest.raises(Refused,match='CONTROL_REPLAY|STALE_CHECKPOINT'):f.runtime.control(raw,sig,(0,99),verb)
        assert (f.runtime.state,f.runtime.stop_event.is_set(),f.store.db.execute('SELECT count(*) FROM control').fetchone())==before
    finally:f.store.close()

@pytest.mark.parametrize('field',['source','config','release','pid','invocation','epoch','boot','start','challenge'])
def test_signed_control_bound_to_exact_process(tmp_path,field):
    f=Fixture(tmp_path)
    try:
        raw,sig=f.approval('OPEN_HOLD',bindings=dict(f.bind.as_dict(),**{field:'stale-'+field}))
        with pytest.raises(Refused,match='CONTROL_BINDING'):f.runtime.control(raw,sig,(0,99),'OPEN_HOLD')
        assert f.runtime.state=='CLOSED_INITIAL'
    finally:f.store.close()

def test_restart_never_reopens_and_outstanding_permit_never_accepts(tmp_path):
    f=Fixture(tmp_path);f.opened();token=f.arm();root=f.store.root;f.store.close()
    store=Store(root)
    try:
        r=Runtime(store,f.bind,f.legacy,f.granite,f.authority,f.provider,f.back,commitment_key=b'DUMMY_REQUEST_COMMITMENT_KEY_123456',observer=f.runtime.observer,view_status=f.runtime.view_status,legacy_policy=f.runtime.legacy_policy)
        assert r.state=='CLOSED_RECOVERY_HOLD'
        with pytest.raises(Refused):asyncio.run(r.request(transport='REST',token=token,message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink()))
        assert store.count()==0 and f.provider.calls==[]
    finally:store.close()

@pytest.mark.asyncio
async def test_afunix_trickling_peer_is_cut_off(tmp_path,monkeypatch):
    f=Fixture(tmp_path);monkeypatch.setattr(local_control,'TOTAL_READ_SECONDS',0.4)
    left,right=socket.socketpair(socket.AF_UNIX,socket.SOCK_STREAM)
    def trickle():
        right.sendall(struct.pack('!I',200))
        for _ in range(20):
            try:right.sendall(b' ');time.sleep(0.05)
            except OSError:return
    t=threading.Thread(target=trickle);t.start()
    try:
        start=time.monotonic();LocalControl(f.runtime,operator_uid=os.getuid()).handle(left);elapsed=time.monotonic()-start
        n=struct.unpack('!I',right.recv(4))[0];reply=strict_json(right.recv(n))
        assert reply=={'accepted':False,'code':'CONTROL_REFUSED'} and elapsed<1.5 and f.runtime.state=='CLOSED_INITIAL'
    finally:
        left.close();right.close();t.join();f.store.close()

def test_v2_archive_proves_zero_use_only_and_successor_payload_acknowledges(tmp_path):
    from tests.execution.shadow_pilot_backup_test import isolated
    from app.execution import shadow_backup as backup
    controller,owner,data=isolated(tmp_path)
    try:
        # The same rows the 2026-10-15 host power-off produced through the lifespan hook.
        controller._db.execute("INSERT INTO pilot_events(attempt,code) VALUES(NULL,'OPERATOR_STOP')")
        controller._db.execute("UPDATE epochs SET status='CLOSED_COMPLETE',input_complete=1")
        bundle=backup.create_bundle(controller,owner,data,tmp_path/'archive/one');m=backup.validate_bundle(bundle)
    finally:controller.close()
    proof=validate_v2_archive(bundle,epoch=m['associations']['epochs'][0][0],implementation_hashes=m['source']['implementation_sha256'])
    assert proof.stop_attribution=='UNATTRIBUTED_V2_SHUTDOWN_HOOK'
    root=tmp_path/'hw';root.mkdir(mode=0o700);h=HighWater(root,create=True);seen=[]
    try:
        bindings=Bindings(*('source','config','release','pid','invocation','child','boot','start','challenge')).as_dict()
        proof=fresh_fixture_proof(proof)
        with pytest.raises(Refused,match='SUCCESSOR_AUTHORITY'):reserve_fixture(h,proof,bindings,authority=1)
        with pytest.raises(Refused,match='PREDECESSOR_PROOF'):reserve_fixture(h,PredecessorProof(proof.epoch,proof.archive_digest,0,proof.source_digest,'OPERATOR_INTENT_PROVEN'),bindings)
        seen.append(reserve_fixture(h,proof,bindings))
        assert seen[0]['stop_attribution']=='UNATTRIBUTED_V2_SHUTDOWN_HOOK' and seen[0]['retirement']=='EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT'
    finally:h.close()

@pytest.mark.parametrize('mutation',['manifest_byte','scope_duplicate_key','state_symlink','missing_member','extra_stop_code'])
def test_corrupt_predecessor_archive_refused_with_fixed_code(tmp_path,mutation):
    from tests.execution.shadow_pilot_backup_test import isolated
    from app.execution import shadow_backup as backup
    controller,owner,data=isolated(tmp_path)
    try:
        controller._db.execute("INSERT INTO pilot_events(attempt,code) VALUES(NULL,'OPERATOR_STOP')")
        if mutation=='extra_stop_code':controller._db.execute("INSERT INTO pilot_events(attempt,code) VALUES(NULL,'BACKUP_FAILURE')")
        controller._db.execute("UPDATE epochs SET status='CLOSED_COMPLETE',input_complete=1")
        bundle=backup.create_bundle(controller,owner,data,tmp_path/'archive/one');m=backup.validate_bundle(bundle)
    finally:controller.close()
    bundle.chmod(0o700)  # attacker with write access to the archive; V2 publishes it read-only
    for member in bundle.iterdir():member.chmod(0o600)
    if mutation=='manifest_byte':p=bundle/'manifest.json';b=bytearray(p.read_bytes());b[-2]^=1;p.write_bytes(bytes(b))
    if mutation=='scope_duplicate_key':p=bundle/'scope.json';p.write_bytes(b'{"version":1,"version":1}')
    if mutation=='state_symlink':p=bundle/'state.json';t=tmp_path/'elsewhere.json';t.write_bytes(p.read_bytes());p.unlink();p.symlink_to(t)
    if mutation=='missing_member':(bundle/'ownership.managed').unlink()
    with pytest.raises(Refused) as e:validate_v2_archive(bundle,epoch=m['associations']['epochs'][0][0],implementation_hashes=m['source']['implementation_sha256'])
    assert str(e.value) in ('V2_ARCHIVE_INPUT','V2_ARCHIVE_INVALID','DUPLICATE_JSON_KEY','INVALID_JSON','V2_NOT_CLEAN_ZERO_USE_STOP')

# ---------------------------------------------------------------- Part D: rollback and filesystem

def _copy_state(base,names,dest):
    dest.mkdir(mode=0o700)
    for n in names:shutil.copytree(base/n,dest/n,copy_function=shutil.copy2)

def _restore_state(base,names,src):
    for n in names:
        shutil.rmtree(base/n);shutil.copytree(src/n,base/n,copy_function=shutil.copy2)

@pytest.mark.asyncio
async def test_partial_rollback_of_highwater_or_controller_is_refused(integrated,tmp_path):
    f=integrated;saved=tmp_path.parent/(tmp_path.name+'-saved');_copy_state(tmp_path,('highwater',),saved)
    f.opened();await f.turn();f.high.close()
    _restore_state(tmp_path,('highwater',),saved);f.high=HighWater(tmp_path/'highwater')
    with pytest.raises(Refused,match='HIGHWATER_ROLLBACK_OR_INCOMPLETE_COMMIT'):f.high.check(f.store,allow_terminal=True)

@pytest.mark.asyncio
async def test_coordinated_full_rollback_is_not_detectable_locally(integrated,tmp_path):
    """Honest limit: same-UID state plus hashes can be replaced together. NOT antirollback."""
    f=integrated;names=('state','highwater','evidence','domains');saved=tmp_path.parent/(tmp_path.name+'-saved')
    _copy_state(tmp_path,names,saved)
    f.opened();await f.turn();assert f.store.count()==1;f.close()
    _restore_state(tmp_path,names,saved)
    store=Store(tmp_path/'state');high=HighWater(tmp_path/'highwater');ev=EvidenceBridge(tmp_path/'evidence')
    try:
        high.check(store);assert store.count()==0 and ev.validate()==0     # rollback accepted by every local check
        assert any(json.loads((p/'manifest.json').read_bytes())['accepted']==1 for p in (tmp_path/'coordinated').iterdir() if (p/'manifest.json').exists())
    finally:store.close();high.close();ev.close()
    f.close=lambda:None  # components already closed above

CHILD_RESERVATION='''
import json,resource,signal,sys
from pathlib import Path
signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
from candidate_v3.storage import Store
from candidate_v3.contracts import Refused
base=Path(sys.argv[1]);pred=dict(epoch='predecessor',status='CLOSED_COMPLETE',accepted=0,complete=True,unknown=False,retirement='EXPLICIT_ZERO_USE_RETIREMENT',archive='pinned-archive')
bind={k:k for k in ('source','config','release','pid','invocation','boot','start','challenge')};bind['epoch']='successor'
soft,hard=resource.getrlimit(resource.RLIMIT_FSIZE);resource.setrlimit(resource.RLIMIT_FSIZE,(64,hard))
try:Store(base/'state',predecessor=pred,child='successor',bindings=bind);out='CREATED'
except Refused as e:out=str(e)
except OSError as e:out='OSError'
resource.setrlimit(resource.RLIMIT_FSIZE,(soft,hard))
r=base/'lineage-reservation.json'
print(json.dumps({'result':out,'reservation_bytes':r.stat().st_size if r.exists() else None,'state_exists':(base/'state').exists()}))
'''

CHILD_CHECKPOINT='''
import json,resource,signal,sys
from pathlib import Path
signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
from candidate_v3.storage import Store,checkpoint,verify_checkpoint
from candidate_v3.contracts import Refused
base=Path(sys.argv[1]);pred=dict(epoch='predecessor',status='CLOSED_COMPLETE',accepted=0,complete=True,unknown=False,retirement='EXPLICIT_ZERO_USE_RETIREMENT',archive='pinned-archive')
bind={k:k for k in ('source','config','release','pid','invocation','boot','start','challenge')};bind['epoch']='successor'
store=Store(base/'state',predecessor=pred,child='successor',bindings=bind);backups=base/'backups';backups.mkdir(mode=0o700)
size=(base/'state'/'controller.sqlite3').stat().st_size
soft,hard=resource.getrlimit(resource.RLIMIT_FSIZE);resource.setrlimit(resource.RLIMIT_FSIZE,(size//2,hard))
try:checkpoint(store,backups);out='PUBLISHED'
except Refused as e:out='Refused:'+str(e)
except Exception as e:out=type(e).__name__
resource.setrlimit(resource.RLIMIT_FSIZE,(soft,hard))
verdicts=[]
for p in backups.iterdir():
    try:verify_checkpoint(p);verdicts.append('VALID')
    except Refused as e:verdicts.append(str(e))
    except Exception as e:verdicts.append(type(e).__name__)
print(json.dumps({'result':out,'bundles':verdicts,'checkpoint_rows':store.db.execute('SELECT count(*) FROM checkpoints').fetchone()[0],'ready':bool(store.ready())}))
'''

def _child(code,base):
    p=subprocess.run([sys.executable,'-c',code,str(base)],capture_output=True,text=True,timeout=60,cwd=str(Path.cwd()))
    assert p.returncode==0,p.stderr[-2000:]
    return json.loads(p.stdout.strip().splitlines()[-1])

def test_kernel_rlimit_short_write_on_successor_reservation(tmp_path):
    base=tmp_path/'root';base.mkdir(mode=0o700);r=_child(CHILD_RESERVATION,base)
    assert r=={'result':'RESERVATION_PARTIAL_WRITE','reservation_bytes':64,'state_exists':False}
    pred=dict(epoch='predecessor',status='CLOSED_COMPLETE',accepted=0,complete=True,unknown=False,retirement='EXPLICIT_ZERO_USE_RETIREMENT',archive='pinned-archive')
    bind={k:k for k in ('source','config','release','pid','invocation','boot','start','challenge')};bind['epoch']='successor'
    with pytest.raises(Refused,match='SUCCESSOR_ALREADY_RESERVED'):Store(base/'state',predecessor=pred,child='successor',bindings=bind)
    artifact('rlimit-reservation.json',r)

def test_kernel_rlimit_efbig_during_checkpoint_never_publishes(tmp_path):
    base=tmp_path/'root';base.mkdir(mode=0o700);r=_child(CHILD_CHECKPOINT,base)
    assert r['result']!='PUBLISHED' and r['checkpoint_rows']==0 and r['ready'] is False
    assert r['bundles'] and 'VALID' not in r['bundles']
    artifact('rlimit-checkpoint.json',r)

@pytest.mark.asyncio
async def test_permission_drift_blocks_checkpoint_and_next_permit(integrated):
    f=integrated;f.opened();await f.turn()
    (f.evidence.root/'observations.jsonl').chmod(0o644)
    with pytest.raises(Refused):f.runtime._checkpoint()
    with pytest.raises(Refused):f.arm('REST',ORIGINAL_INPUTS[1])
    assert f.store.count()==1

@pytest.mark.asyncio
async def test_symlinked_evidence_file_refused(integrated,tmp_path):
    f=integrated;f.opened();await f.turn()
    obs=f.evidence.root/'observations.jsonl';target=tmp_path.parent/(tmp_path.name+'-elsewhere');target.write_bytes(obs.read_bytes());target.chmod(0o600)
    obs.unlink();obs.symlink_to(target)
    with pytest.raises(Refused):f.evidence.validate()
    with pytest.raises(Refused):f.runtime._checkpoint()
