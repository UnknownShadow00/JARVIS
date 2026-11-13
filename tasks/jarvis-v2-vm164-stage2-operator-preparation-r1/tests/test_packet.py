"""All input records here are SYNTHETIC. No host subprocess/network execution."""
import ast
import copy
import datetime as dt
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import packet as p
import proposals

def identity():
 return {'node':'pve','packages':p.PACKAGES.copy(),'uid':65534,'gid':65534,'groups':[65534],
 'nobody_processes':[],'source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
 **{k:'f'*64 for k in ('vm_authority_absent_review','credential_access_denied_review','binary_custody_review',
 'acl_review','source_custody_review','exclusive_operator_review')}}

def session():
 return {'nonce':'a'*32,'boot_id':'12345678-1234-1234-1234-123456789abc','starts_utc':'2030-01-01T00:00:00Z',
 'expires_utc':'2030-01-01T00:45:00Z','start_boot_us':1_000_000_000,'start_offset_low_us':49_999_900,'start_offset_high_us':50_000_100}

def sample():
 return {'utc':'2030-01-01T00:01:00Z','boot_id':session()['boot_id'],'boot_us':1_060_000_000,
 'offset_low_us':49_999_900,'offset_high_us':50_000_100}

class Arguments(unittest.TestCase):
 def test_all_cases_bounded_nonroot(self):
  for c in p.CASES:
   with self.subTest(case=c):
    a=p.plan(session(),sample(),c,identity())['argv']
    for v in ('--system','--no-ask-password','--property=User=65534','--property=Group=65534','--property=Type=exec',
              '--timer-property=WakeSystem=yes','--property=Restart=no','--property=NoNewPrivileges=yes',
              '--property=CapabilityBoundingSet=','--property=ProtectSystem=strict','--property=MemoryMax=128M',
              '--property=TasksMax=16','--property=KillMode=control-group'):
     self.assertIn(v,a)
    self.assertNotIn('--collect',a);self.assertNotIn('--wait',a)
    self.assertTrue(a[a.index('--')+1].startswith('/'))
 def test_absolute_uptime_not_relative(self):
  a=p.plan(session(),sample(),'success',identity())
  self.assertEqual(a['deadline_boot_us'],1_090_000_000)
  self.assertIn('--on-boot=1090.000000s',a['argv'])
 def test_subsecond_precision(self):
  self.assertIn('--on-boot=1000.000123s',p.timer_argv('a'*32,'success',1_000_000_123))
 def test_pinned_callback(self):
  a=p.plan(session(),sample(),'success',identity())['argv'];self.assertEqual(a[a.index('--')+1:],p.callback())
 def test_mode7(self):self.assertEqual(p.callback('failure')[-1],'failure')
 def test_no_worker_or_vm_commands(self):
  for c in p.CASES:
   a=p.timer_argv('a'*32,c,1000)
   self.assertFalse(any('host-fence' in x or x in ('/usr/sbin/qm','/usr/bin/pvesh','--execute-reviewed-host') for x in a))
 def test_inline_code_compiles(self):
  for c in ('timeout','late','missingdep'):
   a=p.timer_argv('a'*32,c,1000);ast.parse(a[-1])
 def test_timeout_is_three_seconds(self):self.assertIn('--property=RuntimeMaxSec=3s',p.timer_argv('a'*32,'timeout',1000))
 def test_invalid_cases(self):
  for c in ('','success; reboot','deadline','grace','../x'):
   with self.assertRaises(ValueError):p.unit('a'*32,c)
 def test_invalid_nonce(self):
  for n in ('a'*31,'A'*32,'a'*33,'../x','a'*31+';','--all',None):
   with self.assertRaises(ValueError):p.unit(n,'success')
 def test_names_unique(self):self.assertEqual(len({p.unit('a'*32,c) for c in p.CASES}),len(p.CASES))
 def test_foreign_namespace(self):self.assertNotEqual(p.unit('a'*32,'success'),'jv164-r3-'+'a'*32+'-grace')
 def test_collision_each_suffix(self):
  for suffix in ('.timer','.service','-absent.service'):
   with self.assertRaises(ValueError):p.plan(session(),sample(),'failedtimer',identity(),occupied=[p.unit('a'*32,'failedtimer')+suffix])
 def test_reuse_denied(self):
  with self.assertRaises(ValueError):p.plan(session(),sample(),'success',identity(),used=[p.unit('a'*32,'success')])
 def test_distinct_rearm(self):
  a=p.plan(session(),sample(),'rearm-a',identity());b=p.plan(session(),sample(),'rearm-b',identity())
  self.assertNotEqual(a['name'],b['name']);self.assertEqual(a['expires_utc'],b['expires_utc'])

class UID(unittest.TestCase):
 def test_valid_is_consistency_only(self):self.assertTrue(p.validate_identity(identity()))
 def test_root_and_other_ids(self):
  for field in ('uid','gid'):
   for value in (0,1,'65534',True,None):
    i=identity();i[field]=value
    with self.assertRaises(ValueError):p.validate_identity(i)
 def test_extra_groups(self):
  for groups in ([65534,0],[65534,34],[],None):
   i=identity();i['groups']=groups
   with self.assertRaises(ValueError):p.validate_identity(i)
 def test_processes_unknown_or_present(self):
  for value in (None,[123],False):
   i=identity();i['nobody_processes']=value
   with self.assertRaises(ValueError):p.validate_identity(i)
 def test_review_evidence_required(self):
  for field in [k for k in identity() if k.endswith('_review')]:
   for value in (None,True,'UNKNOWN',''):
    i=identity();i[field]=value
    with self.assertRaises(ValueError):p.validate_identity(i)
 def test_pins_packages_node_drift(self):
  for field in ('source_pin','callback_pin','packages','node'):
   i=identity();i[field]=None
   with self.assertRaises(ValueError):p.validate_identity(i)

class Deadline(unittest.TestCase):
 def test_window_valid(self):self.assertEqual(p.window(session(),sample()),2640)
 def test_expiry_mandatory(self):
  s=session();s['expires_utc']=None
  with self.assertRaises(ValueError):p.window(s,sample())
 def test_over_45_minutes(self):
  s=session();s['expires_utc']='2030-01-01T00:45:01Z'
  with self.assertRaises(ValueError):p.window(s,sample())
 def test_exact_expiry_denies(self):
  x=sample();x.update(utc=session()['expires_utc'],boot_us=session()['start_boot_us']+2_700_000_000)
  with self.assertRaises(ValueError):p.window(session(),x)
 def test_wall_clock_backward_or_forward(self):
  for t in ('2029-12-31T23:59:59Z','2030-01-01T00:03:00Z'):
   x=sample();x['utc']=t
   with self.assertRaises(ValueError):p.window(session(),x)
 def test_boot_regression(self):
  x=sample();x['boot_us']=0
  with self.assertRaises(ValueError):p.window(session(),x)
 def test_boot_change(self):
  x=sample();x['boot_id']='0'*36
  with self.assertRaises(ValueError):p.window(session(),x)
 def test_35_minute_creation_stop(self):
  x=sample();x.update(utc='2030-01-01T00:35:00Z',boot_us=3_100_000_000)
  with self.assertRaises(ValueError):p.window(session(),x)
  self.assertEqual(p.window(session(),x,creation=False),600)
 def test_suspend_offset_change(self):
  x=sample();x['offset_high_us']+=10000
  with self.assertRaises(ValueError):p.window(session(),x)
 def test_freshness(self):
  a=p.plan(session(),sample(),'success',identity());self.assertTrue(p.freshness(session(),sample(),a))
 def test_stale_argv(self):
  a=p.plan(session(),sample(),'success',identity());x=sample();x.update(utc='2030-01-01T00:01:26Z',boot_us=x['boot_us']+26_000_000)
  with self.assertRaises(ValueError):p.freshness(session(),x,a)
 def test_altered_command_denied(self):
  a=p.plan(session(),sample(),'success',identity());a['argv'].append('--collect')
  with self.assertRaises(ValueError):p.freshness(session(),sample(),a)

class Clock(unittest.TestCase):
 def test_historical_suspend_monotonic(self):self.assertEqual(p.clock_domain(100_000_000,50_000_000,49_999_900,50_000_100),'CLOCK_MONOTONIC')
 def test_historical_suspend_boottime(self):self.assertEqual(p.clock_domain(100_000_000,100_000_000,49_999_900,50_000_100),'CLOCK_BOOTTIME')
 def test_equal_clocks_unknown(self):
  with self.assertRaises(ValueError):p.clock_domain(100,100,-1,1)
 def test_documented_ambiguity_resolution(self):self.assertEqual(p.clock_domain(100,100,-1,1,'CLOCK_MONOTONIC'),'CLOCK_MONOTONIC')
 def test_doc_conflict(self):
  with self.assertRaises(ValueError):p.clock_domain(100_000_000,50_000_000,49_999_900,50_000_100,'CLOCK_BOOTTIME')
 def test_bad_samples(self):
  for args in ((100,0,0,0),(100,100,5,2),(100,100,0,1001),(100,100,'0',0)):
   with self.assertRaises(ValueError):p.clock_domain(*args)
 def test_waiting_negative_states(self):
  t={'load':'loaded','active':'active','sub':'waiting','result':'success','last_trigger_us':0,'on_boot_us':100_000_000,'next_us':50_000_000}
  s={'active':'inactive','sub':'dead','result':'success'}
  self.assertTrue(p.waiting(t,s,100_000_000,'CLOCK_MONOTONIC',49_999_900,50_000_100,99_000_000))
  for key,value in (('load','not-found'),('active','failed'),('active','inactive'),('sub','elapsed'),('result','resources'),('last_trigger_us',1),('on_boot_us',0)):
   bad=t.copy();bad[key]=value
   with self.assertRaises(ValueError):p.waiting(bad,s,100_000_000,'CLOCK_MONOTONIC',49_999_900,50_000_100,99_000_000)
 def test_unknown_never_passes(self):
  with self.assertRaises(ValueError):p.waiting({}, {},100,'UNKNOWN',0,0,0)

class Failures(unittest.TestCase):
 def row(self):return {'status':'NON_ROOT_NON_VM_CLOCK_CANARY','uid':65534,'euid':65534,'vm_operations':False,'boottime_us':100_000_100,'requested_mode':'success'}
 def test_success_and_exit7(self):
  self.assertEqual(p.outcome('success',callback_row=self.row(),result='success',code=1,status=0,deadline=100_000_000),'EXPECTED_OBSERVATION')
  r=self.row();r['requested_mode']='failure'
  self.assertEqual(p.outcome('exit7',callback_row=r,result='exit-code',code=1,status=7,deadline=100_000_000),'EXPECTED_OBSERVATION')
 def test_late_rejected_for_success(self):
  r=self.row();r['boottime_us']+=2_000_000
  with self.assertRaises(ValueError):p.outcome('success',callback_row=r,result='success',code=1,status=0,deadline=100_000_000)
  self.assertEqual(p.outcome('late',callback_row=r,result='success',code=1,status=0,deadline=100_000_000),'EXPECTED_LATE_REJECTED_NOT_TIMING_PASS')
 def test_early_rejected(self):
  with self.assertRaises(ValueError):p.outcome('success',callback_row=self.row(),result='success',code=1,status=0,deadline=100_000_101)
 def test_root_callback_rejected(self):
  r=self.row();r['euid']=0
  with self.assertRaises(ValueError):p.outcome('success',callback_row=r,result='success',code=1,status=0,deadline=100_000_000)
 def test_exit_mismatch(self):
  with self.assertRaises(ValueError):p.outcome('success',callback_row=self.row(),result='success',code=1,status=7,deadline=100_000_000)
 def test_expected_failures(self):
  for case,result,code,status in (('timeout','timeout',2,15),('missingexec','exit-code',1,203),('missingdep','exit-code',1,1)):
   self.assertEqual(p.outcome(case,result=result,code=code,status=status),'EXPECTED_OBSERVATION')
 def test_missing_exec_ack_not_proof(self):
  with self.assertRaises(ValueError):p.outcome('missingexec',result='success',code=0,status=0)
 def test_no_fake_manual_pass(self):
  for c in ('collision','cancel','inactive','failedtimer'):
   with self.assertRaises(ValueError):p.outcome(c,result='success')

class Cleanup(unittest.TestCase):
 def records(self):
  a=p.plan(session(),sample(),'success',identity());a.update(boot_id=session()['boot_id'],description='JARVIS-Stage2-'+'a'*32+'-success')
  b=copy.deepcopy(a);b['states']=['active','inactive'];return a,b
 def test_exact_only_timer_then_service(self):
  a,b=self.records();cmd=p.cleanup_argv('a'*32,'success',a,b)
  self.assertEqual(cmd[0][-1],a['name']+'.timer');self.assertEqual(cmd[1][-1],a['name']+'.service')
  self.assertNotIn('*',str(cmd));self.assertNotIn('reset-failed',str(cmd))
 def test_idempotence_failed_retained(self):
  a,b=self.records()
  for states in (['inactive','inactive'],['inactive','failed'],['failed','failed']):
   b['states']=states;self.assertEqual(p.cleanup_argv('a'*32,'success',a,b),[])
 def test_interrupted_cleanup_resumes_service_only(self):
  a,b=self.records();b['states']=['inactive','active']
  self.assertEqual(p.cleanup_argv('a'*32,'success',a,b),[['/usr/bin/systemctl','--system','--no-ask-password','stop',a['name']+'.service']])
 def test_unknown_owner_no_stop(self):
  a,b=self.records();b['description']='foreign'
  with self.assertRaises(ValueError):p.cleanup_argv('a'*32,'success',a,b)
 def test_changed_argv_no_stop(self):
  a,b=self.records();b['argv'].append('unknown')
  with self.assertRaises(ValueError):p.cleanup_argv('a'*32,'success',a,b)
 def test_changed_boot_no_stop(self):
  a,b=self.records();b['boot_id']='different'
  with self.assertRaises(ValueError):p.cleanup_argv('a'*32,'success',a,b)
 def test_transition_unknown_no_success(self):
  a,b=self.records();b['states']=['deactivating','active']
  with self.assertRaises(ValueError):p.cleanup_argv('a'*32,'success',a,b)

class SourceSafety(unittest.TestCase):
 def test_pure_library_no_execution_imports(self):
  tree=ast.parse((ROOT/'src/packet.py').read_text())
  mods={n.names[0].name for n in ast.walk(tree) if isinstance(n,ast.Import)}
  self.assertEqual(mods,{'datetime','json','re'})
 def test_install_code_static_guards(self):
  ast.parse(proposals.INSTALL_CODE)
  for token in ('os.O_EXCL','os.O_NOFOLLOW','dir_fd=','os.fsync','os.mkdir','os.geteuid()!=0',p.CALLBACK_PIN):self.assertIn(token,proposals.INSTALL_CODE)
  for token in ('unlink','rmtree','replace(','chown(','subprocess','socket'):self.assertNotIn(token,proposals.INSTALL_CODE)
 def test_all_proposal_code_parses(self):
  for name,value in vars(proposals).items():
   if name.endswith('_CODE'):ast.parse(value)
 def test_original_canary_uid_restriction(self):
  original=ROOT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src/stage2_canary.py'
  spec=importlib.util.spec_from_file_location('sealed_canary',original);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
  for uid,euid in ((0,0),(65534,0),(0,65534)):
   with patch.object(sys,'argv',['canary.py','--approved-nonvm-callback']),patch.object(m.os,'getuid',return_value=uid),patch.object(m.os,'geteuid',return_value=euid):
    with self.assertRaisesRegex(ValueError,'must_not_be_root'):m.main()
 def test_r3_codec_unknown_and_offset(self):
  sealed=ROOT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src'
  sys.path.insert(0,str(sealed))
  import systemd_codec as codec
  with self.assertRaises(ValueError):codec.normalize_deadline({'next_us':50},'UNKNOWN',0,0)
  got=codec.normalize_deadline({'next_us':50_000_000},'CLOCK_MONOTONIC',49_999_900,50_000_100)
  self.assertLessEqual(got['next_boot_min_us'],100_000_000);self.assertGreaterEqual(got['next_boot_max_us'],100_000_000)

class ResultRecords(unittest.TestCase):
 def record(self):
  return {'kind':'CAPTURED_STAGE2_LIMITED_RESULT','source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
  'expiration_guaranteed':False,'live_qualification':False,'result':'INCOMPLETE','session':session(),
  'cases':{c:{'status':'NOT_RUN'} for c in p.CASES},
  'unqualified':['manager_reexec','host_reboot','physical_suspend_wake','VM_termination','root_bootstrap']}
 def test_truthful_incomplete(self):
  from results import validate
  self.assertFalse(validate(self.record())['authenticity_verified'])
 def test_missing_raw_evidence(self):
  from results import validate
  r=self.record();r['cases']['success']['status']='EXPECTED_OBSERVATION'
  with self.assertRaises(ValueError):validate(r)
 def test_no_promoted_guarantee(self):
  from results import validate
  for key in ('expiration_guaranteed','live_qualification'):
   r=self.record();r[key]=True
   with self.assertRaises(ValueError):validate(r)
 def test_no_reviewed_pass_with_unknowns(self):
  from results import validate
  r=self.record();r['result']='LIMITED_OBSERVATIONS_REVIEWED'
  with self.assertRaises(ValueError):validate(r)
 def test_no_erased_scope_limitations(self):
  from results import validate
  r=self.record();r['unqualified']=[]
  with self.assertRaises(ValueError):validate(r)
 def test_no_traversal_evidence_path(self):
  from results import validate
  r=self.record();r['cases']['success']={'status':'FAIL','argv_sha256':'a'*64,'evidence':[{'path':'../escape','sha256':'a'*64,'bytes':1}]}
  with self.assertRaises(ValueError):validate(r)

class Catalog(unittest.TestCase):
 def test_catalog_inert_and_complete(self):
  c=json.loads((ROOT/'COMMAND-CATALOG.json').read_bytes())
  self.assertEqual(set(c['create']),set(p.CASES))
  self.assertTrue(c['kind'].startswith('INERT_'))
  for case,argv in c['create'].items():
   self.assertIn('--unit=jarvis-vm164-r3-stage2-<SESSION_NONCE>-'+case,argv)
   self.assertIn('--on-boot=<ABSOLUTE_BOOT_SECONDS.SIX_DIGITS>s',argv)
 def test_catalog_matches_builder(self):
  c=json.loads((ROOT/'COMMAND-CATALOG.json').read_bytes())
  for case,argv in c['create'].items():
   concrete=[a.replace('<SESSION_NONCE>','a'*32).replace('<ABSOLUTE_BOOT_SECONDS.SIX_DIGITS>','1000.000000') for a in argv]
   self.assertEqual(concrete,p.timer_argv('a'*32,case,1_000_000_000))
 def test_template_is_not_live_evidence(self):
  t=json.loads((ROOT/'templates/LIVE-RESULT.json').read_bytes())
  self.assertIsNone(t['session']['expires_utc']);self.assertFalse(t['stage2_authorized'])
  self.assertTrue(all(r['status']=='NOT_RUN' for r in t['cases'].values()))
 def test_install_argv_exact(self):
  c=json.loads((ROOT/'COMMAND-CATALOG.json').read_bytes())
  self.assertEqual(c['install'][:5],['/usr/bin/python3','-I','-B','-S','-c'])
  self.assertEqual(c['install'][5],proposals.INSTALL_CODE)
