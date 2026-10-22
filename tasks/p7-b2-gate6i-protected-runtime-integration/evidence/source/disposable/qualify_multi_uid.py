#!/usr/bin/env python3
"""NOT authorized to run on Nexus/Core. Future operator-provisioned VM only.

Root is the narrow authority identity in this qualification. Three pre-existing
non-login identities are required. No account creation, install, network, sudo,
SSH, systemd, shell, production secret, or model lifecycle operations.
"""
import asyncio,ctypes,dataclasses,errno,json,multiprocessing,os,pwd,shutil,stat,sys,threading,time,uuid
from pathlib import Path

BASE=Path('/var/lib/g6i-disposable')
RELEASE=Path('/opt/g6i-release')
ROLES=('g6i-operator','g6i-service','g6i-agent')
sys.dont_write_bytecode=True
sys.path.insert(0,str(RELEASE/'repo'))
sys.path.append('/usr/lib/python3/dist-packages')


def network_guard():
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(38,1,0,0,0):raise RuntimeError('NO_NEW_PRIVS')
    sec=ctypes.CDLL('libseccomp.so.2');sec.seccomp_init.argtypes=[ctypes.c_uint32];sec.seccomp_init.restype=ctypes.c_void_p
    sec.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];sec.seccomp_syscall_resolve_name.restype=ctypes.c_int
    sec.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_int,ctypes.c_uint];sec.seccomp_load.argtypes=[ctypes.c_void_p];sec.seccomp_release.argtypes=[ctypes.c_void_p]
    class Compare(ctypes.Structure):_fields_=[('arg',ctypes.c_uint),('op',ctypes.c_int),('a',ctypes.c_uint64),('b',ctypes.c_uint64)]
    ctx=sec.seccomp_init(0x7fff0000)
    try:
        # Kernel blocks all network families except AF_UNIX, independent of mocks.
        if sec.seccomp_rule_add(ctx,0x50000|errno.EPERM,sec.seccomp_syscall_resolve_name(b'socket'),1,Compare(0,1,1,0)):raise RuntimeError('SECCOMP_RULE')
        if sec.seccomp_load(ctx):raise RuntimeError('SECCOMP_LOAD')
    finally:sec.seccomp_release(ctx)


def deny_access(paths):
    outcomes=[]
    for path in paths:
        for flags in (os.O_RDONLY,os.O_WRONLY):
            try:
                fd=os.open(path,flags|os.O_NOFOLLOW);os.close(fd);outcomes.append(False)
            except PermissionError:outcomes.append(True)
    return outcomes


def service_role(pipe,authority_pid,operator_pid,operator_uid):
    from tests.execution.v3_integration_test import Integrated
    from candidate_v3.contracts import canonical,digest,strict_json,Refused
    from candidate_v3.authority import Authority
    from candidate_v3.protected_authority import Ed25519Verifier
    from candidate_v3.authority_client import ServiceAuthorityClient
    from candidate_v3.local_control import UnixAuthorityConnection,ProcessPin
    from candidate_v3.checkpoints import CheckpointWriter
    from candidate_v3.application import build_protected_isolated_app
    from candidate_v3.source_memory import procedural_snapshot
    from candidate_v3.runtime import ORIGINAL_INPUTS
    from tests.execution.v3_candidate_test import Sink
    f=Integrated(BASE/'app');old_high=f.high
    memory=procedural_snapshot((RELEASE/'repo/skills.md').read_bytes(),expected_sha256='3a61af6054795cad154b5de00e4185063d32e08e592aba315bc8ef1560e6d4a2')
    f.runtime.legacy_policy=dataclasses.replace(f.runtime.legacy_policy,memory_snapshot=memory)
    pin=ProcessPin.capture(os.getuid(),os.getpid())
    inventory={'source':digest((BASE/'release/source').read_bytes())}
    f.bind=dataclasses.replace(f.bind,source=digest(canonical(inventory)),config=digest((BASE/'release/config').read_bytes()),pid=str(pin.pid),start=pin.start,boot=pin.boot)
    f.runtime.bindings=f.bind
    reservation=BASE/'app/lineage-reservation.json';value=strict_json(reservation.read_bytes());value['bindings']=f.bind.as_dict();reservation.write_bytes(canonical(value))
    f.store.db.execute("UPDATE meta SET value=? WHERE key='bindings'",(canonical(f.bind.as_dict()).decode(),))
    f.store.db.execute("UPDATE meta SET value=? WHERE key='lineage_hash'",(digest(reservation.read_bytes()),))
    contracts=dict(legacy_router=f.router,legacy_trivial=f.trivial,legacy_normal=f.normal,granite=f.granite)
    pipe.send(dict(uid=os.getuid(),pid=os.getpid(),bindings=f.bind,contracts=contracts))
    high=None
    while True:
        command,arg=pipe.recv()
        try:
            if command=='attach':
                f.authority=Authority(f.bind,Ed25519Verifier(arg,operator_id='dummy-human'),clock=lambda:100.,operator_id='dummy-human',peer_uid=operator_uid);f.runtime.authority=f.authority
                high=ServiceAuthorityClient(UnixAuthorityConnection(BASE/'run/service/control.sock',authority_pin=ProcessPin.capture(0,authority_pid)),contracts=contracts)
                f.runtime.acceptance_guard=high
                f.writer=CheckpointWriter(BASE/'app/coordinated',evidence=f.evidence,domains=f.domains,highwater=high,ownership=f.ownership);f.runtime.checkpoint_writer=f.writer
                f.runtime._checkpoint()
                f.app=build_protected_isolated_app(f.runtime,api_token=b'DUMMY',allowed_origins=set(),qualification='OFFLINE_EVALUATION_ONLY')
                shutil.copytree(BASE/'app',BASE/'backup/snapshot')
                result=True
            elif command=='prepare':
                payload={}
                if arg=='AUTHORIZE_ONE':
                    if 'REST' not in f.tokens:f.tokens['REST']=f.runtime.new_session('REST')
                    payload=dict(transport='REST',session=f.tokens['REST'][1],request_commitment=f.runtime.commitment(ORIGINAL_INPUTS[0]))
                result=dict(verb=arg,nonce=uuid.uuid4().hex,expires=130.,bindings=f.bind.as_dict(),checkpoint=digest((f.runtime.last_checkpoint/'manifest.json').read_bytes()),payload=payload)
            elif command=='apply':
                raw,sig=arg;f.runtime.apply_protected_command(strict_json(raw)['nonce']);result=True
            elif command=='attempt_unknown':
                async def attempt():
                    f.block='gemma3:4b'
                    work=asyncio.create_task(f.runtime.request(transport='REST',token=f.tokens['REST'][0],message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink()))
                    await asyncio.wait_for(f.entered.wait(),5);f.runtime.stop('OPERATOR_STOP')
                    try:await work
                    except Refused:pass
                    return dict(accepted=f.store.count(),clean=f.store.clean(),calls=len(f.calls),terminal=f.store.terminal())
                result=asyncio.run(attempt())
            elif command=='rollback':
                # Disposable rollback, all app files. Protected authority stays intact.
                f.store.close();f.domains.close();f.evidence.close();old_high.close()
                shutil.copytree(BASE/'backup/snapshot',BASE/'app',dirs_exist_ok=True)
                try:high.connection.call('CHECK',dict(expected={k:high.read()[k] for k in ('seq','seal')},allow_terminal=True));result=False
                except Refused:result=True
            elif command=='denials':
                result=deny_access([BASE/'authority/authority.sqlite3',BASE/'operator/signing.key'])
                for path in (BASE/'release/source',BASE/'release/config',BASE/'run/operator/control.sock'):
                    try:fd=os.open(path,os.O_WRONLY|os.O_NOFOLLOW);os.close(fd);result.append(False)
                    except (PermissionError,OSError):result.append(True)
                try:high.connection.call('SIGNED',dict(body={},signature='00'*64));result.append(False)
                except Refused:result.append(True)
            elif command=='exit':pipe.send(True);return
            else:raise RuntimeError('FIXED_RUNNER_COMMAND')
            pipe.send(result)
        except Exception as e:pipe.send({'failure':type(e).__name__})


def operator_role(pipe,authority_pid):
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat,PrivateFormat,NoEncryption
    from candidate_v3.local_control import OperatorCommandClient,UnixAuthorityConnection,ProcessPin
    from candidate_v3.contracts import canonical,Refused
    key=Ed25519PrivateKey.generate()
    fd=os.open(BASE/'operator/signing.key',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    os.write(fd,key.private_bytes(Encoding.Raw,PrivateFormat.Raw,NoEncryption()));os.close(fd)
    pipe.send(dict(uid=os.getuid(),pid=os.getpid(),public=key.public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)))
    client=OperatorCommandClient(UnixAuthorityConnection(BASE/'run/operator/control.sock',authority_pin=ProcessPin.capture(0,authority_pid)))
    while True:
        cmd,arg=pipe.recv()
        if cmd=='exit':pipe.send(True);return
        if cmd=='sign_submit':
            raw=canonical(arg);sig=key.sign(raw)
            try:client.submit(raw,sig);pipe.send((raw,sig))
            except Refused:pipe.send(False)
        elif cmd=='replay':
            try:client.submit(*arg);pipe.send(False)
            except Refused:pipe.send(True)
        elif cmd=='successor_race':
            from concurrent.futures import ThreadPoolExecutor
            def submit(body):
                raw=canonical(body);sig=key.sign(raw)
                try:client.submit(raw,sig);return True
                except Refused:return False
            with ThreadPoolExecutor(2) as pool:pipe.send(list(pool.map(submit,arg)))
        else:pipe.send(False)


def agent_role(pipe):
    pipe.send(dict(uid=os.getuid(),pid=os.getpid()))
    while True:
        cmd,arg=pipe.recv()
        if cmd=='exit':pipe.send(True);return
        if cmd!='denials':pipe.send(False);continue
        result=deny_access([BASE/'authority/authority.sqlite3',BASE/'operator/signing.key',BASE/'app/state/controller.sqlite3'])
        for p in (BASE/'release/source',BASE/'release/config'):
            try:fd=os.open(p,os.O_WRONLY);os.close(fd);result.append(False)
            except PermissionError:result.append(True)
        pipe.send(result)


def child(role,pipe,authority_pid,extra):
    entry=pwd.getpwnam(role);os.setgroups([]);os.setgid(entry.pw_gid);os.setuid(entry.pw_uid)
    network_guard()
    if role=='g6i-operator':operator_role(pipe,authority_pid)
    elif role=='g6i-service':service_role(pipe,authority_pid,*extra)
    else:agent_role(pipe)


def receive(pipe):
    if not pipe.poll(20):raise RuntimeError('CHILD_TIMEOUT')
    answer=pipe.recv()
    if isinstance(answer,dict) and 'failure' in answer:raise RuntimeError(answer['failure'])
    return answer


def main():
    # Refuse before any writes on the current known machines or unapproved VM.
    if os.geteuid()!=0:raise RuntimeError('OPERATOR_PROVISIONED_ROOT_RUN_REQUIRED')
    marker=Path('/etc/g6i-disposable-approved.json')
    st=marker.lstat()
    if st.st_uid!=0 or stat.S_IMODE(st.st_mode)!=0o600 or marker.is_symlink():raise RuntimeError('APPROVAL_MARKER')
    approval=json.loads(marker.read_text())
    machine=Path('/etc/machine-id').read_text().strip()
    if approval!={'machine_id':machine,'scope':'GATE6I_DISPOSABLE_ONLY','network':'NO_NIC','release':'/opt/g6i-release'}:raise RuntimeError('APPROVAL_SCOPE')
    if os.uname().nodename in ('jarvis','nexus-services','pve') or set(p.name for p in Path('/sys/class/net').iterdir())!={'lo'}:raise RuntimeError('NOT_ISOLATED_VM')
    if Path('/home/jarvis').exists() or Path('/home/nexus').exists():raise RuntimeError('PRODUCTION_HOME_PRESENT')
    entries={r:pwd.getpwnam(r) for r in ROLES}
    if len({0,*(e.pw_uid for e in entries.values())})!=4:raise RuntimeError('DISTINCT_KERNEL_UIDS_REQUIRED')
    for p in [RELEASE,*RELEASE.rglob('*')]:
        st=p.lstat()
        if p.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise RuntimeError('IMMUTABLE_RELEASE_REQUIRED')
    network_guard();BASE.mkdir(mode=0o755)
    for name,role in [('app','g6i-service'),('backup','g6i-service'),('operator','g6i-operator')]:
        p=BASE/name;p.mkdir(mode=0o700);os.chown(p,entries[role].pw_uid,entries[role].pw_gid)
    (BASE/'authority').mkdir(mode=0o700);(BASE/'run').mkdir(mode=0o755);(BASE/'release').mkdir(mode=0o755)
    for name in ('source','config'):(BASE/'release'/name).write_text('DISPOSABLE_FIXTURE\n');(BASE/'release'/name).chmod(0o444)
    for channel,role in [('operator','g6i-operator'),('service','g6i-service')]:
        p=BASE/'run'/channel;p.mkdir(mode=0o750);os.chown(p,0,entries[role].pw_gid)
    ctx=multiprocessing.get_context('fork');children=[];servers=[];threads=[]
    def launch(role,extra=()):
        parent,other=ctx.Pipe();process=ctx.Process(target=child,args=(role,other,os.getpid(),extra));process.start();other.close();children.append((process,parent));return parent,receive(parent)
    try:
        op,opinfo=launch('g6i-operator');svc,info=launch('g6i-service',(opinfo['pid'],opinfo['uid']));agent,agentinfo=launch('g6i-agent')
        from candidate_v3.contracts import canonical,digest
        from candidate_v3.authority import Authority,SUCCESSOR_VERB
        from candidate_v3.protected_authority import Ed25519Verifier
        from candidate_v3.runtime_authority import RuntimeJournal,ControllerReader,AuthorityService,ReleaseIdentityReader
        from candidate_v3.local_control import UnixAuthorityServer,ProcessPin
        from candidate_v3.lineage import PredecessorProof,successor_payload
        from tests.execution.v3_successor_support import fresh_fixture_proof
        bind=info['bindings'];proof=fresh_fixture_proof(PredecessorProof('predecessor','a'*64,0,'b'*64))
        authority=Authority(bind,Ed25519Verifier(opinfo['public'],operator_id='dummy-human'),clock=lambda:100.,operator_id='dummy-human',peer_uid=opinfo['uid'])
        resources={r:digest(canonical(dataclasses.asdict(c))) for r,c in info['contracts'].items()}
        identity=ReleaseIdentityReader(BASE/'release',{'source':digest((BASE/'release/source').read_bytes())},BASE/'release/config',bind.config,bind,ProcessPin.capture(info['uid'],info['pid']))
        journal=RuntimeJournal(BASE/'authority',owner_uid=0,service_uid=info['uid'],authority=authority,predecessor_reader=lambda:proof,identity_reader=identity,provider_resources=resources,create=True)
        # Intentionally no provider terminal witness: unknown can NEVER be cleared.
        service=AuthorityService(journal,ControllerReader(BASE/'app/state',BASE/'app/coordinated',service_uid=info['uid']),terminal_reader=lambda pending:dict(terminal=False,association=pending),contracts=info['contracts'])
        for channel,peer in [('operator',opinfo),('service',info)]:
            server=UnixAuthorityServer(BASE/'run'/channel/'control.sock',service,channel=channel,peer_pin=ProcessPin.capture(peer['uid'],peer['pid']),group=entries['g6i-'+channel].pw_gid)
            thread=threading.Thread(target=server.serve,daemon=True);thread.start();servers.append(server);threads.append(thread)
        payload=successor_payload(proof,bind.as_dict())
        bodies=[dict(verb=SUCCESSOR_VERB,nonce=uuid.uuid4().hex,expires=130.,bindings=bind.as_dict(),checkpoint=digest(canonical(payload)),payload=payload) for _ in range(2)]
        op.send(('successor_race',bodies));assert sorted(receive(op))==[False,True]
        svc.send(('attach',opinfo['public']));assert receive(svc) is True
        for verb in ('OPEN_HOLD','AUTHORIZE_ONE'):
            svc.send(('prepare',verb));body=receive(svc);op.send(('sign_submit',body));signed=receive(op);assert signed
            svc.send(('apply',signed));assert receive(svc) is True
            op.send(('replay',signed));assert receive(op) is True
        svc.send(('denials',None));assert all(receive(svc));agent.send(('denials',None));assert all(receive(agent))
        svc.send(('attempt_unknown',None));result=receive(svc);assert result==dict(accepted=1,clean=False,calls=1,terminal='CLOSED_INCOMPLETE')
        before=journal.read();assert len(before['accepted'])==1 and before['pending'] and before['terminal']
        svc.send(('rollback',None));assert receive(svc) is True
        journal.close()
        journal=RuntimeJournal(BASE/'authority',owner_uid=0,service_uid=info['uid'],authority=authority,predecessor_reader=lambda:proof,identity_reader=identity,provider_resources=resources)
        service.journal=journal;assert journal.read()==before
        report={'result':'PASS','kernel_uids':{'authority':0,'operator':opinfo['uid'],'service':info['uid'],'agent':agentinfo['uid']},'process_ids':[os.getpid(),opinfo['pid'],info['pid'],agentinfo['pid']],
                'checks':['immutable release','key read denial','protected root read/write denial','real accept and peer credentials','signed successor race','signature and nonce replay','durable approval and permit consumption','possible send survives uncertainty','D06 remains unknown','whole app and controller/backup rollback refusal','authority database reopen preservation','no network families except AF_UNIX'],
                'limits':['synthetic predecessor/model data','no independent provider terminal witness','on-host root rollback outside guarantee','process-kill boundary suite must also pass']}
        (BASE/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
        journal.close()
    finally:
        for process,pipe in children:
            if process.is_alive():
                try:pipe.send(('exit',None));receive(pipe)
                except Exception:pass
            process.join(2)
            if process.is_alive():process.terminate();process.join(2)
        for server in servers:server.close()
        for thread in threads:thread.join(2)

if __name__=='__main__':main()
