"""VM164-only host fence policy/state machine. All effects injected.

No import-time effects. A is graceful-only and never promises expiry. B is
simulation-only in the shipped runtime adapter. Root admission is always denied.
"""
import copy
import datetime as dt
import hashlib
import json
import re

VMID=164
UUID='faeb1db8-0df9-482d-b3e4-f6ccc1602193'
DISK='downloads:164/vm-164-disk-0.raw'
SERIAL='g6k164-12821f6b54a2'
ISO='local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso'
ISO_SHA='fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154'
BASE='/opt/jarvis-vm164-host-fence-r3'
STATE='/var/lib/jarvis-vm164-host-fence-r3'
GRACE_US=540_000_000
DEADLINE_US=600_000_000
STOP_BY_US=630_000_000
MAX_START_DELAY_US=15_000_000
MAX_LATENESS_US=1_000_000
UUID_RE=r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
PHASES=('grace','deadline')
FORCE_RUNTIME_ENABLED=False
REQUIRED={'name','smbios1','scsi0','ide2','boot','hotplug','agent','onboot','protection',
          'serial0','vga','bios','machine','digest','cores','sockets','memory','balloon'}
OPTIONAL={'scsihw','cpu','ostype','numa','meta','description','tags','lock','template'}

class Refusal(ValueError):pass
class Busy(Refusal):pass

def need(ok,reason):
    if not ok:raise Refusal(reason)

def canonical(d):return json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(b):return hashlib.sha256(b).hexdigest()
def integer(n):return type(n) is int and n>=0

def parse(raw,limit=2*1024*1024):
    need(type(raw) in (str,bytes) and len(raw)<=limit,'input_bound')
    def pairs(rows):
        d={}
        for k,v in rows:need(k not in d,'duplicate_json_key');d[k]=v
        return d
    def bad(_):raise Refusal('nonfinite_json')
    try:return json.loads(raw,object_pairs_hook=pairs,parse_constant=bad)
    except (UnicodeError,json.JSONDecodeError,RecursionError) as exc:raise Refusal('malformed_json') from exc

def intlike(x):
    need(type(x) in (int,str) and re.fullmatch(r'0|[1-9][0-9]{0,8}',str(x)) is not None,'integer_schema')
    return int(x)

def stamp(s):
    need(type(s) is str and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ',s) is not None,'utc_timestamp')
    try:return dt.datetime.strptime(s,'%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)
    except ValueError as exc:raise Refusal('invalid_utc') from exc

def validate_snapshot(s,now_us,boot_id,*,digest=None,status=None):
    need(type(s) is dict,'snapshot_schema')
    need(s.get('node')=='pve' and type(s.get('vmid')) is int and s['vmid']==VMID,'wrong_node_or_vmid')
    need(s.get('host_boot_id')==boot_id and re.fullmatch(UUID_RE,boot_id or '') is not None,'host_boot_changed')
    need(integer(now_us) and integer(s.get('began_us')) and integer(s.get('ended_us'))
         and s['began_us']<=s['ended_us']<=now_us and now_us-s['began_us']<=10_000_000
         and s['ended_us']-s['began_us']<=7_000_000,'stale_or_nonatomic_readback')
    c=s.get('config');need(type(c) is dict and REQUIRED<=c.keys() and c.keys()<=REQUIRED|OPTIONAL,'missing_or_extra_hardware')
    need(c['name']=='jarvis-g6k-clean-164' and c['smbios1']=='uuid='+UUID,'wrong_name_or_uuid')
    need(c['bios']=='seabios' and c['machine']=='q35','bios_or_machine')
    need(c['boot']=='order=scsi0' and intlike(c['hotplug'])==0 and intlike(c['onboot'])==0
         and intlike(c['protection'])==1,'boot_or_protection')
    need(type(c['agent']) in (int,str) and c['agent'] in (0,'0','enabled=0'),'guest_agent')
    need(c['serial0']=='socket' and c['vga']=='std' and not c.get('lock') and not c.get('template'),'console_lock_or_template')
    need(c['ide2']==ISO+',media=cdrom','wrong_or_missing_iso')
    need(type(c['digest']) is str and re.fullmatch('[0-9a-f]{40}',c['digest']) is not None,'config_digest')
    need(digest is None or c['digest']==digest,'config_digest_changed')
    need(type(c['scsi0']) is str,'disk_schema');parts=c['scsi0'].split(',');need(parts[0]==DISK,'wrong_disk')
    options={}
    for part in parts[1:]:
        need(part.count('=')==1,'disk_option_schema');k,v=part.split('=')
        need(k not in options,'duplicate_disk_option');options[k]=v
    need(options.get('serial')==SERIAL and options.get('size')=='64G','disk_serial_or_size')
    need(options.keys()<={'serial','size','cache','iothread','aio','backup','discard','ssd','detect_zeroes'},'extra_disk_option')
    need(4<=intlike(c['cores'])*intlike(c['sockets'])<=256 and 6000<=intlike(c['memory'])<=1048576
         and intlike(c['balloon'])==0,'resources')
    st=s.get('status');need(type(st) is dict and type(st.get('vmid')) is int and st['vmid']==VMID
                          and st.get('status') in ('running','stopped'),'status_schema_or_vmid')
    need(status is None or st['status']==status,'unexpected_vm_status')
    pending=s.get('pending');need(type(pending) is list and len(pending)<=256,'pending_schema');seen=set()
    for row in pending:
        need(type(row) is dict and set(row)=={'key','value'},'pending_or_malformed_row')
        k=row['key'];need(type(k) is str and k in c and k not in seen and type(row['value']) is type(c[k])
                          and row['value']==c[k],'pending_current_mismatch');seen.add(k)
    media=s.get('iso');need(type(media) is dict and media.get('volume')==ISO and media.get('sha256')==ISO_SHA
                            and type(media.get('bytes')) is int and media['bytes']==196608
                            and media.get('config_digest')==c['digest'],'iso_custody_binding')
    return sha(canonical(c))

def validate_approval(a,now_utc,boot_id,source_hash,*,require_full_window=True):
    required={'format','kind','policy','stage','purpose','operator_reference','review_sha256','source_sha256',
              'host_boot_id','issued_at','expires_at','stage2_record_sha256','command_contract_reviewed',
              'forced_stop_authorization'}
    need(type(a) is dict and set(a)==required,'approval_schema')
    need(a['format']=='vm164-r3-reviewed-authorization' and a['kind'] in ('synthetic','reviewed_host_root'),'approval_kind')
    need(a['policy'] in ('A','B') and type(a['stage']) is int and a['stage']==3
         and a['purpose']=='non_root_vm164_qualification','no_root_authorization')
    need(re.fullmatch('[A-Za-z0-9_.:-]{1,100}',a['operator_reference'] or '') is not None,'operator_reference')
    for k in ('review_sha256','source_sha256','stage2_record_sha256'):
        need(type(a[k]) is str and re.fullmatch('[0-9a-f]{64}',a[k]) is not None,'review_or_source_pin')
    need(a['source_sha256']==source_hash and a['host_boot_id']==boot_id,'approval_binding')
    start=stamp(a['issued_at']);end=stamp(a['expires_at'])
    need(start<=now_utc<end and (end-start).total_seconds()<=3600,'stale_or_short_approval')
    if require_full_window:
        need((end-now_utc).total_seconds()>=STOP_BY_US/1e6+15,'stale_or_short_approval')
    need(a['command_contract_reviewed'] is True,'pve_command_contract_unqualified')
    if a['policy']=='A':need(a['forced_stop_authorization'] is None,'A_cannot_force')
    else:
        b=a['forced_stop_authorization']
        need(type(b) is dict and set(b)=={'policy','vmid','review_sha256','accepts_disk_loss','explicit_forced_termination'}
             and b['policy']=='B' and type(b['vmid']) is int and b['vmid']==VMID
             and b['accepts_disk_loss'] is True and b['explicit_forced_termination'] is True
             and re.fullmatch('[0-9a-f]{64}',b['review_sha256'] or '') is not None,'separate_B_authorization_required')
    return sha(canonical(a))

def names(session):
    need(type(session) is str and re.fullmatch('[0-9a-f]{32}',session) is not None,'session_nonce')
    return {p:f'jv164-r3-{session}-{p}' for p in PHASES}

def worker_argv(session,phase):
    need(phase in PHASES,'phase');names(session)
    return ['/usr/bin/python3','-I','-B','-S',BASE+'/cli.py','worker','--session',session,
            '--phase',phase,'--execute-reviewed-host']

def verify_unit(plan,phase,proof,now_us):
    n=plan['names'][phase];deadline=plan[phase+'_us'];t=proof.get('timer',{});s=proof.get('service',{})
    need(proof.get('host_boot_id')==plan['host_boot_id'],'unit_host_binding')
    need(all(integer(t.get(k)) for k in ('accuracy_us','random_us','last_trigger_us','on_boot_us','next_us',
                                       'next_boot_min_us','next_boot_max_us')),'timer_numeric_schema')
    need(integer(proof.get('observed_us')) and plan['armed_us']<=proof['observed_us']<=now_us
         and now_us-proof['observed_us']<=3_000_000,'unit_proof_stale')
    need(t.get('id')==n+'.timer' and s.get('id')==n+'.service','unit_identity')
    need(t.get('transient') is True and s.get('transient') is True,'not_transient')
    need(t.get('load')=='loaded' and t.get('active')=='active' and t.get('sub')=='waiting'
         and t.get('result')=='success' and t.get('trigger')==n+'.service','timer_inactive_or_failed')
    need(t.get('wake') is True and t.get('accuracy_us')==1 and t.get('random_us')==0
         and t.get('last_trigger_us')==0 and t.get('remain') is True,'timer_parameters_or_pre_firing')
    need(t.get('on_boot_us')==deadline and t.get('readback_clock') in ('CLOCK_MONOTONIC','CLOCK_BOOTTIME')
         and t['next_boot_min_us']<=deadline<=t['next_boot_max_us']
         and t['next_boot_max_us']-t['next_boot_min_us']<=1000
         and now_us<deadline,'wrong_or_late_deadline')
    lo=t.get('readback_offset_low_us');hi=t.get('readback_offset_high_us')
    need(type(lo) is int and type(hi) is int and -1000<=lo<=hi and hi-lo<=1000
         and t['next_boot_min_us']==max(0,t['next_us']+lo)
         and t['next_boot_max_us']==max(0,t['next_us']+hi)
         and (t['readback_clock']!='CLOCK_BOOTTIME' or lo==hi==0),'clock_conversion_inconsistent')
    need(s.get('load')=='loaded' and s.get('active')=='inactive' and s.get('sub')=='dead'
         and s.get('result')=='success' and s.get('type')=='exec','service_not_ready')
    need(s.get('argv')==worker_argv(plan['session'],phase) and s.get('user')=='root'
         and s.get('group')=='root' and s.get('restart')=='no' and s.get('kill_mode')=='control-group'
         and s.get('runtime_us')==(45_000_000 if phase=='grace' else 30_000_000)
         and s.get('stop_timeout_us')==5_000_000 and s.get('extra_commands') is False,
         'service_execution_contract')
    need(s.get('umask')=='0077' and s.get('memory_max')=='134217728' and s.get('tasks_max')=='16'
         and s.get('send_sigkill') is True and s.get('stdin')=='null' and s.get('stdout')=='journal'
         and s.get('stderr')=='journal' and s.get('start_timeout_us')==10_000_000,'service_resource_or_stdio_contract')
    return True

class Engine:
    def __init__(self,backend,store,clock,source_hash,*,expected_session=None,expected_approval_sha256=None):
        self.b=backend;self.s=store;self.clock=clock;self.source_hash=source_hash
        self.expected_session=expected_session;self.expected_approval_sha256=expected_approval_sha256
    def _plan(self):
        plan=self.s.plan();need(plan.get('source_sha256')==self.source_hash,'session_source_changed')
        need(self.expected_session is None or plan.get('session')==self.expected_session,'stale_worker_session')
        need(self.expected_approval_sha256 is None or plan.get('approval_sha256')==self.expected_approval_sha256,'session_approval_changed')
        self.s.bind(plan['session'])
        return plan
    def snapshot(self,plan=None,status=None):
        x=self.b.snapshot();validate_snapshot(x,self.clock.us(),self.clock.boot_id,
                    digest=plan['digest'] if plan else None,status=status)
        if plan:need(sha(canonical(x['config']))==plan['config_sha256'],'configuration_changed')
        return x
    def prepare(self,approval,session):
        validate_approval(approval,self.clock.utc(),self.clock.boot_id,self.source_hash)
        if not self.b.simulated:need(approval['policy']=='A','B_runtime_disabled')
        x=self.snapshot(status='stopped');armed=self.clock.us()
        plan={'session':session,'names':names(session),'host_boot_id':self.clock.boot_id,'armed_us':armed,
              'grace_us':armed+GRACE_US,'deadline_us':armed+DEADLINE_US,'stop_by_us':armed+STOP_BY_US,
              'digest':x['config']['digest'],'config_sha256':sha(canonical(x['config'])),
              'approval_sha256':sha(canonical(approval)),'policy':approval['policy'],'source_sha256':self.source_hash}
        plan['force_grant_sha256']=sha(canonical(approval['forced_stop_authorization'])) if approval['policy']=='B' else None
        self.s.create(plan)
        attempted=[];created=[]
        try:
            for p in PHASES:
                need(not self.b.unit_exists(plan['names'][p]+'.timer') and not self.b.unit_exists(plan['names'][p]+'.service'),'unit_collision')
            need(self.b.canary(plan) is True,'exec_canary_failed')
            for p in PHASES:
                attempted.append(p);self.b.create_timer(plan,p);created.append(p)
            for p in PHASES:verify_unit(plan,p,self.b.unit_proof(plan,p),self.clock.us())
            self.snapshot(plan,status='stopped')
            need(self.clock.us()-armed<=MAX_START_DELAY_US,'arming_too_slow_no_start')
            self.s.event('ARMED',{'canary_executed':True})
        except BaseException:
            orphan=False
            for p in attempted:
                try:
                    self.b.stop_own_units(plan,p)
                    need(self.b.units_inactive(plan,p),'setup_rollback_unverified')
                except BaseException:orphan=True
            self.s.best_effort('SETUP_FAILED_NO_START',{'owned_unit_cancellation_verified':not orphan,
                                                      'orphan_or_unknown_units':orphan})
            raise
        return self.receipt(plan,'ARMED_NOT_TERMINATION_PROOF')
    def start(self):
        plan=self._plan();need(self.s.phase()=='ARMED','duplicate_or_unarmed_start')
        need(self.clock.boot_id==plan['host_boot_id'] and plan['armed_us']<=self.clock.us()<=plan['armed_us']+MAX_START_DELAY_US,'stale_arm_or_host_reboot')
        self.snapshot(plan,status='stopped')
        for p in PHASES:verify_unit(plan,p,self.b.unit_proof(plan,p),self.clock.us())
        # Persist BEFORE start: interrupted/lost ack cannot authorize a duplicate.
        self.s.event('START_REQUESTED',{})
        try:self.b.start_vm()
        except BaseException:
            self.s.best_effort('START_UNKNOWN_KEEP_FENCE',{});raise
        try:
            self.snapshot(plan,status='running');self.s.event('ACTIVE',{})
        except BaseException:
            self.s.best_effort('START_UNKNOWN_KEEP_FENCE',{});raise
        return self.receipt(plan,'START_ACK_NOT_ROOT_AUTHORITY')
    def expire(self,phase):
        plan=self._plan();need(phase in PHASES,'phase')
        need(self.clock.boot_id==plan['host_boot_id'],'host_reboot_fence_invalid')
        if self.s.phase() in ('CLOSED','CLOSING'):return self.receipt(plan,'ALREADY_CLOSED_NO_ACTION')
        now=self.clock.us();need(now>=plan[phase+'_us'],'early_worker')
        need(self.s.is_armed(),'not_armed')
        late=now>plan[phase+'_us']+MAX_LATENESS_US
        try:x=self.snapshot(plan)
        except BaseException:
            self.s.best_effort('IDENTITY_OR_INTERFACE_BLOCKER',{});raise
        if not self.s.claim(phase):return self.receipt(plan,'DUPLICATE_WORKER_NO_ACTION')
        terminal=False
        try:
            self.s.best_effort('WORKER_'+phase.upper(),{'late':late})
            if x['status']['status']=='stopped':
                terminal=True;self.s.best_effort('STOPPED_OBSERVED',{'late':late})
                return self.receipt(plan,'STOPPED_LATE' if late else 'STOPPED_OBSERVED')
            if phase=='grace':action='graceful'
            elif plan['policy']=='A':
                terminal=True;self.s.best_effort('POLICY_A_BLOCKER_NO_FORCE',{'late':late})
                return self.receipt(plan,'POLICY_A_NO_EXPIRATION_GUARANTEE')
            else:
                need(self.b.simulated or FORCE_RUNTIME_ENABLED,'B_runtime_disabled');action='force'
            # No unlogged actuation. A full/corrupt evidence store is a blocker,
            # explicitly another reason this build cannot promise hard expiry.
            self.s.event('ACTION_INTENT',{'action':action,'vmid':VMID})
            error=False
            try:self.b.graceful() if action=='graceful' else self.b.force(plan['force_grant_sha256'])
            except BaseException:error=True
            try:after=self.snapshot(plan)
            except BaseException:
                self.s.best_effort('POST_ACTION_OBSERVATION_FAILED',{});raise
            stopped=after['status']['status']=='stopped'
            self.s.best_effort('STOPPED_OBSERVED' if stopped else 'TERMINATION_UNPROVEN',
                              {'action':action,'command_error':error,'late':late,'observed_us':self.clock.us()})
            if stopped:
                terminal=True
                return self.receipt(plan,'STOPPED_LATE' if late or self.clock.us()>plan['stop_by_us'] else 'STOPPED_OBSERVED')
            return self.receipt(plan,'TERMINATION_UNPROVEN')
        finally:self.s.release(phase,terminal)
    def cleanup(self):
        plan=self._plan()
        if self.s.phase()=='CLOSED':return self.receipt(plan,'ALREADY_CLOSED_NO_ACTION')
        self.snapshot(plan,status='stopped')
        # Cancellation is forbidden while running, including after a lost ack.
        self.s.event('CLOSING',{})
        for phase in PHASES:
            self.b.stop_own_units(plan,phase)
            need(self.b.units_inactive(plan,phase),'cleanup_incomplete')
        self.s.assert_workers_idle()
        self.snapshot(plan,status='stopped');self.s.event('CLOSED',{})
        return self.receipt(plan,'CLOSED_EVIDENCE_RETAINED')
    def retire(self,new_approval):
        plan=self._plan();need(self.s.phase()=='CLOSED','closed_session_required_for_retire')
        validate_approval(new_approval,self.clock.utc(),self.clock.boot_id,self.source_hash)
        need(sha(canonical(new_approval))!=plan['approval_sha256'],'new_finite_approval_required')
        self.snapshot(plan,status='stopped')
        for p in PHASES:need(self.b.units_inactive(plan,p),'cannot_retire_live_units')
        self.s.assert_workers_idle()
        self.s.event('RETIRED',{'new_approval_sha256':sha(canonical(new_approval))})
        result=self.receipt(plan,'RETIRED_REGISTRY_EVIDENCE_PRESERVED');self.s.retire()
        return result
    def verify(self):
        plan=self._plan();self.snapshot(plan)
        for p in PHASES:verify_unit(plan,p,self.b.unit_proof(plan,p),self.clock.us())
        return self.receipt(plan,'READBACK_CONSISTENCY_ONLY')
    def observe(self):
        plan=self._plan();snapshot=self.snapshot(plan)
        observations={}
        for phase in PHASES:
            proof=self.b.unit_proof(plan,phase)
            need(proof.get('host_boot_id')==plan['host_boot_id'],'observation_host_changed')
            need(proof['timer']['id']==plan['names'][phase]+'.timer'
                 and proof['service']['id']==plan['names'][phase]+'.service','observation_unit_changed')
            observations[phase]=proof
        r=self.receipt(plan,'OBSERVATION_NOT_QUALIFICATION')
        r.update(observed_vm_status=snapshot['status']['status'],units=observations)
        return r
    def receipt(self,plan,status):
        return {'status':status,'session':plan['session'],'policy':plan['policy'],
                'phase':self.s.phase(),'simulated':self.b.simulated,
                'evidence_healthy':self.s.healthy,'root_boot_go':False,
                'live_qualification':False,'installation_qualified':False,
                'expiration_guaranteed':False,'forced_stop_runtime_enabled':False}
