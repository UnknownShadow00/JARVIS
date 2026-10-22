#!/usr/bin/env python3
"""NOT authorized to run on Nexus/Core. Future operator-provisioned VM only.

Root is the narrow authority identity in this qualification. Three pre-existing
non-login identities are required. No account creation, install, network, sudo,
SSH, systemd, shell, production secret, or model lifecycle operations.
"""
import asyncio,ctypes,dataclasses,errno,grp,json,os,pwd,shutil,socket,stat,sys,threading,time,uuid
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from process_boundary import role_context,SafePipe
from safety_preflight import validate_environment,validate_approval,verify_manifest,validate_dependencies,CREDENTIAL_PATHS,read_approval,validate_capacity
from offline_artifacts import verify_artifacts

BASE=Path('/var/lib/g6j-disposable')
RELEASE=Path('/opt/g6j-release')
ROLES=('g6j-operator','g6j-service','g6j-agent')
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
    if not ctx:raise RuntimeError('SECCOMP_INIT')
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
                fd=os.open(path,flags|os.O_NOFOLLOW|os.O_NONBLOCK);os.close(fd);outcomes.append(False)
            except PermissionError:outcomes.append(True)
    return outcomes


def mutation_denials(paths):
    """Kernel denials only: ENOENT/EINVAL/other failures must fail qualification."""
    outcomes=[]
    for path in paths:
        attacks=(lambda:os.open(path,os.O_WRONLY|os.O_TRUNC|os.O_NOFOLLOW|os.O_NONBLOCK),
                 lambda:os.chmod(path,0o600),lambda:os.unlink(path),
                 lambda:os.rename(path,path.with_name(path.name+'.moved')),
                 lambda:os.link(path,path.with_name(path.name+'.hardlink')),
                 lambda:os.symlink('fixture',path.with_name(path.name+'.symlink')))
        for attack in attacks:
            try:
                result=attack()
                if isinstance(result,int):os.close(result)
                outcomes.append(False)
            except PermissionError:outcomes.append(True)
    return outcomes


def socket_mutation_denials(path):
    # Socket open(2) is not a permission proof. Exercise path mutation syscalls.
    outcomes=[]
    for attack in (lambda:os.unlink(path),lambda:os.rename(path,path.with_name('replacement.sock')),
                   lambda:os.chmod(path,0o666),lambda:os.symlink('fixture',path.parent/'new.sock')):
        try:attack();outcomes.append(False)
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
                races=[]
                def consume_race(store,transport,session,commitment):
                    from concurrent.futures import ThreadPoolExecutor
                    high.check(store)
                    permit=store.db.execute('SELECT nonce FROM permits WHERE spent=0').fetchone()[0]
                    expected=dict(high.cursor)
                    def consume(_):
                        try:high.connection.call('CONSUME',dict(expected=expected,permit=permit));return True
                        except Refused:return False
                    with ThreadPoolExecutor(2) as pool:races.extend(pool.map(consume,range(2)))
                    if sorted(races)!=[False,True]:raise RuntimeError('CONSUMPTION_RACE')
                    high.read()
                high.before_accept=consume_race  # Inject concurrency at the REAL runtime acceptance boundary.
                async def attempt():
                    f.block='gemma3:4b'
                    work=asyncio.create_task(f.runtime.request(transport='REST',token=f.tokens['REST'][0],message=ORIGINAL_INPUTS[0],authenticated=True,delivery=Sink()))
                    await asyncio.wait_for(f.entered.wait(),5);f.runtime.stop('OPERATOR_STOP')
                    try:await work
                    except Refused:pass
                    return dict(accepted=f.store.count(),clean=f.store.clean(),calls=len(f.calls),terminal=f.store.terminal(),consume_race=sorted(races))
                result=asyncio.run(attempt())
            elif command=='rollback':
                # Disposable rollback, all app files. Protected authority stays intact.
                f.store.close();f.domains.close();f.evidence.close();old_high.close()
                shutil.copytree(BASE/'backup/snapshot',BASE/'app',dirs_exist_ok=True)
                try:high.connection.call('CHECK',dict(expected={k:high.read()[k] for k in ('seq','seal')},allow_terminal=True));result=False
                except Refused:result=True
            elif command=='denials':
                result=deny_access([BASE/'authority/authority.sqlite3',BASE/'operator/signing.key'])
                result+=mutation_denials([BASE/'authority/authority.sqlite3',BASE/'release/source',BASE/'release/config',BASE/'operator/signing.key',RELEASE/'repo/candidate_v3/runtime_authority.py'])
                result+=socket_mutation_denials(BASE/'run/service/control.sock')
                for path in (BASE/'release/source',BASE/'release/config'):
                    try:fd=os.open(path,os.O_WRONLY|os.O_NOFOLLOW);os.close(fd);result.append(False)
                    except PermissionError:result.append(True)
                with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as peer:
                    try:peer.connect(str(BASE/'run/operator/control.sock'));result.append(False)
                    except PermissionError:result.append(True)
                rejected=UnixAuthorityConnection(BASE/'run/service/reject.sock',authority_pin=ProcessPin.capture(0,authority_pid))
                try:rejected.call('READ',{});result.append(False)
                except Refused:result.append(True)
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
        elif cmd=='sign_submit_drop':
            import struct
            raw=canonical(arg);sig=key.sign(raw)
            packet=canonical(dict(version=1,operation='SIGNED',arguments=dict(body=arg,signature=sig.hex())))
            with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
                connection.settimeout(2);connection.connect(str(BASE/'run/operator/control.sock'))
                connection.sendall(struct.pack('!I',len(packet))+packet)
            pipe.send((raw,sig))  # Deliberately no authority acknowledgment read.
        elif cmd=='invalid_signed':
            outcomes=[]
            for body,invalid_signature in ((arg,True),(dict(arg,expires=99.),False)):
                raw=canonical(body);sig=bytes(64) if invalid_signature else key.sign(raw)
                try:client.submit(raw,sig);outcomes.append(False)
                except Refused:outcomes.append(True)
            pipe.send(outcomes)
        elif cmd=='denials':
            pipe.send(mutation_denials([BASE/'authority/authority.sqlite3',BASE/'release/source',BASE/'release/config']))
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


def agent_role(pipe,authority_pid):
    pipe.send(dict(uid=os.getuid(),pid=os.getpid()))
    while True:
        cmd,arg=pipe.recv()
        if cmd=='exit':pipe.send(True);return
        if cmd!='denials':pipe.send(False);continue
        from candidate_v3.local_control import UnixAuthorityConnection,ProcessPin
        from candidate_v3.contracts import Refused
        result=deny_access([BASE/'authority/authority.sqlite3',BASE/'operator/signing.key',BASE/'app/state/controller.sqlite3'])
        client=UnixAuthorityConnection(BASE/'run/service/control.sock',authority_pin=ProcessPin.capture(0,authority_pid))
        try:client.call('READ',{'uid':0,'pid':authority_pid});result.append(False)
        except Refused:result.append(True)
        result+=mutation_denials([BASE/'authority/authority.sqlite3',BASE/'release/source',BASE/'release/config',BASE/'operator/signing.key',RELEASE/'repo/candidate_v3/runtime_authority.py'])
        for p in (BASE/'release/source',BASE/'release/config'):
            try:fd=os.open(p,os.O_WRONLY);os.close(fd);result.append(False)
            except PermissionError:result.append(True)
        pipe.send(result)


def child(role,pipe,authority_pid,extra):
    entry=pwd.getpwnam(role);os.setgroups([]);os.setgid(entry.pw_gid);os.setuid(entry.pw_uid)
    network_guard()
    if role=='g6j-operator':operator_role(pipe,authority_pid)
    elif role=='g6j-service':service_role(pipe,authority_pid,*extra)
    else:agent_role(pipe,authority_pid)


def receive(pipe):
    if not pipe.poll(20):raise RuntimeError('CHILD_TIMEOUT')
    answer=pipe.recv()
    if isinstance(answer,dict) and 'failure' in answer:raise RuntimeError(answer['failure'])
    return answer


def validate_roles(entries,groups):
    if len({0,*(e.pw_uid for e in entries.values())})!=4:raise RuntimeError('DISTINCT_KERNEL_UIDS_REQUIRED')
    if len({0,*(e.pw_gid for e in entries.values())})!=4:raise RuntimeError('DISTINCT_PRIVATE_GROUPS_REQUIRED')
    for role,entry in entries.items():
        if entry.pw_shell not in ('/usr/sbin/nologin','/sbin/nologin','/bin/false'):raise RuntimeError('NONLOGIN_ROLE_REQUIRED')
        if any(role in group.gr_mem and group.gr_gid!=entry.pw_gid for group in groups):raise RuntimeError('SUPPLEMENTARY_GROUPS_FORBIDDEN')


def main():
    # Refuse before any writes on the current known machines or unapproved VM.
    if os.geteuid()!=0:raise RuntimeError('OPERATOR_PROVISIONED_ROOT_RUN_REQUIRED')
    marker=Path('/etc/g6k-disposable-approved.json')
    approval=read_approval(marker)
    machine=Path('/etc/machine-id').read_text().strip()
    validate_approval(approval,machine)
    validate_environment(hostname=os.uname().nodename,interfaces=[p.name for p in Path('/sys/class/net').iterdir()],
        mountinfo=Path('/proc/self/mountinfo').read_text(),credential_paths=[p for p in CREDENTIAL_PATHS if Path(p).exists()])
    verify_manifest(RELEASE,approval['source_manifest'])
    validate_dependencies(RELEASE)
    verify_artifacts(RELEASE,Path('/opt/g6k-offline'),approval['artifacts_sha256'])
    validate_capacity(BASE.parent)
    if BASE.exists() or BASE.is_symlink():raise RuntimeError('PREEXISTING_FIXTURE_REFUSED')
    if os.uname().machine!='x86_64':raise RuntimeError('X86_64_REQUIRED')
    entries={r:pwd.getpwnam(r) for r in ROLES}
    validate_roles(entries,grp.getgrall())
    for p in [RELEASE,*RELEASE.rglob('*')]:
        st=p.lstat()
        if p.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise RuntimeError('IMMUTABLE_RELEASE_REQUIRED')
    network_guard();os.umask(0o022);BASE.mkdir(mode=0o755)
    for name,role in [('app','g6j-service'),('backup','g6j-service'),('operator','g6j-operator')]:
        p=BASE/name;p.mkdir(mode=0o700);os.chown(p,entries[role].pw_uid,entries[role].pw_gid)
    (BASE/'authority').mkdir(mode=0o700);(BASE/'run').mkdir(mode=0o755);(BASE/'release').mkdir(mode=0o755)
    for name in ('source','config'):(BASE/'release'/name).write_text('DISPOSABLE_FIXTURE\n');(BASE/'release'/name).chmod(0o444)
    for channel,role in [('operator','g6j-operator'),('service','g6j-service')]:
        p=BASE/'run'/channel;p.mkdir(mode=0o750);os.chown(p,0,entries[role].pw_gid)
    ctx=role_context();children=[];servers=[];threads=[]
    def launch(role,extra=()):
        left,right=ctx.Pipe();parent,other=SafePipe(left),SafePipe(right);process=ctx.Process(target=child,args=(role,other,os.getpid(),extra));process.start();other.close();children.append((process,parent));return parent,receive(parent)
    cases=[]
    def check(name,passed):
        cases.append(dict(name=name,status='PASS' if passed else 'FAIL',layer='distinct-kernel-UID'))
        if not passed:raise RuntimeError('QUALIFICATION_CASE_FAILED')
    try:
        op,opinfo=launch('g6j-operator');svc,info=launch('g6j-service',(opinfo['pid'],opinfo['uid']));agent,agentinfo=launch('g6j-agent')
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
            server=UnixAuthorityServer(BASE/'run'/channel/'control.sock',service,channel=channel,peer_pin=ProcessPin.capture(peer['uid'],peer['pid']),group=entries['g6j-'+channel].pw_gid)
            thread=threading.Thread(target=server.serve,daemon=True);thread.start();servers.append(server);threads.append(thread)
        server=UnixAuthorityServer(BASE/'run/service/reject.sock',service,channel='service',peer_pin=ProcessPin.capture(opinfo['uid'],opinfo['pid']),group=entries['g6j-service'].pw_gid)
        thread=threading.Thread(target=server.serve,daemon=True);thread.start();servers.append(server);threads.append(thread)
        payload=successor_payload(proof,bind.as_dict())
        bodies=[dict(verb=SUCCESSOR_VERB,nonce=uuid.uuid4().hex,expires=130.,bindings=bind.as_dict(),checkpoint=digest(canonical(payload)),payload=payload) for _ in range(2)]
        before_invalid=journal.read()
        op.send(('invalid_signed',bodies[0]));check('invalid-and-expired-signature-correct-peer',receive(op)==[True,True] and journal.read()==before_invalid)
        op.send(('successor_race',bodies));check('concurrent-successor-reservation',sorted(receive(op))==[False,True])
        svc.send(('attach',opinfo['public']));check('service-approved-operation',receive(svc) is True)
        for verb in ('OPEN_HOLD','AUTHORIZE_ONE'):
            svc.send(('prepare',verb));body=receive(svc);op.send(('sign_submit_drop' if verb=='OPEN_HOLD' else 'sign_submit',body));signed=receive(op);check('signed-'+verb,bool(signed))
            if verb=='OPEN_HOLD':
                deadline=time.monotonic()+3
                while body['nonce'] not in journal.read()['commands'] and time.monotonic()<deadline:time.sleep(0.01)
                check('lost-open-ack-remains-durable',body['nonce'] in journal.read()['commands'])
            svc.send(('apply',signed));check('service-approved-operation',receive(svc) is True)
            op.send(('replay',signed));check('signed-replay-'+verb,receive(op) is True)
        svc.send(('denials',None));check('service-storage-and-signing-and-kernel-peer-denials',all(receive(svc)));agent.send(('denials',None));check('agent-storage-import-and-forged-identity-denials',all(receive(agent)))
        op.send(('denials',None));check('operator-direct-authority-write-denial',all(receive(op)))
        svc.send(('attempt_unknown',None));result=receive(svc);check('possible-send-and-D06-unknown',result==dict(accepted=1,clean=False,calls=1,terminal='CLOSED_INCOMPLETE',consume_race=[False,True]))
        check('concurrent-permit-consumption',result['consume_race']==[False,True])
        before=journal.read();check('nonrefundable-protected-acceptance',len(before['accepted'])==1 and bool(before['pending']) and before['terminal'])
        svc.send(('rollback',None));check('all-app-controller-backup-rollback-refusal',receive(svc) is True)
        journal.close()
        journal=RuntimeJournal(BASE/'authority',owner_uid=0,service_uid=info['uid'],authority=authority,predecessor_reader=lambda:proof,identity_reader=identity,provider_resources=resources)
        service.journal=journal;check('authority-reopen-preservation',journal.read()==before)
        op.send(('replay',signed));check('signed-replay-after-authority-reopen',receive(op) is True)
        report={'result':'PASS','kernel_uids':{'authority':0,'operator':opinfo['uid'],'service':info['uid'],'agent':agentinfo['uid']},'process_ids':[os.getpid(),opinfo['pid'],info['pid'],agentinfo['pid']],
                'cases':cases,'additional_scope':'same-UID JUnit suite must also pass','checks':['immutable release','key read denial','protected root read/write/chmod/unlink/rename/link denial','real accept and peer credentials','signed successor race','signature and nonce replay','durable approval and permit consumption','possible send survives uncertainty','D06 remains unknown','whole app and controller/backup rollback refusal','authority database reopen preservation','no network families except AF_UNIX'],
                'limits':['synthetic predecessor/model data','no independent provider terminal witness','on-host root rollback outside guarantee','process-kill boundary suite must also pass']}
        (BASE/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
        journal.close()
    except BaseException as error:
        (BASE/'report.json').write_text(json.dumps({'result':'FAIL','failure':type(error).__name__,'real_multi_uid_qualified':False,'cases':cases})+'\n')
        raise
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
