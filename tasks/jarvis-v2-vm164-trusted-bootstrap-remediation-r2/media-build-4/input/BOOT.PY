"""VM164 r2 diagnostic/cleanup CANDIDATE. Nothing executes at import.

No host expiry implementation here. Host prearmed, qualified expiry is mandatory
before a separately authorized root boot. Attached media is reported truthfully;
this diagnostic can NEVER qualify installation. Do not use the old BOOT.PY.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import sys
import time

UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL='g6k164-12821f6b54a2'
PROBE_SHA='08eae2a8a9056cb75419e03d066eb6631e1d41ba21e65f2583a2a0f4d3c6931a'
RAM=Path('/run/vm164-bootstrap-r2')
PYTHON='/usr/bin/python3.14'
WORK_BUDGET=60
STEP_BUDGET=5
KILL_REAP_BUDGET=1
POWEROFF_RESERVE=6
UNIT_START_LIMIT=90
UNIT_STOP_LIMIT=5
OPS={
    'mask':['/usr/bin/systemctl','mask','--runtime','debug-shell.service'],
    'stop':['/usr/bin/systemctl','stop','debug-shell.service'],
    'kill':['/usr/bin/systemctl','kill','--kill-whom=all','--signal=KILL','debug-shell.service'],
    'poweroff':['/usr/bin/systemctl','--no-block','poweroff'],
}
class Refusal(ValueError):
    pass

def need(ok,reason):
    if not ok:raise Refusal(reason)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def read_regular(path,limit=65536):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        st=os.fstat(fd)
        need(stat.S_ISREG(st.st_mode) and st.st_nlink==1 and st.st_size<=limit,'regular_bounded_single_link')
        raw=os.read(fd,limit+1);after=os.fstat(fd)
        need(len(raw)==st.st_size and (st.st_ino,st.st_size,st.st_mtime_ns,st.st_ctime_ns)==
             (after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns),'input_changed')
        return raw
    finally:os.close(fd)

def write_new(path,raw):
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    with os.fdopen(fd,'wb') as f:f.write(raw)

def identity():
    # Called in a bounded child. No state file, timer or broad snapshot dependency.
    need(Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()==UUID,'wrong_uuid')
    need(Path('/sys/block/sda/device/serial').read_text().strip()==SERIAL,'wrong_serial')
    need(int(Path('/sys/block/sda/size').read_text().strip())*512==64*1024**3,'wrong_disk_size')
    need(os.getuid()==os.geteuid()==0 and Path('/proc/1/comm').read_text().strip()=='systemd','root_systemd_required')
    return {'verified':True,'uuid':UUID,'serial':SERIAL,'disk_bytes':64*1024**3,
            'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}

def valid_identity(d):
    return (type(d) is dict and d.get('verified') is True and d.get('uuid')==UUID
            and d.get('serial')==SERIAL and type(d.get('disk_bytes')) is int
            and d['disk_bytes']==64*1024**3 and type(d.get('boot_id')) is str
            and re.fullmatch('[0-9a-f-]{36}',d['boot_id']) is not None)

def close_session(backend):
    """All post-identity failures attempt termination. Wrong/unknown target: no action.

    SIGKILL/manager death cannot run finally: only the independent host fence
    can cover those cases. This result never claims that the VM actually stopped.
    """
    result={'target_verified':False,'guest_closure_observed':False,
            'poweroff_requested':False,'vm_stopped_verified':False,
            'external_fence_must_remain_armed':True,'errors':[]}
    try:
        target=backend.call('identity')
        need(valid_identity(target),'identity_not_verified')
    except BaseException:
        result['errors'].append('identity_unverified_no_guest_actions')
        return result
    result['target_verified']=True
    try:
        try:
            validated=backend.call('validate')
            need(type(validated) is dict and validated.get('valid') is True,'invalid_state_receipt')
        except BaseException:
            result['errors'].append('state_or_snapshot_validation_failed')
    finally:
        # No state/snapshot/receipt/console precondition can bypass these attempts.
        try:
            for action in ('mask','stop','kill','inspect'):
                try:
                    observed=backend.call(action)
                    if action=='inspect':
                        need(type(observed) is dict and observed.get('closed') is True,'closure_not_verified')
                        result['guest_closure_observed']=True
                except BaseException:
                    result['errors'].append(action+'_failed_or_timed_out')
            try:
                backend.call('emit',result)
            except BaseException:
                result['errors'].append('receipt_failed')
        finally:
            try:
                backend.call('poweroff')
                result['poweroff_requested']=True
            except BaseException:
                result['errors'].append('poweroff_failed_or_timed_out')
    return result

class GuestRunner:
    """Future guest adapter. Tests MUST replace Popen; never used in offline CLI."""
    def __init__(self,clock=time.monotonic):
        self.clock=clock;self.deadline=clock()+WORK_BUDGET
        self.script=str(Path(__file__).resolve())
    def call(self,action,value=None):
        reserve=0 if action=='poweroff' else POWEROFF_RESERVE
        available=self.deadline-self.clock()-reserve-KILL_REAP_BUDGET
        need(available>0,'deadline_exhausted')
        timeout=min(STEP_BUDGET,available)
        argv=OPS.get(action)
        if argv is None:
            need(action in ('identity','validate','inspect','emit'),'fixed_action_only')
            argv=[PYTHON,'-I','-B','-S',self.script,'child',action]
            if action=='emit':argv.append(json.dumps(value,separators=(',',':')))
        proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,start_new_session=True,
                              env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8'})
        try:
            out,err=proc.communicate(timeout=timeout)
        except BaseException:
            # New process group: kill child AND descendants on timeout/interruption.
            try:os.killpg(proc.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            try:proc.communicate(timeout=KILL_REAP_BUDGET)
            except BaseException:pass
            raise
        need(proc.returncode==0 and len(out)<=65536 and len(err)<=65536,'bounded_fixed_command_failed')
        if action in ('identity','validate','inspect'):return json.loads(out)
        return None

def child(action,data=None):
    if action=='identity':return identity()
    if action=='validate':
        d=identity();s=json.loads(read_regular(RAM/'SESSION.json'))
        need(s['identity']==d and s['probe_sha256']==PROBE_SHA,'session_or_probe_binding')
        return {'valid':True}
    if action=='inspect':
        # Outer runner kills this child process group, including systemctl, if hung.
        r=subprocess.run(['/usr/bin/systemctl','show','debug-shell.service','-p','ActiveState',
                          '-p','MainPID','-p','UnitFileState','-p','ControlGroup'],
                         stdin=subprocess.DEVNULL,capture_output=True,timeout=3,check=True)
        props=dict(x.split('=',1) for x in r.stdout.decode().splitlines() if '=' in x)
        need(Path('/sys/fs/cgroup/cgroup.controllers').is_file()
             and Path('/proc/1/cgroup').read_text().strip() in ('0::/','0::/init.scope'),'cgroup_view')
        need(props.get('ControlGroup') in ('','/system.slice/debug-shell.service'),'unexpected_cgroup')
        cg=Path('/sys/fs/cgroup/system.slice/debug-shell.service/cgroup.procs')
        empty=not cg.exists() or not cg.read_text().strip()
        return {'closed':props.get('ActiveState') in ('inactive','failed')
                and props.get('MainPID')=='0' and props.get('UnitFileState')=='masked-runtime' and empty}
    if action=='emit':
        identity();raw=(json.dumps(json.loads(data),sort_keys=True)+'\n').encode()
        fd=os.open('/dev/tty1',os.O_WRONLY|os.O_NOCTTY|os.O_NOFOLLOW|os.O_CLOEXEC)
        try:
            st=os.fstat(fd);need(stat.S_ISCHR(st.st_mode) and os.major(st.st_rdev)==4
                                and os.minor(st.st_rdev)==1,'VGA_device')
            need(os.write(fd,raw)==len(raw),'short_console_write')
        finally:os.close(fd)
        return None
    raise Refusal('child_action')

def submit_close():
    # Submission/identity failures still leave the independently armed HOST fence.
    runner=GuestRunner();need(valid_identity(runner.call('identity')),'identity_required')
    argv=['/usr/bin/systemd-run','--unit=vm164-bootstrap-close-r2',
          '--property=Type=oneshot','--property=Restart=no',
          '--property=TimeoutStartSec=90s','--property=TimeoutStopSec=5s',
          '--property=KillMode=control-group','--property=SendSIGKILL=yes',
          '--property=MemoryMax=96M','--property=TasksMax=16','--property=UMask=0077',
          '--property=StandardInput=null','--property=StandardOutput=journal',
          '--property=StandardError=journal',PYTHON,'-I','-B','-S',runner.script,'close-unit']
    subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,timeout=5,check=True)
    print('CLOSE_SUBMITTED_NOT_CLOSURE_PROOF; KEEP_HOST_FENCE_ARMED')

def diagnostic_probe():
    d=identity();need(os.ttyname(0)=='/dev/tty1','supervised_VGA_required')
    rows=[x.split() for x in Path('/proc/self/mountinfo').read_text().splitlines()]
    for row in rows:
        row[4]=re.sub(r'\\(040|011|012|134)',lambda m:chr(int(m[1],8)),row[4])
    need(any(r[4]=='/run' and r[r.index('-')+1]=='tmpfs' for r in rows),'RAM_required')
    medium=Path(__file__).resolve().parent
    need(any(r[4]==str(medium) and r[r.index('-')+1]=='iso9660'
             and {'ro','nosuid','nodev','noexec'}<=set(r[5].split(',')) for r in rows),'read_only_verified_media')
    raw=read_regular(medium/'LABPKG.PY');need(sha(raw)==PROBE_SHA,'unchanged_probe_pin')
    os.mkdir(RAM,0o700)
    write_new(RAM/'SESSION.json',(json.dumps({'identity':d,'probe_sha256':PROBE_SHA})+'\n').encode())
    r=subprocess.run([PYTHON,'-I','-B','-S',str(medium/'LABPKG.PY'),'probe'],
                     stdin=subprocess.DEVNULL,capture_output=True,timeout=15)
    write_new(RAM/'PROBE.JSON',r.stdout)
    need(r.returncode==0,'probe_failed_raw_output_preserved')
    p=json.loads(r.stdout)
    need(p.get('format')=='vm164-readonly-probe-v1' and p.get('vm_uuid')==UUID
         and p.get('boot_id')==d['boot_id'] and p.get('disk_serial')==SERIAL
         and type(p.get('disk_bytes')) is int and p['disk_bytes']==64*1024**3
         and p.get('optical_media_present') is True,
         'diagnostic_identity_or_expected_media')
    write_new(RAM/'DIAGNOSTIC.json',(json.dumps({'format':'vm164-r2-attached-diagnostic',
        'raw_probe_sha256':sha(r.stdout),'optical_media_present':True,
        'installation_qualified':False,'guest_report_is_independent_attestation':False})+'\n').encode())
    print('DIAGNOSTIC_ONLY_MEDIA_ATTACHED; INSTALLATION_NO_GO; SHA256='+sha(r.stdout))

def pages(page):
    raw=read_regular(RAM/'PROBE.JSON');encoded=base64.b64encode(raw).decode()
    rows=[encoded[i:i+48] for i in range(0,len(encoded),48)]
    need(type(page) is int and 0<=page<(len(rows)+7)//8,'page_bound')
    print(f'PAGE {page+1}/{(len(rows)+7)//8} SHA256={sha(raw)}')
    for i in range(page*8,min((page+1)*8,len(rows))):print(f'R{i:04d}:'+rows[i])

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['probe','page','close','close-unit','child'])
    p.add_argument('argument',nargs='?');p.add_argument('data',nargs='?')
    p.add_argument('--execute-supervised-guest',action='store_true')
    a=p.parse_args()
    # Internal bounded children/close-unit inherit this authorization via their
    # fixed caller; root can already control the guest. This is not host authority.
    need(a.execute_supervised_guest or a.action in ('child','close-unit'),'explicit_guest_execution_required')
    if a.action=='probe':diagnostic_probe()
    elif a.action=='page':pages(int(a.argument or 0))
    elif a.action=='close':submit_close()
    elif a.action=='close-unit':
        r=close_session(GuestRunner());print(json.dumps(r));return 0 if r['guest_closure_observed'] and r['poweroff_requested'] and not r['errors'] else 1
    else:
        r=child(a.argument,a.data)
        if r is not None:print(json.dumps(r))
    return 0
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as exc:
        print(json.dumps({'status':'INCOMPLETE_KEEP_HOST_FENCE_ARMED','reason':type(exc).__name__,
                          'vm_stopped_verified':False,'installation_qualified':False}))
        raise SystemExit(1)
