"""Pure offline argv/predicate library. Never executes emitted host commands."""
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
            '/usr/bin/dpkg-query', '/usr/bin/journalctl', '/usr/bin/getent',
            '/usr/bin/id', '/usr/bin/getfacl', '/usr/bin/sudo')
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

def require(ok, message):
    if not ok:
        raise ValueError(message)


def number(x):
    return type(x) is int and x >= 0


def utc(value):
    require(type(value) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ', value), 'explicit UTC required')
    return dt.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)


def unit(nonce, case):
    require(type(nonce) is str and re.fullmatch('[0-9a-f]{32}', nonce), 'fresh 128-bit nonce required')
    require(case in CASES, 'unknown case')
    return 'jarvis-vm164-r3-stage2-' + nonce + '-' + case


def validate_identity(record):
    require(record.get('node') == 'pve', 'host mismatch')
    require(record.get('packages') == PACKAGES, 'package drift')
    require(type(record.get('uid')) is int and record['uid'] == 65534, 'UID must be 65534')
    require(type(record.get('gid')) is int and record['gid'] == 65534, 'GID must be 65534')
    require(record.get('groups') == [65534], 'supplementary membership blocks')
    require(record.get('nobody_processes') == [] and type(record.get('nobody_processes')) is list, 'UID shared or unknown')
    for key in ('vm_authority_absent_review', 'credential_access_denied_review', 'binary_custody_review',
                'acl_review', 'source_custody_review', 'exclusive_operator_review'):
        require(type(record.get(key)) is str and re.fullmatch('[0-9a-f]{64}', record[key]), 'missing evidence digest: ' + key)
    require(record.get('source_pin') == SOURCE_PIN and record.get('callback_pin') == CALLBACK_PIN, 'source pin mismatch')
    # Digests bind evidence; they do NOT establish truth, completeness or authorization.
    return True


def window(session, sample, *, creation=True):
    start, end, now = (utc(session['starts_utc']), utc(session['expires_utc']), utc(sample['utc']))
    duration = (end-start).total_seconds()
    require(0 < duration <= 2700, 'maximum 45 minutes')
    require(start <= now < end, 'expired or not begun')
    require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}', session['boot_id']) is not None,
            'boot ID required')
    require(sample['boot_id'] == session['boot_id'], 'boot changed')
    for k in ('boot_us', 'offset_low_us', 'offset_high_us'):
        require(type(sample[k]) is int, 'integer clock required')
    require(number(session['start_boot_us']) and sample['boot_us'] >= session['start_boot_us'], 'clock regression')
    elapsed = (sample['boot_us']-session['start_boot_us'])/1e6
    require(elapsed < duration, 'boot session expired')
    require(abs((now-start).total_seconds()-elapsed) <= 1, 'UTC/boot drift')
    lo, hi = sample['offset_low_us'], sample['offset_high_us']
    require(-1000 <= lo <= hi and hi-lo <= 1000, 'clock skew')
    require(type(session['start_offset_low_us']) is int and type(session['start_offset_high_us']) is int,
            'initial offset missing')
    require(-1000 <= session['start_offset_low_us'] <= session['start_offset_high_us'], 'initial offset invalid')
    require(max(hi, session['start_offset_high_us'])-min(lo, session['start_offset_low_us']) <= 1000,
            'suspend or offset change')
    left = min((end-now).total_seconds(), duration-elapsed)
    if creation:
        require(elapsed < 2100 and left >= 360, 'creation closed; cleanup reserve')
    return left


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
    argv = ['/usr/bin/systemd-run', '--system', '--no-ask-password', '--unit=' + name,
            '--description=JARVIS-Stage2-' + nonce + '-' + case,
            '--on-boot=' + str(deadline_us//1_000_000) + '.' + str(deadline_us%1_000_000).zfill(6) + 's']
    argv += ['--timer-property=' + p for p in TIMER_PROPERTIES]
    if case == 'failedtimer':
        # Missing owned-namespace dependency; no dependency unit is created or stopped.
        dep = name + '-absent.service'
        argv += ['--timer-property=Requires=' + dep, '--timer-property=After=' + dep]
    argv += ['--property=' + p for p in SERVICE_PROPERTIES]
    argv += ['--property=RuntimeMaxSec=' + ('3s' if case == 'timeout' else '10s')]
    return argv + ['--'] + command


def plan(session, sample, case, identity, occupied=(), used=()):
    validate_identity(identity)
    left = window(session, sample)
    name = unit(session['nonce'], case)
    require(name not in used, 'case already consumed; no retry')
    names = {name + '.timer', name + '.service'}
    if case == 'failedtimer':
        names.add(name + '-absent.service')
    require(not names.intersection(occupied), 'collision: do not touch existing units')
    deadline = sample['boot_us'] + 30_000_000
    require(left > 30 + 10 + 5 + 2 + 300, 'insufficient cleanup reserve')
    return {'kind': 'NON_EXECUTING_PROPOSAL_NOT_AUTHORIZATION', 'case': case,
            'name': name, 'deadline_boot_us': deadline, 'expires_utc': session['expires_utc'],
            'argv': timer_argv(session['nonce'], case, deadline)}


def freshness(session, sample, proposal):
    window(session, sample)
    require(proposal['expires_utc'] == session['expires_utc'], 'expiry changed')
    require(proposal['name'] == unit(session['nonce'], proposal['case']), 'name changed')
    require(proposal['argv'] == timer_argv(session['nonce'], proposal['case'], proposal['deadline_boot_us']), 'argv changed')
    require(5_000_000 <= proposal['deadline_boot_us']-sample['boot_us'] <= 30_000_000, 'stale proposal')
    return True


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


def waiting(timer, service, deadline, domain, lo, hi, now):
    require(domain in ('CLOCK_MONOTONIC', 'CLOCK_BOOTTIME'), 'UNKNOWN fails')
    require(timer['load'] == 'loaded' and timer['active'] == 'active' and timer['sub'] == 'waiting'
            and timer['result'] == 'success' and timer['last_trigger_us'] == 0, 'failed/inactive/fired timer')
    require(service['active'] == 'inactive' and service['sub'] == 'dead' and service['result'] == 'success', 'service not ready')
    require(timer['on_boot_us'] == deadline and now < deadline, 'late/configuration mismatch')
    require(clock_domain(deadline, timer['next_us'], lo, hi, domain) == domain, 'domain mismatch')
    return True


def outcome(case, *, callback_row=None, result=None, code=None, status=None, deadline=None):
    require(case in CASES, 'unknown case')
    if case in ('success','exit7','late','rearm-a','rearm-b'):
        r = callback_row or {}
        require(r.get('status') == 'NON_ROOT_NON_VM_CLOCK_CANARY' and
                type(r.get('uid')) is int and r['uid'] == 65534 and
                type(r.get('euid')) is int and r['euid'] == 65534 and r.get('vm_operations') is False,
                'unproven callback')
        require(number(deadline) and number(r.get('boottime_us')), 'missing deadline')
        latency = r['boottime_us']-deadline
        require(latency >= 0, 'early callback')
        require(r.get('requested_mode') == ('failure' if case == 'exit7' else 'success'), 'mode')
        require(code == 1 and status == (7 if case == 'exit7' else 0), 'exit mismatch')
        require(result == ('exit-code' if case == 'exit7' else 'success'), 'result mismatch')
        if case == 'late':
            require(latency > 1_000_000, 'late case did not become late')
            return 'EXPECTED_LATE_REJECTED_NOT_TIMING_PASS'
        require(latency <= 1_000_000, 'late firing')
        return 'EXPECTED_OBSERVATION'
    if case == 'timeout':
        require(result == 'timeout' and code in (2,3), 'timeout not observed')
    elif case == 'missingexec':
        require(result == 'exit-code' and code == 1 and status == 203, 'exec failure unproven')
    elif case == 'missingdep':
        require(result == 'exit-code' and code == 1 and status == 1, 'dependency failure unproven')
    else:
        raise ValueError('manual raw-state comparison required; no automatic PASS')
    return 'EXPECTED_OBSERVATION'


def cleanup_argv(nonce, case, owned, current):
    name = unit(nonce, case)
    require(owned.get('name') == name and owned.get('argv') == current.get('argv') and
            owned.get('boot_id') == current.get('boot_id') and owned.get('description') == current.get('description')
            and owned.get('description') == 'JARVIS-Stage2-' + nonce + '-' + case,
            'ownership unproven; quarantine')
    require(owned.get('argv') == timer_argv(nonce, case, owned.get('deadline_boot_us')), 'owned argv invalid')
    require(current.get('states') in (['inactive','inactive'], ['inactive','failed'], ['active','inactive'],
                                     ['active','active'], ['inactive','active'], ['failed','active'], ['failed','inactive'], ['failed','failed'], ['active','failed']),
            'unknown/transitioning state')
    if current['states'] in (['inactive','inactive'], ['inactive','failed'], ['failed','inactive'], ['failed','failed']):
        return []
    commands = []
    if current['states'][0] == 'active':
        commands.append(['/usr/bin/systemctl','--system','--no-ask-password','stop',name+'.timer'])
    if current['states'][1] == 'active' or current['states'][0] == 'active':
        commands.append(['/usr/bin/systemctl','--system','--no-ask-password','stop',name+'.service'])
    return commands


def observation_commands(nonce, case, boot_id):
    name = unit(nonce, case)
    require(re.fullmatch(r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}',boot_id) is not None, 'boot ID')
    return {'clock': ['/usr/bin/python3','-I','-B','-S','-c',CLOCK_CODE],
            'timer': ['/usr/bin/systemctl','--system','--no-pager','show','--all',name+'.timer'],
            'service': ['/usr/bin/systemctl','--system','--no-pager','show','--all',name+'.service'],
            'journal': ['/usr/bin/journalctl','--no-pager','--output=json','--all','--boot='+boot_id,
                        '--unit='+name+'.timer','--unit='+name+'.service']}
