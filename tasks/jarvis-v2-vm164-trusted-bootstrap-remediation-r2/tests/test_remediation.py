"""Offline fault injection. All subprocess/service/TTY operations are replaced."""
import base64,copy,hashlib,importlib.machinery,importlib.util,json,os,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
T=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path,loader=importlib.machinery.SourceFileLoader(name,str(path)))
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
# dataclasses requires a registered module.
import sys
spec=importlib.util.spec_from_file_location('lease_policy_r2',T/'tools/lease_policy.py')
L=importlib.util.module_from_spec(spec);sys.modules[spec.name]=L;spec.loader.exec_module(L)
B=load('boot_r2',T/'payload/BOOT.PY');D=load('decoder_r2',T/'tools/decode_diagnostic.py')
BOOT='11111111-2222-3333-4444-555555555555';HOST='aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'
def ident():return {'verified':True,'uuid':B.UUID,'serial':B.SERIAL,'disk_bytes':64*1024**3,'boot_id':BOOT}
def target():return {'node':'pve','vmid':164,'uuid':L.UUID,'serial':L.SERIAL,'disk':L.DISK,'disk_bytes':64*1024**3,'state':'stopped','boot':'order=scsi0','no_nic':True,'no_agent':True,'no_pending':True,'hotplug':'0','digest':'a'*40}
def proof():return {'scope':'synthetic_policy_only','host_owned':True,'independent_of_guest':True,'independent_of_cleanup':True,'hard_stop_authorized':True,'backend_qualified':True,'both_workers_active':True,'clock':'CLOCK_BOOTTIME','no_extension':True,'target_digest':'a'*40,'host_boot_id':HOST,'session':'OFFLINE-ONLY','armed_ns':100*L.NS,'revoke_ns':640*L.NS,'hard_stop_ns':700*L.NS}
def lease():return L.Lease.arm(target(),proof(),100*L.NS)
class FixtureBackend:
 def __init__(self,errors=None,values=None):self.errors=errors or {};self.values=values or {};self.calls=[]
 def call(self,action,value=None):
  self.calls.append(action)
  if action in self.errors:raise self.errors[action]
  return self.values.get(action,{'identity':ident(),'validate':{'valid':True},'inspect':{'closed':True}}.get(action))
class NoGuestCommands(unittest.TestCase):
 def setUp(self):
  self.p=patch.object(B.subprocess,'Popen',side_effect=AssertionError('NO_REAL_GUEST_COMMANDS'))
  self.p.start();self.addCleanup(self.p.stop)
class CleanupTests(NoGuestCommands):
 def test_success_still_never_claims_vm_stopped(self):
  f=FixtureBackend();r=B.close_session(f)
  self.assertTrue(r['guest_closure_observed']);self.assertTrue(r['poweroff_requested']);self.assertFalse(r['vm_stopped_verified']);self.assertTrue(r['external_fence_must_remain_armed']);self.assertEqual(r['errors'],[])
  self.assertEqual(f.calls,['identity','validate','mask','stop','kill','inspect','emit','poweroff'])
 def test_missing_state_still_terminates(self):
  f=FixtureBackend({'validate':FileNotFoundError()});r=B.close_session(f)
  self.assertTrue(r['poweroff_requested']);self.assertIn('state_or_snapshot_validation_failed',r['errors']);self.assertIn('mask',f.calls)
 def test_corrupt_state_still_terminates(self):
  f=FixtureBackend({'validate':json.JSONDecodeError('fixture','',0)});r=B.close_session(f);self.assertTrue(r['poweroff_requested']);self.assertTrue(r['errors'])
 def test_stale_binding_still_terminates_verified_target(self):
  f=FixtureBackend({'validate':B.Refusal('boot_changed')});r=B.close_session(f);self.assertTrue(r['poweroff_requested']);self.assertTrue(r['errors'])
 def test_snapshot_io_failure_still_terminates(self):
  f=FixtureBackend({'validate':OSError('snapshot')});self.assertTrue(B.close_session(f)['poweroff_requested'])
 def test_bad_validation_receipt_marks_incomplete(self):
  r=B.close_session(FixtureBackend(values={'validate':None}));self.assertTrue(r['poweroff_requested']);self.assertTrue(r['errors'])
 def test_each_action_exception_cannot_skip_poweroff(self):
  for action in ('validate','mask','stop','kill','inspect','emit'):
   with self.subTest(action=action):
    f=FixtureBackend({action:RuntimeError('fixture')});r=B.close_session(f);self.assertTrue(r['poweroff_requested']);self.assertEqual(f.calls[-1],'poweroff');self.assertTrue(r['errors'])
 def test_each_command_timeout_still_reaches_finalizer(self):
  for action in ('validate','mask','stop','kill','inspect','emit'):
   with self.subTest(action=action):
    f=FixtureBackend({action:subprocess.TimeoutExpired('fixture',5)});self.assertTrue(B.close_session(f)['poweroff_requested'])
 def test_keyboard_interrupt_after_identity_still_terminates(self):
  f=FixtureBackend({'validate':KeyboardInterrupt()});self.assertTrue(B.close_session(f)['poweroff_requested'])
 def test_system_exit_after_identity_still_terminates(self):
  f=FixtureBackend({'mask':SystemExit(2)});self.assertTrue(B.close_session(f)['poweroff_requested'])
 def test_all_cleanup_operations_fail_still_attempt_poweroff(self):
  f=FixtureBackend({k:OSError() for k in ('validate','mask','stop','kill','inspect','emit')});r=B.close_session(f);self.assertTrue(r['poweroff_requested']);self.assertFalse(r['guest_closure_observed'])
 def test_poweroff_timeout_never_stopped_pass(self):
  r=B.close_session(FixtureBackend({'poweroff':subprocess.TimeoutExpired('fixture',5)}));self.assertFalse(r['poweroff_requested']);self.assertFalse(r['vm_stopped_verified']);self.assertTrue(r['external_fence_must_remain_armed'])
 def test_mask_failure_marks_incomplete_even_if_later_inspect_closed(self):
  r=B.close_session(FixtureBackend({'mask':OSError()}));self.assertTrue(r['guest_closure_observed']);self.assertTrue(r['errors'])
 def test_residual_processes_not_closed(self):
  r=B.close_session(FixtureBackend(values={'inspect':{'closed':False}}));self.assertFalse(r['guest_closure_observed']);self.assertTrue(r['poweroff_requested'])
 def test_untrusted_inspect_type_not_closed(self):
  r=B.close_session(FixtureBackend(values={'inspect':{'closed':1}}));self.assertFalse(r['guest_closure_observed'])
 def test_identity_exception_no_guest_mutation(self):
  f=FixtureBackend({'identity':OSError()});r=B.close_session(f);self.assertEqual(f.calls,['identity']);self.assertFalse(r['poweroff_requested'])
 def test_identity_timeout_no_guest_mutation(self):
  f=FixtureBackend({'identity':subprocess.TimeoutExpired('fixture',5)});B.close_session(f);self.assertEqual(f.calls,['identity'])
 def test_wrong_identity_variations_no_guest_mutation(self):
  for k,v in {'uuid':'wrong','serial':'wrong','disk_bytes':0,'verified':False,'boot_id':'bad'}.items():
   with self.subTest(field=k):
    d=ident();d[k]=v;f=FixtureBackend(values={'identity':d});r=B.close_session(f);self.assertEqual(f.calls,['identity']);self.assertFalse(r['target_verified'])
 def test_bad_identity_schema_no_guest_mutation(self):
  f=FixtureBackend(values={'identity':None});B.close_session(f);self.assertEqual(f.calls,['identity'])
 def test_direct_inspect_rechecks_identity_before_manager(self):
  with patch.object(B,'identity',side_effect=B.Refusal('wrong_target')),patch.object(B.subprocess,'run') as run:
   with self.assertRaises(B.Refusal):B.child('inspect')
   run.assert_not_called()
 def test_no_wait_for_capture_in_cleanup(self):
  source=(T/'payload/BOOT.PY').read_text();self.assertNotIn('time.sleep(',source)
 def test_budget_composition_fits_manager_envelope(self):
  composed=8*(B.STEP_BUDGET+B.KILL_REAP_BUDGET)
  self.assertLessEqual(composed, B.WORK_BUDGET)
  self.assertGreaterEqual(B.UNIT_START_LIMIT,B.WORK_BUDGET+B.UNIT_STOP_LIMIT+10)
 def test_only_fixed_unit_operations(self):
  self.assertEqual(set(B.OPS),{'mask','stop','kill','poweroff'})
  self.assertTrue(all(x[0]=='/usr/bin/systemctl' for x in B.OPS.values()))
  self.assertNotIn('--force',sum(B.OPS.values(),[]))
 def test_sigkill_cannot_be_python_finally_proof(self):
  # Not a real SIGKILL test: model loss of every guest worker, then host deadline.
  f=lease();self.assertEqual(f.tick(f.hard_stop_ns,HOST,'running'),'HARD_STOP_DUE_UNTIL_INDEPENDENT_STOP_PROOF')
  self.assertFalse(L.receipt(f)['live_enforcement_verified'])
 def test_independent_close_submission_properties(self):
  runner=MagicMock();runner.call.return_value=ident();runner.script='/verified-media/BOOT.PY'
  with patch.object(B,'GuestRunner',return_value=runner),patch.object(B.subprocess,'run') as run:
   B.submit_close()
  argv=run.call_args.args[0]
  for prop in ('--property=TimeoutStartSec=90s','--property=TimeoutStopSec=5s','--property=KillMode=control-group','--property=Restart=no'):self.assertIn(prop,argv)
 def test_submit_failure_retains_host_fence_requirement(self):
  runner=MagicMock();runner.call.return_value=ident();runner.script='/verified-media/BOOT.PY'
  with patch.object(B,'GuestRunner',return_value=runner),patch.object(B.subprocess,'run',side_effect=subprocess.TimeoutExpired('fixture',5)):
   with self.assertRaises(subprocess.TimeoutExpired):B.submit_close()
  self.assertFalse(L.receipt(lease())['root_boot_go'])
class BudgetTests(NoGuestCommands):
 def test_exhausted_normal_budget_still_reserves_poweroff(self):
  now=[0];runner=B.GuestRunner(clock=lambda:now[0]);now[0]=54
  with self.assertRaises(B.Refusal):runner.call('mask')
  proc=MagicMock();proc.returncode=0;proc.communicate.return_value=(b'',b'')
  with patch.object(B.subprocess,'Popen',return_value=proc):runner.call('poweroff')
  self.assertLessEqual(proc.communicate.call_args.kwargs['timeout'],5)
 def test_exhausted_global_budget_starts_no_process(self):
  now=[0];runner=B.GuestRunner(clock=lambda:now[0]);now[0]=60
  with self.assertRaises(B.Refusal):runner.call('poweroff')
 def test_timeout_kills_process_group(self):
  proc=MagicMock();proc.pid=987654;proc.communicate.side_effect=[subprocess.TimeoutExpired('fixture',5),(b'',b'')]
  with patch.object(B.subprocess,'Popen',return_value=proc),patch.object(B.os,'killpg') as kill:
   with self.assertRaises(subprocess.TimeoutExpired):B.GuestRunner().call('mask')
  kill.assert_called_once_with(987654,B.signal.SIGKILL);self.assertEqual(proc.communicate.call_count,2)
 def test_keyboard_interrupt_kills_process_group(self):
  proc=MagicMock();proc.pid=987654;proc.communicate.side_effect=[KeyboardInterrupt(),(b'',b'')]
  with patch.object(B.subprocess,'Popen',return_value=proc),patch.object(B.os,'killpg') as kill:
   with self.assertRaises(KeyboardInterrupt):B.GuestRunner().call('mask')
  kill.assert_called_once()
 def test_reaping_failure_does_not_expand_retry_budget(self):
  proc=MagicMock();proc.pid=987654;proc.communicate.side_effect=[subprocess.TimeoutExpired('fixture',5),subprocess.TimeoutExpired('fixture',1)]
  with patch.object(B.subprocess,'Popen',return_value=proc),patch.object(B.os,'killpg'):
   with self.assertRaises(subprocess.TimeoutExpired):B.GuestRunner().call('mask')
  self.assertEqual(proc.communicate.call_count,2)
 def test_command_error_not_pass(self):
  proc=MagicMock();proc.returncode=1;proc.communicate.return_value=(b'',b'')
  with patch.object(B.subprocess,'Popen',return_value=proc):
   with self.assertRaises(B.Refusal):B.GuestRunner().call('mask')
 def test_unknown_action_cannot_spawn(self):
  with self.assertRaises(B.Refusal):B.GuestRunner().call('arbitrary shell')
 def test_process_resources_and_no_shell(self):
  proc=MagicMock();proc.returncode=0;proc.communicate.return_value=(b'',b'')
  with patch.object(B.subprocess,'Popen',return_value=proc) as popen:B.GuestRunner().call('poweroff')
  self.assertTrue(popen.call_args.kwargs['start_new_session']);self.assertNotIn('shell',popen.call_args.kwargs)
class LeaseTests(unittest.TestCase):
 def test_prearm_with_stopped_target_and_qualified_claims_is_model_only(self):
  l=lease();r=L.receipt(l);self.assertFalse(r['root_boot_go']);self.assertFalse(r['authorization_granted']);self.assertFalse(r['runtime_backend_implemented'])
 def test_all_independence_and_enforcement_flags_required(self):
  for k in ('host_owned','independent_of_guest','independent_of_cleanup','hard_stop_authorized','backend_qualified','both_workers_active','no_extension'):
   with self.subTest(flag=k):
    p=proof();p[k]=False
    with self.assertRaises(L.Refusal):L.Lease.arm(target(),p,100*L.NS)
 def test_live_claims_are_never_accepted_as_replay_authority(self):
  p=proof();p['scope']='live'
  with self.assertRaises(L.Refusal):L.Lease.arm(target(),p,100*L.NS)
 def test_target_mismatch_refused(self):
  for k,v in {'node':'other','vmid':163,'uuid':'wrong','serial':'wrong','disk':'other','disk_bytes':0,'state':'running','boot':'order=scsi0;ide2','no_nic':False,'no_agent':False,'no_pending':False,'hotplug':'disk'}.items():
   with self.subTest(field=k):
    d=target();d[k]=v
    with self.assertRaises(L.Refusal):L.Lease.arm(d,proof(),100*L.NS)
 def test_corrected_boot_accepted_only_as_supplied_claim(self):self.assertEqual(lease().identity_digest,'a'*40)
 def test_guest_timer_only_never_admits(self):
  p=proof();p['host_owned']=False
  with self.assertRaises(L.Refusal):L.Lease.arm(target(),p,100*L.NS)
 def test_arbitrary_timer_deadline_refused(self):
  for k in ('revoke_ns','hard_stop_ns'):
   p=proof();p[k]+=L.NS
   with self.assertRaises(L.Refusal):L.Lease.arm(target(),p,100*L.NS)
 def test_expired_arm_refused(self):
  with self.assertRaises(L.Refusal):L.Lease.arm(target(),proof(),116*L.NS)
 def test_stale_boot_admission_refused(self):
  with self.assertRaises(L.Refusal):lease().before_start(116*L.NS,HOST,'a'*40,True)
 def test_no_worker_before_root_no_admission(self):
  with self.assertRaises(L.Refusal):lease().before_start(101*L.NS,HOST,'a'*40,False)
 def test_restart_or_duplicate_start_refused(self):
  with self.assertRaises(L.Refusal):lease().before_start(101*L.NS,HOST,'a'*40,True,True)
 def test_config_changed_after_arm_refused(self):
  with self.assertRaises(L.Refusal):lease().before_start(101*L.NS,HOST,'b'*40,True)
 def test_host_reboot_invalidates_admission(self):
  with self.assertRaises(L.Refusal):lease().before_start(101*L.NS,BOOT,'a'*40,True)
 def test_deadline_cannot_extend(self):
  l=lease()
  with self.assertRaises(AttributeError):l.hard_stop_ns+=L.NS
 def test_absolute_cutoff_survives_modeled_suspend_time_jump(self):
  l=lease();self.assertEqual(l.tick(900*L.NS,HOST,'running'),'HARD_STOP_DUE_UNTIL_INDEPENDENT_STOP_PROOF')
 def test_revoke_before_hardstop(self):self.assertEqual(lease().tick(640*L.NS,HOST,'running'),'REVOKE_AND_GRACEFUL_SHUTDOWN_DUE')
 def test_hardstop_does_not_claim_vm_stopped(self):self.assertEqual(lease().tick(700*L.NS,HOST,'unknown'),'HARD_STOP_DUE_UNTIL_INDEPENDENT_STOP_PROOF')
 def test_cleanup_or_guest_watchdog_death_does_not_cancel_model(self):self.assertEqual(lease().tick(701*L.NS,HOST,'running'),'HARD_STOP_DUE_UNTIL_INDEPENDENT_STOP_PROOF')
 def test_stopped_observation_does_not_disarm_fence(self):self.assertEqual(lease().tick(300*L.NS,HOST,'stopped'),'KEEP_FENCE_ARMED_UNTIL_EXTERNAL_FINAL_PROOF')
 def test_clock_rollback_refuses_admission(self):self.assertEqual(lease().tick(99*L.NS,HOST,'running'),'UNSAFE_CLOCK_OR_HOST_REBOOT_NO_ADMISSION')
 def test_deadline_types_bool_nan_refused(self):
  for v in (True,float('nan'),-1,'100'):
   p=proof();p['armed_ns']=v
   with self.assertRaises(L.Refusal):L.Lease.arm(target(),p,100*L.NS)
 def test_saved_fabricated_worker_claims_never_make_go(self):self.assertIs(L.receipt(lease())['root_boot_go'],False)
class FileAndCaptureTests(NoGuestCommands):
 def setUp(self):
  super().setUp();self.tmp=tempfile.TemporaryDirectory(dir=T/'evidence');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
 def raw(self,**extra):
  d={'format':'vm164-readonly-probe-v1','vm_uuid':B.UUID,'disk_serial':B.SERIAL,'disk_bytes':64*1024**3,'boot_id':BOOT,'optical_media_present':True};d.update(extra);return json.dumps(d).encode()
 def rows(self,raw):
  e=base64.b64encode(raw).decode();return '\n'.join(f'R{i//48:04d}:'+e[i:i+48] for i in range(0,len(e),48))
 def test_attached_media_diagnostic_roundtrip(self):
  raw=self.raw();self.assertEqual(D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest(),BOOT),raw)
 def test_media_absence_cannot_be_relabelled_attached(self):
  raw=self.raw(optical_media_present=False)
  with self.assertRaises(ValueError):D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest(),BOOT)
 def test_wrong_boot_rejected(self):
  raw=self.raw()
  with self.assertRaises(ValueError):D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest(),HOST)
 def test_missing_duplicate_or_reordered_rows_rejected(self):
  raw=self.raw();rows=self.rows(raw).splitlines()
  for bad in (rows[1:],rows+rows[:1],list(reversed(rows))):
   with self.assertRaises(ValueError):D.decode('\n'.join(bad),hashlib.sha256(raw).hexdigest(),BOOT)
 def test_corruption_rejected(self):
  raw=self.raw()
  with self.assertRaises(ValueError):D.decode(self.rows(raw),'a'*64,BOOT)
 def test_wrong_target_rejected(self):
  raw=self.raw(vm_uuid='wrong')
  with self.assertRaises(ValueError):D.decode(self.rows(raw),hashlib.sha256(raw).hexdigest(),BOOT)
 def test_exclusive_outputs_preserve_existing_evidence(self):
  p=self.root/'saved';p.write_bytes(b'original')
  with self.assertRaises(FileExistsError):B.write_new(p,b'new')
  self.assertEqual(p.read_bytes(),b'original')
 def test_symlink_no_follow(self):
  p=self.root/'input';p.symlink_to(self.root/'original');(self.root/'original').write_bytes(b'old')
  with self.assertRaises(OSError):B.read_regular(p)
 def test_hardlink_refused(self):
  p=self.root/'input';p.write_bytes(b'x');os.link(p,self.root/'linked')
  with self.assertRaises(B.Refusal):B.read_regular(p)
 def test_fifo_refused_without_blocking(self):
  p=self.root/'fifo';os.mkfifo(p)
  with self.assertRaises(B.Refusal):B.read_regular(p)
 def test_oversize_refused(self):
  p=self.root/'large';p.write_bytes(b'x'*65537)
  with self.assertRaises(B.Refusal):B.read_regular(p)
 def test_data_integrity_file_stays_unchanged(self):
  p=self.root/'input';p.write_bytes(b'content');self.assertEqual(B.read_regular(p),b'content');self.assertEqual(p.read_bytes(),b'content')

class DiagnosticIntegrationTests(NoGuestCommands):
 def setUp(self):
  super().setUp();self.tmp=tempfile.TemporaryDirectory(dir=T/'evidence');self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name);self.media=self.root/'media';self.media.mkdir();self.ram=self.root/'run';self.mountinfo=self.root/'mountinfo'
  probe=(T.parent/'jarvis-v2-vm164-lab-readiness-r1/tools/lab_package.py').read_bytes()
  (self.media/'LABPKG.PY').write_bytes(probe);(self.media/'BOOT.PY').write_bytes(b'fixture_path_only')
  encoded=str(self.media).replace('\\','\\134').replace(' ','\\040')
  self.mountinfo.write_text('1 0 0:1 / /run rw - tmpfs tmpfs rw\n2 1 11:0 / '+encoded+' ro,nosuid,nodev,noexec - iso9660 /dev/sr0 ro\n')
  original=Path
  def path(n):return self.mountinfo if str(n)=='/proc/self/mountinfo' else original(n)
  for p in (patch.object(B,'RAM',self.ram),patch.object(B,'__file__',str(self.media/'BOOT.PY')),patch.object(B,'identity',return_value=ident()),patch.object(B.os,'ttyname',return_value='/dev/tty1'),patch.object(B,'Path',side_effect=path)):
   p.start();self.addCleanup(p.stop)
 def result(self,media=True):return subprocess.CompletedProcess([],0,json.dumps({'format':'vm164-readonly-probe-v1','vm_uuid':B.UUID,'disk_serial':B.SERIAL,'boot_id':BOOT,'disk_bytes':64*1024**3,'optical_media_present':media}).encode(),b'')
 def test_real_probe_handoff_is_pinned_and_keeps_media_true(self):
  with patch.object(B.subprocess,'run',return_value=self.result()) as run:B.diagnostic_probe()
  self.assertEqual(run.call_args.args[0],[B.PYTHON,'-I','-B','-S',str(self.media/'LABPKG.PY'),'probe'])
  self.assertTrue(json.loads((self.ram/'PROBE.JSON').read_bytes())['optical_media_present'])
  self.assertFalse(json.loads((self.ram/'DIAGNOSTIC.json').read_bytes())['installation_qualified'])
 def test_false_media_not_converted_to_success(self):
  with patch.object(B.subprocess,'run',return_value=self.result(False)):
   with self.assertRaises(B.Refusal):B.diagnostic_probe()
  self.assertTrue((self.ram/'PROBE.JSON').exists());self.assertFalse((self.ram/'DIAGNOSTIC.json').exists())
 def test_corrupt_payload_refuses_before_execution_or_ram_write(self):
  (self.media/'LABPKG.PY').write_text('corrupt')
  with patch.object(B.subprocess,'run') as run:
   with self.assertRaises(B.Refusal):B.diagnostic_probe()
   run.assert_not_called()
  self.assertFalse(self.ram.exists())
 def test_writable_media_refuses_before_execution(self):
  self.mountinfo.write_text(self.mountinfo.read_text().replace('ro,nosuid,nodev,noexec','rw,nosuid,nodev,noexec'))
  with patch.object(B.subprocess,'run') as run:
   with self.assertRaises(B.Refusal):B.diagnostic_probe()
   run.assert_not_called()
 def test_existing_destination_never_overwritten(self):
  self.ram.mkdir();(self.ram/'keep').write_bytes(b'old')
  with patch.object(B.subprocess,'run') as run:
   with self.assertRaises(FileExistsError):B.diagnostic_probe()
   run.assert_not_called()
  self.assertEqual((self.ram/'keep').read_bytes(),b'old')
 def test_probe_failure_preserves_raw_output(self):
  with patch.object(B.subprocess,'run',return_value=subprocess.CompletedProcess([],1,b'failure-record',b'')):
   with self.assertRaises(B.Refusal):B.diagnostic_probe()
  self.assertEqual((self.ram/'PROBE.JSON').read_bytes(),b'failure-record')
 def test_probe_timeout_keeps_session_for_cleanup(self):
  with patch.object(B.subprocess,'run',side_effect=subprocess.TimeoutExpired('fixture',15)):
   with self.assertRaises(subprocess.TimeoutExpired):B.diagnostic_probe()
  self.assertTrue((self.ram/'SESSION.json').exists())
 def test_no_tmpfs_refuses_before_execution(self):
  self.mountinfo.write_text(self.mountinfo.read_text().replace('- tmpfs','- ext4'))
  with patch.object(B.subprocess,'run') as run:
   with self.assertRaises(B.Refusal):B.diagnostic_probe()
   run.assert_not_called()

G=load('state_gate_r2',T/'tools/state_gate.py')
A=load('artifact_check_r2',T/'tools/check_candidate.py')
BASE=G.V.timestamp('2026-11-06T18:00:00Z')
import datetime as dt

def snap(state,second=0,previous=None):
 status,attached=G.V.STATES[state]
 c={'name':'jarvis-g6k-clean-164','smbios1':'uuid='+L.UUID,'scsi0':L.DISK+',serial='+L.SERIAL+',size=64G','ide2':(G.ISO if attached else 'none')+',media=cdrom','boot':'order=scsi0','onboot':0,'agent':'0','serial0':'socket','vga':'std','hotplug':'0','protection':1,'digest':'a'*40,'cores':4,'sockets':1,'memory':6000,'balloon':0}
 if previous:
  old=G.V.parse(previous['readbacks']['config']['raw']);c['digest']=old['digest'] if c['ide2']==old['ide2'] else 'b'*40
 def stamp(s):return (BASE+dt.timedelta(seconds=s)).strftime('%Y-%m-%dT%H:%M:%SZ')
 s={'id':'s'+str(second),'state':state,'node':'pve','vmid':164,'capture_started_at':stamp(second),'capture_finished_at':stamp(second+3),'previous_sha256':G.V.sha(G.V.canonical(previous)) if previous else None,'readbacks':{},'config_digest':c['digest'],'iso_verification':None}
 for name,value in {'config':c,'status':{'vmid':164,'status':status},'pending':[]}.items():
  raw=json.dumps(value,sort_keys=True);s['readbacks'][name]={'raw':raw,'sha256':G.V.sha(raw.encode()),'captured_at':stamp(second+1),'endpoint':G.V.ENDPOINTS[name]}
 if attached:s['iso_verification']={'volume':G.ISO,'sha256':G.ISO_SHA,'bytes':196608,'captured_at':stamp(second),'config_readback_sha256':s['readbacks']['config']['sha256']}
 return s

def envelope(*snaps):return {'format':G.V.FORMAT,'kind':'synthetic','session_reference':'OFFLINE-R2-ONLY','snapshots':list(snaps)}
class StateAndArtifactTests(unittest.TestCase):
 def test_original_installer_still_rejects_attached_media(self):
  lab=load('unchanged_lab_installer_for_r2_test',T.parent/'jarvis-v2-vm164-lab-readiness-r1/tools/lab_package.py')
  f={'vm_uuid':B.UUID,'disk_serial':B.SERIAL,'disk_bytes':64*1024**3,
     'architecture':'x86_64','python_version':'3.14.4','root_filesystem':'ext4',
     'network_interfaces':['lo'],'block_disks':['sda'],'optical_media_present':True,
     'shared_or_slave_mounts':0,'external_filesystems':0,'sqlite_version':'3.46.1',
     'openssl_version':'OpenSSL 3.5.5 27 Jan 2026'}
  binding={k:None for k in ('machine_id','boot_id','root_device','root_filesystem_uuids','python_sha256','native_runtime_files','bwrap_sha256')}
  with self.assertRaisesRegex(lab.Refusal,'target_optical_media_present'):lab.check_target(f,binding)
 def test_attached_corrected_claim_is_offline_only(self):
  r=G.evaluate(envelope(snap('preflight_attached')),BASE+dt.timedelta(seconds=10));self.assertFalse(r['root_boot_go']);self.assertFalse(r['installation_qualified']);self.assertFalse(r['live_ejection_supported'])
 def test_running_ejection_edge_absent(self):
  self.assertNotIn('debug_empty',G.V.STATES)
  self.assertTrue(all(not (a=='debug_attached' and b=='closed_empty') for a,b in G.V.EDGES))
 def test_diagnostic_then_stop_then_detach_chain(self):
  rows=[]
  for i,state in enumerate(('preflight_attached','debug_attached','closed_attached','closed_empty','clean_running','final_empty')):rows.append(snap(state,i*10,rows[-1] if rows else None))
  r=G.evaluate(envelope(*rows),BASE+dt.timedelta(seconds=60));self.assertFalse(r['authorization_granted'])
 def test_cannot_skip_stopped_attached_before_detach(self):
  a=snap('preflight_attached');b=snap('debug_attached',10,a);c=snap('closed_empty',20,b)
  with self.assertRaises(G.V.Refusal):G.evaluate(envelope(a,b,c),BASE+dt.timedelta(seconds=30))
 def test_pending_only_detach_refused(self):
  s=snap('preflight_attached');raw=json.dumps([{'key':'ide2','value':G.ISO+',media=cdrom','pending':'none,media=cdrom'}]);s['readbacks']['pending']['raw']=raw;s['readbacks']['pending']['sha256']=G.V.sha(raw.encode())
  with self.assertRaises(G.V.Refusal):G.evaluate(envelope(s),BASE+dt.timedelta(seconds=10))
 def test_old_r4_iso_not_r2_authority(self):
  s=snap('preflight_attached');d=G.V.parse(s['readbacks']['config']['raw']);d['ide2']='local:iso/vm164-trusted-bootstrap-fd91b8b07243565e.iso,media=cdrom';raw=json.dumps(d);s['readbacks']['config']['raw']=raw;s['readbacks']['config']['sha256']=G.V.sha(raw.encode())
  with self.assertRaises(G.V.Refusal):G.evaluate(envelope(s),BASE+dt.timedelta(seconds=10))
 def test_stale_readbacks_refused(self):
  with self.assertRaises(G.V.Refusal):G.evaluate(envelope(snap('preflight_attached')),BASE+dt.timedelta(seconds=121))
 def test_duplicate_json_refused(self):
  with self.assertRaises(G.V.Refusal):G.V.parse('{"k":1,"k":2}')
 def test_preserved_bootstrap_manifest_and_seal(self):
  root=T.parent/'jarvis-v2-vm164-trusted-bootstrap-r1';seal=json.loads((root/'SEAL.json').read_bytes());self.assertEqual(hashlib.sha256((root/'MANIFEST.json').read_bytes()).hexdigest(),seal['manifest_sha256'])
 def test_new_candidate_is_nonboot_reproducible_and_unapproved(self):
  r=A.check();self.assertEqual(r['descriptor_types'],[1,255]);self.assertFalse(r['approved_or_attached']);self.assertFalse(r['root_boot_go'])

if __name__=='__main__':unittest.main(verbosity=2)
