"""Independent synthetic probes. No live commands or source-packet writes.

Control tests expect existing protections to hold. Gap tests assert a required
safeguard and deliberately FAIL if the reviewed implementation lacks it.
"""
import ast
import copy
import json
from pathlib import Path
import sys
import unittest

AUDIT=Path(__file__).resolve().parents[1]
TARGET=AUDIT.parent/'jarvis-v2-vm164-stage2-operator-preparation-r1'
sys.path.insert(0,str(TARGET/'src'))
import packet as p
import results
CAT=json.loads((TARGET/'COMMAND-CATALOG.json').read_bytes())

def ident():
 return {'node':'pve','uid':65534,'gid':65534,'groups':[65534],'nobody_processes':[],
 'packages':dict(p.PACKAGES),'source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
 **{k:'d'*64 for k in ('vm_authority_absent_review','credential_access_denied_review',
 'binary_custody_review','acl_review','source_custody_review','exclusive_operator_review')}}

def session():
 return {'nonce':'b'*32,'boot_id':'abcdefab-1234-5678-9abc-123456789abc','starts_utc':'2031-02-03T10:00:00Z',
 'expires_utc':'2031-02-03T10:45:00Z','start_boot_us':8_000_000_000,
 'start_offset_low_us':11_999_900,'start_offset_high_us':12_000_100}

def sample():
 return {'boot_id':session()['boot_id'],'utc':'2031-02-03T10:02:00Z','boot_us':8_120_000_000,
 'offset_low_us':11_999_900,'offset_high_us':12_000_100}

def ownership():
 o=p.plan(session(),sample(),'success',ident())
 o.update(boot_id=session()['boot_id'],description='JARVIS-Stage2-'+'b'*32+'-success')
 c=copy.deepcopy(o);c['states']=['active','active']
 return o,c

def reviewed_record():
 e={'path':'synthetic-only.json','sha256':'a'*64,'bytes':1}
 return {'kind':'CAPTURED_STAGE2_LIMITED_RESULT','source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,
 'session':session(),'expiration_guaranteed':False,'live_qualification':False,'result':'LIMITED_OBSERVATIONS_REVIEWED',
 'independent_reviewer':'SYNTHETIC_TEST_REVIEWER','clock_domain':'CLOCK_MONOTONIC','clock_domain_basis':'SYNTHETIC',
 'cleanup':{'status':'CLOSED_EVIDENCE_RETAINED','inactive_evidence':[e]},
 'unqualified':['manager_reexec','host_reboot','physical_suspend_wake','VM_termination','root_bootstrap'],
 'cases':{c:{'status':'EXPECTED_NEGATIVE','argv_sha256':'b'*64,'evidence':[e]} for c in p.CASES}}

class Controls(unittest.TestCase):
 def test_every_creation_explicit_uid_gid_type(self):
  for c in p.CASES:
   argv=p.timer_argv('b'*32,c,8_150_000_000)
   for prop in ('User=65534','Group=65534','Type=exec','Restart=no','NoNewPrivileges=yes',
                'CapabilityBoundingSet=','AmbientCapabilities=','KillMode=control-group'):
    self.assertIn('--property='+prop,argv)
 def test_all_payloads_in_nonvm_scope(self):
  for c in p.CASES:
   a=p.timer_argv('b'*32,c,8_150_000_000);cmd=a[a.index('--')+1:]
   self.assertIn(cmd[0],('/usr/bin/python3','/opt/jarvis-vm164-r3-stage2/absent-executable-'+'b'*32))
   for forbidden in ('/usr/sbin/qm','/usr/bin/pvesh','--execute-reviewed-host','/bin/sh','/bin/bash'):
    self.assertNotIn(forbidden,cmd)
 def test_twelve_names_distinct_and_bounded(self):
  names=[p.unit('b'*32,c) for c in p.CASES];self.assertEqual(len(set(names)),12)
  self.assertTrue(all(len(n+'.service')<255 for n in names))
 def test_wake_onboot_accuracy_no_jitter(self):
  a=p.timer_argv('b'*32,'success',8_150_000_123)
  for flag in ('--on-boot=8150.000123s','--timer-property=WakeSystem=yes','--timer-property=AccuracySec=1us','--timer-property=RandomizedDelaySec=0'):
   self.assertIn(flag,a)
 def test_foreign_list_collision_denied(self):
  with self.assertRaises(ValueError):p.plan(session(),sample(),'success',ident(),occupied=[p.unit('b'*32,'success')+'.service'])
 def test_identity_unknown_denied(self):
  i=ident();i['credential_access_denied_review']=None
  with self.assertRaises(ValueError):p.plan(session(),sample(),'success',i)
 def test_root_denied(self):
  i=ident();i['uid']=0
  with self.assertRaises(ValueError):p.validate_identity(i)
 def test_privileged_group_denied(self):
  i=ident();i['groups']=[65534,0]
  with self.assertRaises(ValueError):p.validate_identity(i)
 def test_expired_window_denied(self):
  x=sample();x.update(utc='2031-02-03T10:45:00Z',boot_us=10_700_000_000)
  with self.assertRaises(ValueError):p.plan(session(),x,'success',ident())
 def test_oversize_window_denied(self):
  s=session();s['expires_utc']='2031-02-03T10:45:01Z'
  with self.assertRaises(ValueError):p.plan(s,sample(),'success',ident())
 def test_wrong_boot_denied_for_creation(self):
  x=sample();x['boot_id']='12345678-0000-0000-0000-123456789abc'
  with self.assertRaises(ValueError):p.plan(session(),x,'success',ident())
 def test_unknown_clock_domain_denied(self):
  with self.assertRaises(ValueError):p.clock_domain(1000,1000,-1,1)
 def test_unambiguous_historical_suspend_conversion(self):
  self.assertEqual(p.clock_domain(100_000_000,88_000_000,11_999_900,12_000_100),'CLOCK_MONOTONIC')
 def test_changed_owned_argv_denied(self):
  o,c=ownership();c['argv'].append('changed')
  with self.assertRaises(ValueError):p.cleanup_argv('b'*32,'success',o,c)
 def test_interrupted_cleanup_scoped_service_only(self):
  o,c=ownership();c['states']=['inactive','active']
  self.assertEqual(p.cleanup_argv('b'*32,'success',o,c),[['/usr/bin/systemctl','--system','--no-ask-password','stop',o['name']+'.service']])
 def test_retained_failed_states_no_mutation(self):
  o,c=ownership();c['states']=['failed','failed'];self.assertEqual(p.cleanup_argv('b'*32,'success',o,c),[])
 def test_unfilled_results_not_reviewed(self):
  with self.assertRaises(ValueError):results.validate(json.loads((TARGET/'templates/LIVE-RESULT.json').read_bytes()))
 def test_no_guarantee_upgrade(self):
  r=reviewed_record();r['expiration_guaranteed']=True
  with self.assertRaises(ValueError):results.validate(r)
 def test_callback_has_no_actuation_imports(self):
  f=AUDIT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src/stage2_canary.py'
  imports={a.name for n in ast.walk(ast.parse(f.read_bytes())) if isinstance(n,ast.Import) for a in n.names}
  self.assertTrue(imports.isdisjoint({'subprocess','socket','requests','http','urllib'}))
 def test_installer_exclusive_creation_no_remove(self):
  code=CAT['install'][5]
  self.assertIn('os.O_EXCL',code);self.assertIn('os.O_NOFOLLOW',code);self.assertIn('os.mkdir(',code)
  for bad in ('os.unlink','os.remove','shutil.rmtree','os.replace','exist_ok=True'):self.assertNotIn(bad,code)

class GapProbes(unittest.TestCase):
 def test_collision_input_string_must_be_rejected(self):
  # Actual known collision supplied as a malformed JSON string, not an array.
  with self.assertRaises((ValueError,TypeError)):
   p.plan(session(),sample(),'success',ident(),occupied=p.unit('b'*32,'success')+'.service')
 def test_cleanup_missing_boot_binding_must_be_rejected(self):
  o,c=ownership();o.pop('boot_id');c.pop('boot_id')
  with self.assertRaises(ValueError):p.cleanup_argv('b'*32,'success',o,c)
 def test_cleanup_mismatched_current_name_must_be_rejected(self):
  o,c=ownership();c['name']='unrelated.service'
  with self.assertRaises(ValueError):p.cleanup_argv('b'*32,'success',o,c)
 def test_callback_outcome_missing_host_boot_must_be_rejected(self):
  row={'status':'NON_ROOT_NON_VM_CLOCK_CANARY','uid':65534,'euid':65534,'vm_operations':False,
       'boottime_us':8_150_000_001,'requested_mode':'success'}
  with self.assertRaises(ValueError):p.outcome('success',callback_row=row,result='success',code=1,status=0,deadline=8_150_000_000)
 def test_rearm_a_firing_must_not_be_accepted_as_expected(self):
  row={'status':'NON_ROOT_NON_VM_CLOCK_CANARY','uid':65534,'euid':65534,'vm_operations':False,
       'host_boot_id':session()['boot_id'],'boottime_us':8_150_000_001,'requested_mode':'success'}
  with self.assertRaises(ValueError):p.outcome('rearm-a',callback_row=row,result='success',code=1,status=0,deadline=8_150_000_000)
 def test_reviewed_record_requires_operator_and_authorization(self):
  with self.assertRaises(ValueError):results.validate(reviewed_record())
 def test_reviewed_record_requires_case_names_and_observations(self):
  r=reviewed_record();r.update(operator='SYNTHETIC',authorization_reference='SYNTHETIC',packet_manifest_sha256='c'*64)
  with self.assertRaises(ValueError):results.validate(r)
 def test_expected_negative_not_valid_for_ordinary_success(self):
  r=reviewed_record();r.update(operator='SYNTHETIC',authorization_reference='SYNTHETIC',packet_manifest_sha256='c'*64)
  for c,row in r['cases'].items():row.update(unit_names=[p.unit('b'*32,c)+'.timer',p.unit('b'*32,c)+'.service'],observations={'synthetic':True})
  with self.assertRaises(ValueError):results.validate(r)
 def test_policy_read_has_preallocation_bound(self):
  # read_bytes() allocates the whole input before the later length assertion.
  tree=ast.parse(CAT['read']['R19-policy-or-manual-read'][5])
  self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='read_bytes' for n in ast.walk(tree)), 'whole-file allocation precedes size guard')
 def test_manual_decompression_has_streaming_bound(self):
  tree=ast.parse(CAT['read']['R20-manual-gzip-read'][5])
  self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=='decompress' for n in ast.walk(tree)), 'whole gzip decompression precedes size guard')
