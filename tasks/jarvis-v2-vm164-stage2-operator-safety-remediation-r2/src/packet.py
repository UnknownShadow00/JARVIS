"""R2 offline proposals and fail-closed predicates. No command execution."""
import datetime as dt

import json

import re

SOURCE_PIN = '43ea91000e251b9cf34fadf0466cb5135042a3232686c155de1b4ab5ee1ad3d1'

CALLBACK_PIN = 'a0ba1ef999c58c771e679f3765eac41bb52671968930726a2a4de96a98a301fa'

PUBLIC = '/opt/jarvis-vm164-r3-stage2/canary.py'

CASES = ('success', 'exit7', 'missingexec', 'missingdep', 'timeout', 'late',
         'inactive', 'failedtimer', 'collision', 'cancel', 'rearm-a', 'rearm-b')

PACKAGES = {'pve-manager': '9.2.5', 'qemu-server': '9.2.1',
            'pve-qemu-kvm': '11.0.2-2', 'systemd': '257.13-1~deb13u1'}

BINARIES = ('/usr/bin/python3', '/usr/bin/systemd-run', '/usr/bin/systemctl',
            '/usr/sbin/qm', '/usr/bin/pvesh', '/usr/sbin/pvesm',
            '/usr/bin/dpkg-query', '/usr/bin/journalctl', '/usr/bin/getfacl')

SERVICE_PROPERTIES = (
    'Type=exec', 'User=65534', 'Group=65534', 'SupplementaryGroups=',
    'Restart=no', 'TimeoutStartSec=5s', 'TimeoutStopSec=2s',
    'KillMode=control-group', 'SendSIGKILL=yes', 'UMask=0077',
    'MemoryMax=128M', 'TasksMax=16', 'CPUQuota=10%', 'LimitNOFILE=64',
    'LimitCORE=0', 'StandardInput=null', 'StandardOutput=journal',
    'StandardError=journal', 'NoNewPrivileges=yes', 'CapabilityBoundingSet=',
    'AmbientCapabilities=', 'RestrictSUIDSGID=yes', 'PrivateNetwork=yes',
    'PrivateDevices=yes', 'PrivateTmp=yes', 'ProtectSystem=strict',
    'ProtectHome=yes', 'RestrictNamespaces=yes',
    'InaccessiblePaths=-/etc/pve -/var/lib/pve-cluster -/run -/root -/home')

TIMER_PROPERTIES = ('WakeSystem=yes', 'AccuracySec=1us',
                    'RandomizedDelaySec=0', 'RemainAfterElapse=yes', 'Persistent=no')

TIMEOUT_CODE = (
    'import os,json,time; '
    'assert os.getuid()==os.geteuid()==65534 and os.getgid()==os.getegid()==65534; '
    'assert set(os.getgroups()) <= {65534}; '
    "print(json.dumps({'kind':'STAGE2_TIMEOUT_PROBE','uid':os.getuid(),'euid':os.geteuid(),"
    "'gid':os.getgid(),'egid':os.getegid(),'groups':os.getgroups(),"
    "'boottime_us':time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000}),flush=True); "
    'time.sleep(30)')

CLOCK_CODE = """import datetime,json,time
from pathlib import Path
b1=time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000
m=time.clock_gettime_ns(time.CLOCK_MONOTONIC)//1000
b2=time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
 'b1_us':b1,'monotonic_us':m,'b2_us':b2,'offset_low_us':b1-m,'offset_high_us':b2-m}))
"""

def number(x):
    return type(x) is int and x >= 0

def unit(nonce, case):
    require(type(nonce) is str and re.fullmatch('[0-9a-f]{32}', nonce), 'fresh 128-bit nonce required')
    require(case in CASES, 'unknown case')
    return 'jarvis-vm164-r3-stage2-' + nonce + '-' + case

def callback(mode='success'):
    require(mode in ('success', 'failure'), 'mode')
    return ['/usr/bin/python3', '-I', '-B', '-S', PUBLIC,
            '--approved-nonvm-callback', '--expected-source-sha256', CALLBACK_PIN, '--mode', mode]

def timer_argv(nonce, case, deadline_us):
    name = unit(nonce, case)
    require(number(deadline_us) and deadline_us > 0, 'deadline')
    command = callback('failure' if case == 'exit7' else 'success')
    if case == 'missingexec':
        command = ['/opt/jarvis-vm164-r3-stage2/absent-executable-' + nonce]
    elif case == 'missingdep':
        command = ['/usr/bin/python3', '-I', '-B', '-S', '-c',
                   'import jarvis_stage2_intentionally_absent_dependency_' + nonce]
    elif case == 'timeout':
        command = ['/usr/bin/python3', '-I', '-B', '-S', '-c', TIMEOUT_CODE]
    elif case == 'late':
        code = 'import runpy,sys,time; time.sleep(2); sys.argv=' + repr(callback()[4:]) + '; runpy.run_path(' + repr(PUBLIC) + ",run_name='__main__')"
        command = ['/usr/bin/python3', '-I', '-B', '-S', '-c', code]
    argv = ['/usr/bin/systemd-run', '--system', '--no-ask-password', '--expand-environment=no', '--unit=' + name,
            '--description=JARVIS-Stage2-' + nonce + '-' + case,
            '--on-boot=' + str(deadline_us//1_000_000) + '.' + str(deadline_us%1_000_000).zfill(6) + 's']
    argv += ['--timer-property=' + p for p in TIMER_PROPERTIES]
    if case == 'failedtimer':
        # Missing owned-namespace dependency; no dependency unit is created or stopped.
        dep = name + '-absent.service'
        argv += ['--timer-property=Requires=' + dep, '--timer-property=After=' + dep]
    argv += ['--property=' + p for p in SERVICE_PROPERTIES]
    argv += ['--property=RuntimeMaxSec=' + ('3s' if case == 'timeout' else '10s')]
    if '-c' in command:
        i=command.index('-c')+1
        command[i]="exec(bytes.fromhex('"+command[i].encode().hex()+"'))"
    return argv + ['--'] + command

def clock_domain(deadline, raw, lo, hi, documented='UNKNOWN'):
    require(all(type(x) is int for x in (deadline, raw, lo, hi)), 'integer clocks')
    require(deadline > 0 and raw > 0 and -1000 <= lo <= hi and hi-lo <= 1000, 'clock evidence invalid')
    candidates = []
    if raw == deadline:
        candidates.append('CLOCK_BOOTTIME')
    if raw+lo <= deadline <= raw+hi:
        candidates.append('CLOCK_MONOTONIC')
    # No deduction from equal clocks. An exact-version reviewed interface may resolve ambiguity.
    if len(candidates) == 1:
        require(documented in ('UNKNOWN', candidates[0]), 'documentation/observation conflict')
        return candidates[0]
    require(len(candidates) == 2 and documented in candidates, 'UNKNOWN clock convention')
    return documented

def observation_commands(nonce, case, boot_id):
    name = unit(nonce, case)
    require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',boot_id) is not None, 'boot ID')
    return {'clock': ['/usr/bin/python3','-I','-B','-S','-c',CLOCK_CODE],
            'timer': ['/usr/bin/systemctl','--system','--no-pager','show','--all',name+'.timer'],
            'service': ['/usr/bin/systemctl','--system','--no-pager','show','--all',name+'.service'],
            'journal': ['/usr/bin/journalctl','--no-pager','--output=json','--all','--boot='+boot_id,
                        '--unit='+name+'.timer','--unit='+name+'.service']}


from pathlib import Path
from common import need as require, integer, digest, boot, text, utc, sha, canonical
from local_gate import SAFE_ENV

# All are explicit assignments, including inherited-command/environment reset.
SERVICE_PROPERTIES += (
    'SetLoginEnvironment=no', 'PassEnvironment=', 'EnvironmentFile=', 'PAMName=',
    'Environment=LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/usr/sbin:/usr/bin:/sbin:/bin',
    'UnsetEnvironment=LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME PYTHONSTARTUP',
    'ExecStartPre=', 'ExecStartPost=', 'ExecStop=', 'ExecStopPost=',
    'LoadCredential=', 'LoadCredentialEncrypted=', 'ImportCredential=', 'SetCredential=',
    'OnFailure=', 'OnSuccess=')
CAPS = {'read':(10,1048576),'manual':(10,8388608),'install':(20,1048576),
        'create':(5,1048576),'duplicate':(5,1048576),'show':(5,1048576),
        'journal':(10,8388608),'cgroup':(5,1048576),'stop':(5,1048576)}


def source_hash():
    return sha(canonical({p.name:sha(p.read_bytes()) for p in sorted(Path(__file__).parent.glob('*.py'))}))


def validate_identity(record):
    require(type(record) is dict and record.get('node') == 'pve', 'host identity')
    require(record.get('packages') == PACKAGES, 'package drift')
    require(type(record.get('uid')) is int and record['uid'] == 65534 and
            type(record.get('gid')) is int and record['gid'] == 65534, 'numeric UID/GID')
    require(record.get('groups') == [65534] and record.get('nobody_processes') == [], 'unprivileged exclusive UID')
    for k in ('vm_authority_absent_review','credential_access_denied_review','binary_custody_review',
              'acl_review','source_custody_review','exclusive_operator_review','local_only_review','environment_review'):
        digest(record.get(k))
    require(record.get('source_pin') == SOURCE_PIN and record.get('callback_pin') == CALLBACK_PIN,
            'predecessor source pins')
    require(record.get('stage2_sha256') == source_hash(), 'Stage2 source pin')
    return True


def validate_session(session):
    require(type(session) is dict, 'session schema')
    unit(session.get('nonce'), 'success')
    boot(session.get('boot_id'))
    duration = (utc(session.get('expires_utc'))-utc(session.get('starts_utc'))).total_seconds()
    require(0 < duration <= 2700, 'finite 45 minute maximum')
    integer(session.get('start_boot_us'))
    lo,hi=session.get('start_offset_low_us'),session.get('start_offset_high_us')
    require(type(lo) is int and type(hi) is int and -1000 <= lo <= hi and hi-lo <= 1000, 'initial clock envelope')
    text(session.get('authorization_reference'))
    text(session.get('operator'));text(session.get('reviewer'))
    require(session['operator'] != session['reviewer'], 'independent reviewer required')
    require(session.get('stage2_sha256') == source_hash(), 'session source pin')
    require(session.get('scope') == 'STAGE2_NONVM_SUPERVISED_ONLY', 'session scope')
    return duration


def window(session, sample, *, creation=True):
    duration=validate_session(session)
    require(type(sample) is dict and boot(sample.get('boot_id')) == session['boot_id'], 'sample epoch')
    now=utc(sample.get('utc'));start=utc(session['starts_utc']);end=utc(session['expires_utc'])
    elapsed=(integer(sample.get('boot_us'))-session['start_boot_us'])/1e6
    require(start <= now < end and 0 <= elapsed < duration, 'expired or regressed clock')
    require(abs((now-start).total_seconds()-elapsed) <= 1, 'UTC/boot drift')
    lo,hi=sample.get('offset_low_us'),sample.get('offset_high_us')
    require(type(lo) is int and type(hi) is int and -1000 <= lo <= hi and hi-lo <= 1000, 'clock skew')
    require(max(hi,session['start_offset_high_us'])-min(lo,session['start_offset_low_us']) <= 1000, 'offset changed')
    remaining=min((end-now).total_seconds(),duration-elapsed)
    if creation:
        require(elapsed < 2100 and remaining >= 360, 'creation cutoff / reserve')
    return remaining


def command_envelope(argv, operation, session, sample):
    require(operation in CAPS and type(argv) is list and argv and all(type(x) is str and '\0' not in x for x in argv), 'command schema')
    left=window(session,sample,creation=operation in ('create','duplicate','install'))
    cap,limit=CAPS[operation]
    require(left >= cap+2, 'insufficient complete command budget')
    return {'kind':'INERT_COMMAND_NOT_AUTHORIZATION','argv':argv,'argv_sha256':sha(canonical(argv)),
            'timeout_s':cap,'kill_reap_reserve_s':2,'stdout_limit':limit,'stderr_limit':65536,
            'environment':dict(SAFE_ENV),'stdin':'null','shell':False,'expires_utc':session['expires_utc'],
            'deadline_boot_us':min(sample['boot_us']+(cap+2)*1000000,
                 session['start_boot_us']+int((utc(session['expires_utc'])-utc(session['starts_utc'])).total_seconds()*1e6)),
            'python_resource_caps':{'address_space_bytes':134217728,'cpu_seconds':3,'open_files':64}}


def command_receipt(envelope, receipt):
    require(type(receipt) is dict, 'receipt schema')
    require(receipt.get('argv_sha256') == envelope['argv_sha256'], 'receipt argv')
    require(receipt.get('timeout') is False and receipt.get('overflow') is False and receipt.get('signal') is None,
            'timeout/overflow/signal is not evidence success')
    integer(receipt.get('elapsed_us'),0,envelope['timeout_s']*1000000)
    for key,cap in (('raw_stdout',envelope['stdout_limit']),('raw_stderr',envelope['stderr_limit'])):
        value=receipt.get(key)
        require(type(value) is str and len(value.encode())<=cap,'missing or oversized command output')
    require(type(receipt.get('exit_code')) is int, 'missing process exit')
    return receipt['exit_code']  # caller checks exact per-case exit; nonzero is not success


def name_array(value, *, bases=False):
    require(type(value) in (list,tuple), 'unit inventory must be array')
    require(all(type(x) is str for x in value) and len(value) == len(set(value)) and len(value) <= 256, 'duplicate/invalid unit inventory')
    expression=r'jarvis-vm164-r3-stage2-[0-9a-f]{32}-(?:'+ '|'.join(CASES) +')'
    expression += '' if bases else r'(?:-absent)?\.(?:timer|service)'
    require(all(re.fullmatch(expression,x) for x in value), 'unit namespace')
    return set(value)


def plan(session, sample, case, identity, occupied=(), used=()):
    validate_identity(identity);window(session,sample)
    names=name_array(occupied);consumed=name_array(used,bases=True)
    name=unit(session['nonce'],case)
    require(name not in consumed, 'consumed generation')
    require(not {name+'.timer',name+'.service',name+'-absent.service'} & names, 'unit collision')
    deadline=sample['boot_us']+30000000
    generation=sha(canonical([session['nonce'],case,deadline]))
    result={'kind':'INERT_STAGE2_PLAN','case':case,'name':name,'timer':name+'.timer','service':name+'.service',
            'generation':generation,'deadline_boot_us':deadline,'session':dict(session),'boot_id':session['boot_id'],
            'stage2_sha256':source_hash(),'source_pin':SOURCE_PIN,'callback_pin':CALLBACK_PIN,'uid':65534,
            'description':'JARVIS-Stage2-'+session['nonce']+'-'+case,'expires_utc':session['expires_utc']}
    # ExecCondition binds/guards every payload, including missing-executable failure.
    from launch_guard import condition_property
    argv=timer_argv(session['nonce'],case,deadline)
    argv.insert(argv.index('--'), condition_property(result))
    result['argv']=argv;result['argv_sha256']=sha(canonical(argv))
    result['binding_sha256']=sha(canonical({k:v for k,v in result.items() if k!='kind'}))
    return result


def check_plan(p):
    require(type(p) is dict and p.get('kind')=='INERT_STAGE2_PLAN','plan kind')
    session=p.get('session');validate_session(session)
    name=unit(session['nonce'],p.get('case'))
    require(p.get('name')==name and p.get('timer')==name+'.timer' and p.get('service')==name+'.service','plan unit pair')
    require(boot(p.get('boot_id'))==session['boot_id'] and p.get('uid')==65534 and type(p['uid']) is int,'plan epoch/UID')
    require(p.get('stage2_sha256')==source_hash() and p.get('source_pin')==SOURCE_PIN and p.get('callback_pin')==CALLBACK_PIN,'plan pins')
    d=integer(p.get('deadline_boot_us'),1)
    require(p.get('generation')==sha(canonical([session['nonce'],p['case'],d])),'generation binding')
    require(p.get('description')=='JARVIS-Stage2-'+session['nonce']+'-'+p['case'] and p.get('expires_utc')==session['expires_utc'],'plan description/expiry')
    from launch_guard import condition_property
    argv=timer_argv(session['nonce'],p['case'],d);argv.insert(argv.index('--'),condition_property(p))
    require(p.get('argv')==argv and p.get('argv_sha256')==sha(canonical(argv)),'exact executed argv')
    require(p.get('binding_sha256')==sha(canonical({k:v for k,v in p.items() if k not in ('kind','binding_sha256')})), 'plan tampering')
    return True


def freshness(session, sample, proposal):
    check_plan(proposal);window(session,sample)
    require(session==proposal['session'],'session substitution')
    require(20000000 <= proposal['deadline_boot_us']-sample['boot_us'] <= 30000000, 'insufficient waiting-readback budget')
    return True


def outcome(case, *, callback_row=None, result=None, code=None, status=None, deadline=None, expected=None):
    require(case not in ('inactive','cancel','rearm-a','failedtimer'), 'case requires no-invocation transition proof')
    require(type(expected) is dict, 'complete expected callback binding required')
    check_plan(expected);require(expected['case']==case and expected['deadline_boot_us']==deadline,'outcome generation')
    require(type(code) is int and type(status) is int, 'numeric process exit')
    if case in ('success','exit7','late','collision','rearm-b'):
        r=callback_row or {}
        require(r.get('status')=='NON_ROOT_NON_VM_CLOCK_CANARY' and
                type(r.get('uid')) is int and r['uid']==65534 and type(r.get('euid')) is int and r['euid']==65534,
                'callback credential proof')
        require(r.get('root_boot_go') is False,'root bootstrap excluded')
        mono=integer(r.get('monotonic_us'))
        offset=integer(r.get('boottime_us'))-mono
        require(expected['session']['start_offset_low_us']-1000 <= offset <= expected['session']['start_offset_high_us']+1000,'callback clock discrepancy')
        require(boot(r.get('host_boot_id'))==expected['boot_id'] and r.get('vm_operations') is False,'callback epoch/scope')
        latency=integer(r.get('boottime_us'))-deadline
        require(latency>=0 and (latency>1000000 if case=='late' else latency<=1000000), 'callback timing')
        require(r.get('requested_mode')==('failure' if case=='exit7' else 'success'),'callback mode')
        require(code==1 and status==(7 if case=='exit7' else 0) and result==('exit-code' if case=='exit7' else 'success'),'callback process result')
    elif case=='missingexec':require((result,code,status)==('exit-code',1,203),'203/EXEC not observed')
    elif case=='missingdep':require((result,code,status)==('exit-code',1,1),'import failure not observed')
    elif case=='timeout':require(result=='timeout' and code==2 and status in (9,15),'timeout signal not observed')
    else:require(False,'unknown case')
    return 'EXPECTED_LATE_REJECTED_NOT_TIMING_PASS' if case=='late' else 'EXPECTED_OBSERVATION'


def cleanup_argv(nonce, case, owned, current):
    from binding import verify_pair
    check_plan(owned)
    require(owned['name']==unit(nonce,case),'cleanup target')
    verify_pair(owned,current)
    sample=current['sample'];window(owned['session'],sample,creation=False)
    command_envelope(['/usr/bin/systemctl','--system','--no-ask-password','stop',owned['timer']], 'stop',owned['session'],sample)
    commands=[]
    if current['timer']['ActiveState']=='active':
        commands.append(['/usr/bin/systemctl','--system','--no-ask-password','stop',owned['timer']])
    if current['service']['ActiveState']=='active' or commands:
        commands.append(['/usr/bin/systemctl','--system','--no-ask-password','stop',owned['service']])
    if not commands:
        from binding import final_inactive
        final_inactive(owned,current)
    return commands
