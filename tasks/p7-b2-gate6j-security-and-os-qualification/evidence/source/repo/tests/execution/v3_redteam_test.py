"""Gate6J adversarial regressions. All providers and identities are fixtures."""
import time
import pytest
from candidate_v3.contracts import Refused,ProviderRequest,canonical,digest
from candidate_v3.runtime import ORIGINAL_INPUTS
from tests.execution.v3_protected_runtime_test import protected


def local_request(f, protected_send=False):
    f.opened();tok=f.arm();session=f.runtime.sessions[tok]
    c=f.runtime.commitment(ORIGINAL_INPUTS[0])
    f.high.before_accept(f.store,'REST',session.id,c)
    aid=f.store.accept('REST',session.id,c,now=100);f.high.after_accept(f.store)
    contract=f.router
    body=canonical(dict(model=contract.resource.model,messages=[dict(role='user',content='fixture')],stream=False,think=False,keep_alive=60,options=dict(num_ctx=4096,num_predict=64,temperature=0.1)))
    sid=f.store.begin(aid,'LEGACY_ROUTER',contract.resource,digest(body))
    if protected_send:f.high.possible_send(f.store,aid,'LEGACY_ROUTER',contract,digest(body))
    return ProviderRequest(aid,sid,contract.resource,body,digest(body),time.monotonic()+20)

@pytest.mark.asyncio
async def test_direct_provider_without_protected_send_refuses(protected):
    f=protected;req=local_request(f)
    with pytest.raises(Refused):await f.native_original(req)
    assert not f.calls and f.journal.read()['pending'] is None

@pytest.mark.asyncio
async def test_direct_native_without_protected_send_refuses(protected):
    from app.brain.model_ownership import ModelResourceKeyV1
    f=protected;req=local_request(f);owner=f.ownership[0].coordinator
    with owner.begin_generation(ModelResourceKeyV1('ollama',req.resource.endpoint,req.resource.model),req.substep) as lease:
        lease.mark_may_dispatch()
        with pytest.raises(Refused):await f.native.request(req,ownership=lease)
    assert not f.calls

@pytest.mark.asyncio
async def test_dispatch_claim_is_durable_and_one_use(protected):
    f=protected;req=local_request(f,True)
    await f.native_original(req)
    state=f.journal.read()
    assert state['dispatches']==[state['pending']['send_seq']] and len(f.calls)==1
    with pytest.raises(Refused):f.high.dispatch_once(req)

@pytest.mark.parametrize('field',['attempt','substep','request_digest'])
def test_dispatch_rejects_conflicting_association(protected,field):
    import dataclasses
    f=protected;req=local_request(f,True)
    req=dataclasses.replace(req,**{field:'f'*(64 if field=='request_digest' else 32)})
    with pytest.raises(Refused):f.high.dispatch_once(req)
    assert f.journal.read()['dispatches']==[] and not f.calls

@pytest.mark.parametrize('boundary',['before_commit','after_commit'])
def test_dispatch_lost_ack_disposition(protected,boundary):
    f=protected;req=local_request(f,True)
    def fail(where):
        if where==boundary:raise RuntimeError('fixture interruption')
    f.journal.fault=fail
    with pytest.raises(Refused):f.high.dispatch_once(req)
    f.journal.fault=lambda _:None
    state=f.journal.read()
    assert bool(state['dispatches'])==(boundary=='after_commit')
    assert state['pending'] and not f.calls
    if boundary=='after_commit':
        with pytest.raises(Refused):f.high.dispatch_once(req)


def test_dispatch_after_signed_stop_refuses(protected):
    f=protected;req=local_request(f,True)
    raw,sig=f.approval('TERMINAL_STOP');f.operator.submit(raw,sig)
    with pytest.raises(Refused):f.high.dispatch_once(req)
    assert not f.journal.read()['dispatches']


def test_checkpoint_uses_one_captured_snapshot(protected,monkeypatch):
    from candidate_v3.checkpoints import validate_coordinated
    import candidate_v3.storage as storage
    f=protected;root=f.writer.last;calls={};original=storage.read_snapshot_bytes
    def once(path,**kwargs):
        calls[str(path)]=calls.get(str(path),0)+1
        assert calls[str(path)]==1
        return original(path,**kwargs)
    monkeypatch.setattr(storage,'read_snapshot_bytes',once)
    snapshot={};validate_coordinated(root,minimum_accepted=0,snapshot=snapshot)
    assert set(snapshot)=={p.name for p in root.iterdir()}-{'manifest.json'}

@pytest.mark.parametrize('attack',['fifo','oversize','symlink_parent','hardlink'])
def test_privileged_snapshot_input_bounds(tmp_path,attack):
    import os
    from candidate_v3.storage import read_snapshot_bytes
    p=tmp_path/'input';p.write_bytes(b'fixture');p.chmod(0o600)
    if attack=='fifo':p.unlink();os.mkfifo(p,0o600)
    elif attack=='oversize':p.write_bytes(b'x'*65)
    elif attack=='symlink_parent':
        link=tmp_path/'alias';link.symlink_to(tmp_path,target_is_directory=True);p=link/'input'
    else:os.link(p,tmp_path/'other')
    with pytest.raises(Refused):read_snapshot_bytes(p,owner_uid=os.getuid(),limit=64)


def test_checkpoint_manifest_bound(protected):
    from candidate_v3.checkpoints import validate_coordinated
    f=protected;(f.writer.last/'manifest.json').write_bytes(b' '*65537)
    with pytest.raises(Refused,match='SNAPSHOT_FILE_BOUNDARY'):validate_coordinated(f.writer.last,minimum_accepted=0)


def test_connected_socket_cannot_be_delegated_to_other_process(protected):
    import socket,struct,subprocess,sys
    f=protected
    packet=canonical(dict(version=1,operation='READ',arguments={}))
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as client:
        client.connect(str(f.socket_dir/'service'))
        code="import os;os.write(%d,%r)"%(client.fileno(),struct.pack('!I',len(packet))+packet)
        subprocess.run([sys.executable,'-c',code],pass_fds=(client.fileno(),),check=True,timeout=5)
        client.settimeout(2)
        from candidate_v3.local_control import _receive
        response=_receive(client,time.monotonic()+2)
        assert response['accepted'] is False


def test_untrusted_snapshot_sql_work_is_bounded():
    import sqlite3
    from candidate_v3.storage import snapshot_database
    original=sqlite3.connect(':memory:');original.execute('CREATE TABLE fixture(x)');raw=original.serialize();original.close()
    db=snapshot_database(raw)
    try:
        with pytest.raises(sqlite3.OperationalError,match='interrupted'):
            db.execute('WITH RECURSIVE q(x) AS (VALUES(0) UNION ALL SELECT x+1 FROM q) SELECT sum(x) FROM q').fetchone()
    finally:db.close()


def test_authority_incomplete_downgrades_local_terminal(protected):
    f=protected;f.opened();tok=f.arm();session=f.runtime.sessions[tok]
    f.high.before_accept(f.store,'REST',session.id,f.runtime.commitment(ORIGINAL_INPUTS[0]))
    # Durable acceptance exists, but a crash prevented its local D09 join.
    f.runtime.stop('OPERATOR_STOP')
    assert f.journal.read()['terminal_status']=='CLOSED_INCOMPLETE'
    assert f.store.terminal()==f.runtime.state=='CLOSED_INCOMPLETE'

@pytest.mark.parametrize('boundary',['before_commit','after_commit'])
def test_dispatch_process_crash_preserves_one_disposition(protected,boundary):
    import subprocess,sys,os
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
    from candidate_v3.runtime_authority import token
    f=protected;req=local_request(f,True);before=f.journal.read()
    public=f.key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)
    script=f'''import os,sys
sys.path.append('/usr/lib/python3/dist-packages')
from candidate_v3.runtime_authority import *
from candidate_v3.contracts import Bindings
from candidate_v3.authority import Authority
from candidate_v3.protected_authority import Ed25519Verifier
b=Bindings(**{f.bind.as_dict()!r})
a=Authority(b,Ed25519Verifier({public!r},operator_id='dummy-human'),clock=lambda:100.,operator_id='dummy-human',peer_uid=os.getuid())
def fault(point):
 if point=={boundary!r}:os._exit(77)
j=RuntimeJournal({str(f.journal.root)!r},owner_uid=os.getuid(),service_uid=os.getuid(),authority=a,predecessor_reader=lambda:None,identity_reader=b.as_dict,provider_resources={f.journal.provider_resources!r},fault=fault)
reader=ControllerReader({str(f.store.root)!r},{str(f.writer.root)!r},service_uid=os.getuid())
j.dispatch_once(peer=(os.getuid(),os.getpid()),expected={token(before)!r},association_reader=reader.check)
'''
    result=subprocess.run([sys.executable,'-c',script],capture_output=True,timeout=10)
    assert result.returncode==77,result.stderr.decode()
    after=f.journal.read()
    assert after['seq']==before['seq']+(boundary=='after_commit')
    assert bool(after['dispatches'])==(boundary=='after_commit') and after['pending']==before['pending']
    if boundary=='after_commit':
        with pytest.raises(Refused):f.high.dispatch_once(req)
    assert not f.calls


def test_concurrent_dispatch_claims_exactly_one(protected):
    from concurrent.futures import ThreadPoolExecutor
    from candidate_v3.runtime_authority import token
    f=protected;req=local_request(f,True);expected=token(f.journal.read())
    args=dict(expected=expected,attempt=req.attempt,substep=req.substep,role='legacy_router',request_digest=req.request_digest)
    def call(_):
        try:f.high.connection.call('DISPATCH',args);return True
        except Refused:return False
    with ThreadPoolExecutor(2) as pool:assert sorted(pool.map(call,range(2)))==[False,True]
    assert len(f.journal.read()['dispatches'])==1 and not f.calls

@pytest.mark.asyncio
async def test_protected_second_attempt_cannot_add_classifier(protected):
    f=protected;f.opened();await f.turn('REST',ORIGINAL_INPUTS[0])
    tok=f.arm('REST',ORIGINAL_INPUTS[1]);session=f.runtime.sessions[tok];commitment=f.runtime.commitment(ORIGINAL_INPUTS[1])
    f.high.before_accept(f.store,'REST',session.id,commitment)
    aid=f.store.accept('REST',session.id,commitment,now=100);f.high.after_accept(f.store)
    f.store.begin(aid,'LEGACY_ROUTER',f.router.resource,'b'*64)
    before=len(f.calls)
    with pytest.raises(Refused):f.high.possible_send(f.store,aid,'LEGACY_ROUTER',f.router,'b'*64)
    assert len(f.calls)==before and len(f.journal.read()['accepted'])==2
