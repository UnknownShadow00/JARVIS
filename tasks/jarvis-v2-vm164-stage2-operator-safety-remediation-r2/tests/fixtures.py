"""SYNTHETIC ONLY. Never use these values as host evidence or authorization."""
import copy,datetime as dt,json
import packet as p
import binding as b
import results
from common import canonical,sha
from launch_guard import condition_argv,guard_binding

def session():
 return dict(nonce='b'*32,boot_id='abcdefab-1234-5678-9abc-123456789abc',starts_utc='2031-02-03T10:00:00Z',expires_utc='2031-02-03T10:45:00Z',start_boot_us=8000000000,start_offset_low_us=11999900,start_offset_high_us=12000100,authorization_reference='SYNTHETIC-NOT-AUTHORIZED',operator='SYNTHETIC-OPERATOR',reviewer='SYNTHETIC-REVIEWER',stage2_sha256=p.source_hash(),scope='STAGE2_NONVM_SUPERVISED_ONLY')
def sample(seconds=120):
 s=session();return dict(boot_id=s['boot_id'],utc=(dt.datetime(2031,2,3,10,tzinfo=dt.timezone.utc)+dt.timedelta(seconds=seconds)).strftime('%Y-%m-%dT%H:%M:%SZ'),boot_us=s['start_boot_us']+seconds*1000000,offset_low_us=11999900,offset_high_us=12000100)
def ident():
 return dict(node='pve',uid=65534,gid=65534,groups=[65534],nobody_processes=[],packages=p.PACKAGES,source_pin=p.SOURCE_PIN,callback_pin=p.CALLBACK_PIN,stage2_sha256=p.source_hash(),**{k:'d'*64 for k in ('vm_authority_absent_review','credential_access_denied_review','binary_custody_review','acl_review','source_custody_review','exclusive_operator_review','local_only_review','environment_review')})
def execution(argv):return '{ path='+argv[0]+' ; argv[]='+' '.join(argv)+' ; ignore_errors=no ; start_time=[] ; stop_time=[] ; pid=0 ; code=(null) ; status=0 }'
def raw(d):return ''.join(k+'='+v+'\n' for k,v in sorted(d.items()))
def sync(o):
 o['raw_timer']=raw(o['timer']);o['raw_service']=raw(o['service'])
 if 'capture_receipts' in o:
  for k in ('timer','service'):o['capture_receipts'][k]['raw_stdout']=o['raw_'+k]
 return o

def observation(plan,seconds=121,states=('active','inactive'),invoked=False):
 t={k:'' for k in b.TIMER_REQUIRED};s={k:'' for k in b.SERVICE_REQUIRED}
 for item,name,state in ((t,plan['timer'],states[0]),(s,plan['service'],states[1])):
  item.update(Id=name,LoadState='loaded',ActiveState=state,SubState=('waiting' if item is t else 'running') if state=='active' else ('failed' if state=='failed' else 'dead'),Transient='yes',Description=plan['description'],Result='success',Job='0')
 d=plan['deadline_boot_us'];nextdue=d-12000000
 t.update(Unit=plan['service'],WakeSystem='yes',AccuracyUSec='1',RandomizedDelayUSec='0',RemainAfterElapse='yes',Persistent='no',TimersMonotonic='{ OnBootUSec='+str(d)+' ; next_elapse='+str(nextdue)+' }',NextElapseUSecMonotonic=str(nextdue),LastTriggerUSecMonotonic=str(nextdue if invoked else 0))
 s.update(Type='exec',User='65534',Group='65534',Restart='no',KillMode='control-group',SendSIGKILL='yes',StandardInput='null',StandardOutput='journal',StandardError='journal',UMask='0077',NoNewPrivileges='yes',MemoryMax='134217728',TasksMax='16',PrivateNetwork='yes',PrivateDevices='yes',PrivateTmp='yes',ProtectSystem='strict',ProtectHome='yes',RestrictNamespaces='yes',RestrictSUIDSGID='yes',SetLoginEnvironment='no',LimitNOFILE='64',LimitCORE='0',RuntimeMaxUSec='3000000' if plan['case']=='timeout' else '10000000',TimeoutStartUSec='5000000',TimeoutStopUSec='2000000',CPUQuotaPerSecUSec='100000',Environment='LANG=C.UTF-8 LC_ALL=C.UTF-8 PATH=/usr/sbin:/usr/bin:/sbin:/bin',InaccessiblePaths='-/etc/pve -/var/lib/pve-cluster -/run -/root -/home',UnsetEnvironment='LD_PRELOAD LD_LIBRARY_PATH LD_AUDIT PYTHONPATH PYTHONHOME PYTHONSTARTUP',MainPID='0',ControlPID='0',ControlGroup='/system.slice/'+plan['service'],InvocationID=sha(plan['case'].encode())[:32] if invoked else '',ExecMainCode='1' if invoked else '0',ExecMainStatus='0',ExecStart=execution(plan['argv'][plan['argv'].index('--')+1:]),ExecCondition=execution(condition_argv(plan)))
 o=dict(name=plan['name'],boot_id=plan['boot_id'],binding_sha256=plan['binding_sha256'],generation=plan['generation'],argv=copy.deepcopy(plan['argv']),sample=sample(seconds),observed_boot_us=sample(seconds)['boot_us'],timer=t,service=s,cgroup=dict(path='/sys/fs/cgroup/system.slice/'+plan['service'],populated=0,pids=[],complete=True,absent=False))
 sync(o)
 commands=p.observation_commands(plan['session']['nonce'],plan['case'],plan['boot_id']);o['capture_receipts']={}
 for role in ('timer','service','clock'):
  rec=receipt(plan,'read' if role=='clock' else 'show',commands[role],seconds)
  rec['raw_stdout']=o['raw_'+role] if role!='clock' else json.dumps(dict(boot_id=plan['boot_id'],utc=o['sample']['utc'].replace('Z','.000100+00:00'),b1_us=o['sample']['boot_us']-200,b2_us=o['sample']['boot_us'],monotonic_us=o['sample']['boot_us']-12000100,offset_low_us=11999900,offset_high_us=12000100))
  o['capture_receipts'][role]=rec
 return o

class LegacyFixture(dict):
 """Upgrade audit input fixtures only; all 30 original test assertions unchanged."""
 def __setitem__(self,k,v):
  if k=='states':
   for field,state in zip(('timer','service'),v):
    self[field]['ActiveState']=state;self[field]['SubState']=('waiting' if field=='timer' else 'running') if state=='active' else ('failed' if state=='failed' else 'dead')
   sync(self)
  else:super().__setitem__(k,v)
def ownership():
 plan=p.plan(session(),sample(),'success',ident());return plan,LegacyFixture(observation(plan,states=('active','active')))
def receipt(plan,op,argv,seconds,code=0):
 return dict(operation=op,argv=argv,sample=sample(seconds),argv_sha256=sha(canonical(argv)),timeout=False,overflow=False,signal=None,elapsed_us=1000,exit_code=code,raw_stdout='SYNTHETIC-COMMAND-RECEIPT',raw_stderr='')
def collision_proof(plan,start):
 paths=['/run/systemd/transient','/etc/systemd/system']
 proof=dict(boot_id=plan['boot_id'],sample=sample(start),unit_paths=paths,unit_paths_complete=True,namespace_inventory=[],units={})
 for unit in (plan['timer'],plan['service'],plan['name']+'-absent.service'):
  proof['units'][unit]=dict(raw_show=raw(dict(Id=unit,Names=unit,LoadState='not-found',ActiveState='inactive',SubState='dead',Job='0',FragmentPath='',SourcePath='',Transient='no')),show_exit=1,files={path+'/'+unit:dict(absent=True,errno='ENOENT') for path in paths})
 return proof

def record():
 r=dict(kind='SYNTHETIC_STAGE2_R2_RESULT',packet_manifest_sha256='e'*64,stage2_sha256=p.source_hash(),source_pin=p.SOURCE_PIN,callback_pin=p.CALLBACK_PIN,session=session(),identity=ident(),operator=session()['operator'],independent_reviewer=session()['reviewer'],authorization_reference=session()['authorization_reference'],expiration_guaranteed=False,live_qualification=False,result='LIMITED_OBSERVATIONS_REVIEWED',failures=[],clock_domain='CLOCK_MONOTONIC',clock_domain_basis_sha256='c'*64,closure=sample(1000),cases={})
 for index,case in enumerate(p.CASES):
  start=120+index*60;plan=p.plan(session(),sample(start),case,ident());noexec=case in ('cancel','inactive','rearm-a','failedtimer')
  row=dict(plan=plan,collision_preflight=collision_proof(plan,start),status=results.EXPECTED[case],failures=[],waiting=[] if case=='failedtimer' else [observation(plan,start+1),observation(plan,start+2)],final=observation(plan,1000,('inactive','inactive'),not noexec),events=[],journal_interval=dict(complete=True,boot_id=plan['boot_id'],unit=plan['service'],from_boot_us=sample(start)['boot_us'],through_boot_us=sample(1000)['boot_us']),receipts=[receipt(plan,'create',plan['argv'],start)],cleanup_complete=True)
  row['receipts'] += [receipt(plan,'stop',['/usr/bin/systemctl','--system','--no-ask-password','stop',u],start+5 if noexec else start+45) for u in (plan['timer'],plan['service'])]
  if noexec:
   row['cancel_boot_us']=sample(start+5)['boot_us']
   if case=='failedtimer':
    row['timer_failure']=observation(plan,start+1,('failed','inactive'));row['timer_failure']['timer']['Result']='resources';sync(row['timer_failure'])
  else:
   s=row['final']['service'];s['ExecMainStatus']='7' if case=='exit7' else '203' if case=='missingexec' else '1' if case=='missingdep' else '15' if case=='timeout' else '0';s['Result']='exit-code' if case in ('exit7','missingexec','missingdep') else 'timeout' if case=='timeout' else 'success';s['ExecMainCode']='2' if case=='timeout' else '1'
   guard=dict(kind='STAGE2_GUARD_R2',binding=guard_binding(plan),invocation_id=s['InvocationID'],uid=65534,euid=65534,gid=65534,egid=65534,groups=[65534],boottime_us=plan['deadline_boot_us'])
   bodies=[guard]
   if case=='timeout':bodies.append(dict(kind='STAGE2_TIMEOUT_PROBE',uid=65534,euid=65534,gid=65534,egid=65534,groups=[65534],boottime_us=plan['deadline_boot_us']))
   if case in ('success','exit7','late','collision','rearm-b'):
    bodies.append(dict(status='NON_ROOT_NON_VM_CLOCK_CANARY',uid=65534,euid=65534,vm_operations=False,root_boot_go=False,host_boot_id=plan['boot_id'],boottime_us=plan['deadline_boot_us']+(2000000 if case=='late' else 100),monotonic_us=plan['deadline_boot_us']+(2000000 if case=='late' else 100)-12000000,requested_mode='failure' if case=='exit7' else 'success'))
   row['events']=[dict(boot_id=plan['boot_id'],unit=plan['service'],invocation_id=s['InvocationID'],uid=65534,cursor=case+str(i),payload=x) for i,x in enumerate(bodies)]
   sync(row['final'])
  if case=='collision':
   row.update(collision_before=observation(plan,start+2),collision_after=observation(plan,start+3))
   row['receipts'].insert(1,receipt(plan,'duplicate',plan['argv'],start+2,1))
  row['raw_journal']=''.join(json.dumps(dict(_BOOT_ID=plan['boot_id'].replace('-',''),_SYSTEMD_UNIT=e['unit'],_SYSTEMD_INVOCATION_ID=e['invocation_id'],_UID='65534',__CURSOR=e['cursor'],__MONOTONIC_TIMESTAMP=str(plan['deadline_boot_us']-12000000),MESSAGE=json.dumps(e['payload'])))+'\n' for e in row['events'])
  if case in ('missingexec','missingdep'):
   message='EXEC failure' if case=='missingexec' else 'ModuleNotFoundError: jarvis_stage2_intentionally_absent_dependency_'+session()['nonce']
   row['raw_journal']+=json.dumps(dict(_BOOT_ID=plan['boot_id'].replace('-',''),_SYSTEMD_UNIT=plan['service'],__CURSOR=case+'-diagnostic',MESSAGE=message))+'\n'
  row['journal_receipt']=receipt(plan,'journal',p.observation_commands(session()['nonce'],case,session()['boot_id'])['journal'],1000)
  row['journal_receipt']['raw_stdout']=row['raw_journal']
  r['cases'][case]=row
 return seal(r)
def seal(r):
 artifacts={'cases/'+c+'.json':canonical(row) for c,row in r['cases'].items()}
 r['evidence_manifest']={name:dict(sha256=sha(raw),bytes=len(raw)) for name,raw in artifacts.items()};r['evidence_manifest_sha256']=sha(canonical(r['evidence_manifest']))
 return r,artifacts
