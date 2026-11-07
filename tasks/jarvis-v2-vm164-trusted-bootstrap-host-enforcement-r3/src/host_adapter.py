"""Future reviewed host adapter. Never constructed by default/offline CLI.

Runtime policy B has NO dispatch path. All qm operations below are VM164 only,
with no skiplock/unlock/protection/forceStop fallback. Interface semantics are
unqualified on the actual host; Stage2/3 approval and evidence are prerequisites.
"""
import datetime as dt
import os
from pathlib import Path
import re
import signal
import stat
import subprocess
import time
from model import *
import systemd_codec as codec
from preflight import assess,BINARIES,EXPECTED,PACKAGE_COMMAND,PACKAGES,runtime_packages
from store import bounded_read

SOURCE_FILES=('cli.py','host_adapter.py','model.py','preflight.py','store.py','systemd_codec.py','stage2_canary.py','sim.py')
AUTH=Path('/etc/jarvis-vm164-r3/authorization.json')
PREREQ=Path('/etc/jarvis-vm164-r3/stage2-prerequisites.json')
REVIEW=Path('/etc/jarvis-vm164-r3/review-record.json')

def source_digest(directory):
    return sha(canonical({n:sha(bounded_read(Path(directory)/n,131072)) for n in SOURCE_FILES}))

def protected(path,*,regular=False,private=False):
    p=Path(path);need(p.is_absolute(),'absolute_protected_path')
    for part in (Path('/'),*reversed(p.parents[:-1]),p):
        st=part.lstat();need(not stat.S_ISLNK(st.st_mode) and st.st_uid==0 and st.st_mode&0o022==0,'root_custody_required')
    st=p.lstat()
    if regular:need(stat.S_ISREG(st.st_mode) and st.st_nlink==1,'protected_regular_file')
    if private:need(st.st_mode&0o077==0,'private_root_artifact')
    return p

class Clock:
    def us(self):return time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000
    def utc(self):return dt.datetime.now(dt.timezone.utc)
    def offset_bounds(self):
        b1=self.us();m=time.clock_gettime_ns(time.CLOCK_MONOTONIC)//1000;b2=self.us()
        need(0<=b2-b1<=1000,'clock_sample_skew')
        return b1-m,b2-m
    @property
    def boot_id(self):return Path('/proc/sys/kernel/random/boot_id').read_text().strip()

class Permit:
    def __init__(self,approval,prereq,source):self.approval=approval;self.prereq=prereq;self.source_hash=source

def authorize(entrypoint,deadline_us=None):
    # Deny on the repository/Nexus path before executing even a read-only command.
    need(os.getuid()==os.geteuid()==0,'host_root_required')
    need(str(Path(entrypoint).absolute())==BASE+'/cli.py','reviewed_install_path_required')
    for n in SOURCE_FILES:protected(Path(BASE)/n,regular=True)
    for p in (AUTH,PREREQ,REVIEW):protected(p,regular=True,private=True)
    a=parse(bounded_read(AUTH,16384));q=parse(bounded_read(PREREQ,32768));r=parse(bounded_read(REVIEW,16384));h=source_digest(BASE)
    clock=Clock();validate_approval(a,clock.utc(),clock.boot_id,h,require_full_window=False)
    need(sha(canonical(q))==a['stage2_record_sha256'],'stage2_record_hash_mismatch')
    need(sha(canonical(r))==a['review_sha256'],'review_record_hash_mismatch')
    need(r.get('source_sha256')==h and r.get('scope')=='stage3_non_root_policy_A_only'
         and r.get('stage2_record_sha256')==a['stage2_record_sha256'],'review_record_scope_or_binding')
    need(q.get('kind')=='reviewed_stage2_host_evidence' and r.get('kind')=='reviewed_candidate_authorization_record',
         'synthetic_records_cannot_enable_host_execution')
    need(a['kind']=='reviewed_host_root' and a['policy']=='A','only_reviewed_nonroot_policy_A_runtime')
    need(os.uname().release==EXPECTED['kernel'] and Path('/etc/hostname').read_text().strip()=='pve','wrong_host')
    need(assess(q,h)['missing']==[],'stage2_prerequisites_missing')
    for n in BINARIES:
        # Distribution symlinks for system binaries are permitted only after
        # resolution; the resolved chain and its exact digest are rechecked.
        p=Path(n);st=p.lstat();need(st.st_uid==0 and (stat.S_ISLNK(st.st_mode) or st.st_mode&0o022==0),'binary_symlink_custody')
        protected(p.parent)
        resolved=p.resolve(strict=True);protected(resolved,regular=True)
        need(sha(bounded_read(resolved,32*1024*1024))==q['binaries'][n]['sha256'],'binary_pin_changed')
    protected(STATE,private=True)
    permit=Permit(a,q,h)
    raw=Runner(permit,clock,budget=5,deadline_us=deadline_us).run(PACKAGE_COMMAND,timeout=2)
    runtime_packages(raw,q['package_versions'])
    return permit

class Runner:
    def __init__(self,permit,clock=None,budget=45,deadline_us=None):
        need(isinstance(permit,Permit),'reviewed_execution_permit_required')
        self.permit=permit;self.clock=clock or Clock();self.end=self.clock.us()+budget*1_000_000
        if deadline_us is not None:self.end=min(self.end,deadline_us)
    def allowed(self,argv):
        if type(argv) is not list or not all(type(x) is str and '\0' not in x for x in argv):return False
        fixed=[['/usr/sbin/qm','start','164'],
               ['/usr/sbin/qm','shutdown','164','--timeout','15','--forceStop','0'],
               ['/usr/sbin/pvesm','path',ISO]]
        if argv in fixed or argv==PACKAGE_COMMAND:return True
        if argv in [['/usr/bin/pvesh','get','/nodes/pve/qemu/164/config','--current','1','--output-format','json'],
                    ['/usr/bin/pvesh','get','/nodes/pve/qemu/164/status/current','--output-format','json'],
                    ['/usr/bin/pvesh','get','/nodes/pve/qemu/164/pending','--output-format','json']]:return True
        if len(argv)>=4 and argv[:2]==['/usr/bin/systemctl','show']:
            return (re.fullmatch(r'jv164-r3-[0-9a-f]{32}-(grace|deadline)\.(timer|service)',argv[2]) is not None
                    and argv[3]=='--no-pager' and len(argv)==5
                    and argv[4] in ('--property='+','.join(codec.TIMER_PROPS),
                                    '--property='+','.join(codec.SERVICE_PROPS),
                                    '--property=Id,LoadState,ActiveState,SubState'))
        if len(argv)==4 and argv[:2]==['/usr/bin/systemctl','stop']:
            m=re.fullmatch(r'(jv164-r3-[0-9a-f]{32}-(?:grace|deadline))\.timer',argv[2])
            return m is not None and argv[3]==m[1]+'.service'
        if argv[:1]==['/usr/bin/systemd-run']:
            # Approve ONLY exact reconstruction of a fixed worker or canary call.
            m=next((re.fullmatch(r'--unit=jv164-r3-([0-9a-f]{32})-(grace|deadline)',x) for x in argv if x.startswith('--unit=')),None)
            if m:
                token,phase=m.groups();on=next((x for x in argv if x.startswith('--on-boot=')),None)
                if on is None:return False
                val=re.fullmatch(r'--on-boot=(\d+)\.(\d{6})s',on)
                if val is None:return False
                p={'session':token,'names':names(token),phase+'_us':int(val[1])*1_000_000+int(val[2])}
                return argv==codec.timer_command(p,phase)
            return argv==canary_command(self._canary_session(argv)) if self._canary_session(argv) else False
        return False
    @staticmethod
    def _canary_session(argv):
        for x in argv:
            m=re.fullmatch('--unit=jv164-r3-([0-9a-f]{32})-canary',x)
            if m:return m[1]
        return None
    def run(self,argv,timeout=2):
        need(self.allowed(argv),'subprocess_not_allowlisted')
        available=(self.end-self.clock.us())/1e6-1
        need(available>0,'host_command_budget_exhausted')
        p=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                           start_new_session=True,close_fds=True,
                           env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8','SYSTEMD_PAGER':''})
        try:out,err=p.communicate(timeout=min(timeout,available))
        except BaseException:
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
            try:p.communicate(timeout=1)
            except BaseException:pass
            raise
        need(len(out)<=2*1024*1024 and len(err)<=65536,'host_output_bound')
        need(p.returncode==0,'allowlisted_host_command_failed')
        return out

def canary_command(token):
    names(token)
    return ['/usr/bin/systemd-run','--unit=jv164-r3-'+token+'-canary','--wait',
            '--property=Type=exec','--property=User=root','--property=Group=root',
            '--property=Restart=no','--property=RuntimeMaxSec=10s','--property=TimeoutStopSec=2s',
            '--property=StandardOutput=journal','--property=StandardError=journal',
            '/usr/bin/python3','-I','-B','-S',BASE+'/cli.py','selfcheck','--execute-reviewed-host']

class NativeBackend:
    simulated=False
    def __init__(self,permit,clock=None,budget=45,deadline_us=None):
        self.clock=clock or Clock();self.r=Runner(permit,self.clock,budget,deadline_us)
    def snapshot(self):
        began=self.clock.us();data={}
        for field,endpoint in (('config','config'),('status','status/current'),('pending','pending')):
            argv=['/usr/bin/pvesh','get','/nodes/pve/qemu/164/'+endpoint]
            if field=='config':argv+=['--current','1']
            data[field]=parse(self.r.run(argv+['--output-format','json']))
        raw_path=self.r.run(['/usr/sbin/pvesm','path',ISO]).decode().strip()
        need('\n' not in raw_path and raw_path.startswith('/'),'iso_path_resolution')
        p=protected(raw_path,regular=True);need(p.stat().st_size==196608,'iso_size')
        iso={'volume':ISO,'sha256':sha(bounded_read(p,196608)),'bytes':p.stat().st_size,
             'config_digest':data['config'].get('digest')}
        return {'node':'pve','vmid':164,'host_boot_id':self.clock.boot_id,'began_us':began,
                'ended_us':self.clock.us(),**data,'iso':iso}
    def _show(self,n,props):
        return self.r.run(['/usr/bin/systemctl','show',n,'--no-pager','--property='+','.join(props)])
    def unit_exists(self,n):
        raw=codec.properties(self._show(n,('Id','LoadState','ActiveState','SubState')))
        need(raw.get('Id')==n,'unit_id');return raw.get('LoadState')!='not-found'
    def canary(self,plan):
        # Existing/failed canary is not replaced, collected or reset.
        # Timer namespace uniqueness is already reserved in the persistent store.
        self.r.run(canary_command(plan['session']),timeout=12);return True
    def create_timer(self,plan,phase):self.r.run(codec.timer_command(plan,phase),timeout=3)
    def unit_proof(self,plan,phase):
        n=plan['names'][phase]
        lo1,hi1=self.clock.offset_bounds()
        t=codec.timer(self._show(n+'.timer',codec.TIMER_PROPS))
        s=codec.service(self._show(n+'.service',codec.SERVICE_PROPS))
        lo2,hi2=self.clock.offset_bounds()
        t=codec.normalize_deadline(t,self.r.permit.prereq['timer_readback_clock_domain'],min(lo1,lo2),max(hi1,hi2))
        return {'timer':t,'service':s,'host_boot_id':self.clock.boot_id,'observed_us':self.clock.us()}
    def start_vm(self):self.r.run(['/usr/sbin/qm','start','164'],timeout=8)
    def graceful(self):self.r.run(['/usr/sbin/qm','shutdown','164','--timeout','15','--forceStop','0'],timeout=17)
    def force(self,_grant=None):
        # Deliberately no qm-stop allowlist entry and no enabling config switch.
        raise Refusal('FORCED_STOP_BUILD_DISABLED_SEPARATE_REVIEW_REQUIRED')
    def stop_own_units(self,plan,phase):
        n=plan['names'][phase]
        minimum=[]
        for suffix in ('.timer','.service'):
            p=codec.properties(self._show(n+suffix,('Id','LoadState','ActiveState','SubState')))
            need(p.get('Id')==n+suffix,'unit_ownership_changed');minimum.append(p)
        if all(p.get('LoadState')=='not-found' and p.get('ActiveState')=='inactive' for p in minimum):return
        # Recheck exact executable/arguments before cancelling any owned namespace.
        service=codec.service(self._show(n+'.service',codec.SERVICE_PROPS))
        need(service['id']==n+'.service' and service['argv']==worker_argv(plan['session'],phase),'unit_ownership_changed')
        self.r.run(['/usr/bin/systemctl','stop',n+'.timer',n+'.service'],timeout=7)
    def units_inactive(self,plan,phase):
        for suffix in ('.timer','.service'):
            p=codec.properties(self._show(plan['names'][phase]+suffix,('Id','LoadState','ActiveState','SubState')))
            if p.get('Id')!=plan['names'][phase]+suffix or p.get('LoadState') not in ('loaded','not-found') or p.get('ActiveState') not in ('inactive','failed'):return False
        return True
