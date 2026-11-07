"""Deterministic fixture tests. NO real command, timer, VM or network effects."""
import copy,datetime as dt,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
T=Path(__file__).resolve().parents[1];sys.path.insert(0,str(T/'src'))
import model as M
import store as S
import sim
import host_adapter as H
import systemd_codec as C
import preflight as P
SESSION='1'*32;SOURCE='2'*64
class NoEffects(unittest.TestCase):
 def setUp(self):
  for target in ('subprocess.Popen','os.killpg'):
   p=patch(target,side_effect=AssertionError('OFFLINE_UNEXPECTED_EFFECT:'+target));p.start();self.addCleanup(p.stop)
 def setup_engine(self,policy='A',store=None):
  c=sim.FakeClock();b=sim.FixtureBackend(c);s=store or S.MemoryStore();e=M.Engine(b,s,c,SOURCE)
  a=sim.approval(c,SOURCE,policy);return c,b,s,e,a
 def armed(self,policy='A'):
  c,b,s,e,a=self.setup_engine(policy);e.prepare(a,SESSION)
  if policy=='B':b.force_grant=s.plan()['force_grant_sha256']
  return c,b,s,e,a
class ValidationTests(NoEffects):
 def test_exact_reported_hardware_is_fixture_only(self):
  c,b,s,e,a=self.setup_engine();r=e.prepare(a,SESSION)
  self.assertFalse(r['root_boot_go']);self.assertFalse(r['expiration_guaranteed']);self.assertTrue(r['simulated'])
 def test_wrong_vmid_uuid_disk_serial(self):
  for field,value in [('vmid',163),('uuid','wrong'),('disk','other:164/raw'),('serial','wrong')]:
   with self.subTest(field=field):
    c,b,s,e,a=self.setup_engine()
    if field=='vmid':b.overrides['vmid']=value
    elif field=='uuid':b.cfg['smbios1']='uuid='+value
    elif field=='disk':b.cfg['scsi0']=value+',serial='+M.SERIAL+',size=64G'
    else:b.cfg['scsi0']=M.DISK+',serial='+value+',size=64G'
    with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
    self.assertNotIn(('start',164),b.actions)
 def test_boot_order_extra_devices_and_missing_fields(self):
  for mutation in ('boot','net0','efidisk0','agent_missing'):
   with self.subTest(mutation=mutation):
    c,b,s,e,a=self.setup_engine()
    if mutation=='boot':b.cfg['boot']='order=scsi0;ide2'
    elif mutation=='agent_missing':del b.cfg['agent']
    else:b.cfg[mutation]='unexpected'
    with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_missing_or_wrong_iso_and_wrong_content(self):
  for field,value in [('ide2','none,media=cdrom'),('ide2','other.iso,media=cdrom'),('hash','0'*64),('bytes',0)]:
   c,b,s,e,a=self.setup_engine()
   if field=='ide2':b.cfg[field]=value
   else:
    d=b.snapshot()['iso'];d['sha256' if field=='hash' else 'bytes']=value;b.overrides['iso']=d
   with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_guest_agent_enabled(self):
  c,b,s,e,a=self.setup_engine();b.cfg['agent']='enabled=1'
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_pending_and_malformed_rows(self):
  for pending in ([{}],[{'key':'boot','value':'order=scsi0','pending':None}],[{'key':'boot','value':'wrong'}]):
   c,b,s,e,a=self.setup_engine();b.pending=pending
   with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_duplicate_conflicting_serial(self):
  c,b,s,e,a=self.setup_engine();b.cfg['scsi0']+=',serial=wrong'
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_wrong_host_boot_or_snapshot_origin(self):
  c,b,s,e,a=self.setup_engine();b.overrides['host_boot_id']='bbbbbbbb-cccc-dddd-eeee-ffffffffffff'
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_stale_or_future_snapshot(self):
  for beginning,end in ((0,1),(1_000_000_001,1_000_000_002)):
   c,b,s,e,a=self.setup_engine();b.overrides.update(began_us=beginning,ended_us=end)
   with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_malformed_duplicate_nonfinite_json(self):
  for raw in ('{"x":1,"x":2}','{"x":NaN}','{',b'\xff'):
   with self.assertRaises(M.Refusal):M.parse(raw)
 def test_stale_operator_approval(self):
  c,b,s,e,a=self.setup_engine();a['expires_at']='2026-11-06T20:59:59Z'
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
 def test_wrong_scope_source_review_or_missing_b_authority(self):
  c,b,s,e,a=self.setup_engine('B')
  for field,value in [('stage',4),('purpose','root_boot'),('source_sha256','3'*64),('review_sha256','bad'),('forced_stop_authorization',None)]:
   d=copy.deepcopy(a);d[field]=value
   with self.assertRaises(M.Refusal):e.prepare(d,SESSION)
 def test_no_bool_integer_coercion(self):
  c,b,s,e,a=self.setup_engine();b.cfg['protection']=True
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
class SetupTests(NoEffects):
 def test_vm_running_before_any_timer(self):
  c,b,s,e,a=self.setup_engine();b.status='running'
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
  self.assertFalse(b.units)
 def test_timer_creation_failure_and_owned_rollback(self):
  c,b,s,e,a=self.setup_engine();b.fail['create_deadline']=OSError('fixture')
  with self.assertRaises(OSError):e.prepare(a,SESSION)
  self.assertFalse(s.is_armed());self.assertEqual(b.units['grace']['timer']['active'],'inactive');self.assertEqual(s.phase(),'SETUP_FAILED_NO_START')
 def test_failed_rollback_quarantines_without_start(self):
  c,b,s,e,a=self.setup_engine();b.fail.update(create_deadline=OSError(),cancel_grace=OSError())
  with self.assertRaises(OSError):e.prepare(a,SESSION)
  row=s.events[-1];self.assertTrue(row['data']['orphan_or_unknown_units'])
  with self.assertRaises(M.Refusal):e.start()
 def test_canary_failure_is_not_exec_proof(self):
  c,b,s,e,a=self.setup_engine();b.canary_ok=False
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
  self.assertFalse(b.units)
 def test_unit_name_collision_does_not_cancel_foreign_unit(self):
  c,b,s,e,a=self.setup_engine();b.collisions.add(M.names(SESSION)['grace']+'.timer')
  with self.assertRaises(M.Refusal):e.prepare(a,SESSION)
  self.assertFalse(any(x[0].startswith('cancel_') for x in b.actions))
 def test_timer_created_but_inactive_before_start(self):
  c,b,s,e,a=self.armed();b.units['deadline']['timer']['active']='inactive'
  with self.assertRaises(M.Refusal):e.start()
  self.assertNotIn(('start',164),b.actions)
 def test_service_exec_or_extra_command_mismatch(self):
  for field,value in [('type','simple'),('argv',['/bin/sh']),('extra_commands',True),('user','nobody')]:
   c,b,s,e,a=self.armed();b.units['grace']['service'][field]=value
   with self.assertRaises(M.Refusal):e.start()
 def test_deadline_wrong_clock_or_late_timer(self):
  for field,value in [('wake',False),('accuracy_us',60_000_000),('next_us',2_000_000_000),('last_trigger_us',1)]:
   c,b,s,e,a=self.armed();b.units['grace']['timer'][field]=value
   with self.assertRaises(M.Refusal):e.start()
 def test_changed_digest_before_start(self):
  c,b,s,e,a=self.armed();b.cfg['digest']='b'*40
  with self.assertRaises(M.Refusal):e.start()
 def test_changed_config_same_digest_refused(self):
  c,b,s,e,a=self.armed();b.cfg['cpu']='different'
  with self.assertRaises(M.Refusal):e.start()
 def test_vm_running_before_timer_verification(self):
  c,b,s,e,a=self.armed();b.status='running'
  with self.assertRaises(M.Refusal):e.start()
 def test_duplicate_start_or_two_operator_attempts_no_renewal(self):
  c,b,s,e,a=self.armed();e.start()
  with self.assertRaises(M.Refusal):e.start()
  with self.assertRaises(M.Refusal):e.prepare(a,'2'*32)
  self.assertEqual(b.actions.count(('start',164)),1)
 def test_lost_start_ack_still_consumes_generation(self):
  c,b,s,e,a=self.armed();b.fail['start']=TimeoutError()
  with self.assertRaises(TimeoutError):e.start()
  with self.assertRaises(M.Refusal):e.start()
  self.assertEqual(s.phase(),'START_UNKNOWN_KEEP_FENCE')
 def test_host_reboot_invalidates_armed_session(self):
  c,b,s,e,a=self.armed();c.boot_id='bbbbbbbb-cccc-dddd-eeee-ffffffffffff'
  with self.assertRaises(M.Refusal):e.start()
  c.value=s.plan()['deadline_us']
  with self.assertRaises(M.Refusal):e.expire('deadline')
 def test_late_setup_or_rearm_does_not_extend_deadline(self):
  c,b,s,e,a=self.armed();deadline=s.plan()['deadline_us'];c.advance(M.MAX_START_DELAY_US+1)
  with self.assertRaises(M.Refusal):e.start()
  self.assertEqual(s.plan()['deadline_us'],deadline)
 def test_evidence_failure_during_setup_never_starts(self):
  c,b,s,e,a=self.setup_engine();s.fail_write=True
  with self.assertRaises(OSError):e.prepare(a,SESSION)
  self.assertFalse(b.units)
class ExpirationTests(NoEffects):
 def active(self,policy='A'):
  c,b,s,e,a=self.armed(policy);e.start();return c,b,s,e,a
 def test_policy_a_graceful_stops_without_force(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us'];r=e.expire('grace')
  self.assertEqual(r['status'],'STOPPED_OBSERVED');self.assertFalse(r['expiration_guaranteed']);self.assertNotIn(('force_SIMULATED_ONLY',164),b.actions)
 def test_policy_a_refused_acpi_is_hard_blocker(self):
  c,b,s,e,a=self.active();b.grace_stops=False;c.value=s.plan()['grace_us']
  self.assertEqual(e.expire('grace')['status'],'TERMINATION_UNPROVEN');c.value=s.plan()['deadline_us']
  r=e.expire('deadline');self.assertEqual(r['status'],'POLICY_A_NO_EXPIRATION_GUARANTEE');self.assertEqual(b.status,'running')
 def test_graceful_command_timeout_is_not_stop_proof(self):
  c,b,s,e,a=self.active();b.fail['graceful']=subprocess.TimeoutExpired('fixture',15);c.value=s.plan()['grace_us']
  self.assertEqual(e.expire('grace')['status'],'TERMINATION_UNPROVEN')
 def test_service_failure_does_not_disarm_independent_deadline(self):
  c,b,s,e,a=self.active();b.fail['graceful']=OSError();c.value=s.plan()['grace_us'];e.expire('grace')
  self.assertEqual(b.units['deadline']['timer']['active'],'active');c.value=s.plan()['deadline_us']
  self.assertIn('NO_EXPIRATION',e.expire('deadline')['status'])
 def test_policy_b_distinct_authorized_force_model_only(self):
  c,b,s,e,a=self.active('B');b.grace_stops=False;c.value=s.plan()['grace_us'];e.expire('grace')
  c.value=s.plan()['deadline_us'];r=e.expire('deadline')
  self.assertEqual(b.status,'stopped');self.assertTrue(r['simulated']);self.assertFalse(r['forced_stop_runtime_enabled']);self.assertEqual(b.actions.count(('force_SIMULATED_ONLY',164)),1)
 def test_unauthorized_force_model_refused(self):
  c,b,s,e,a=self.active('B');b.force_grant=None;c.value=s.plan()['deadline_us']
  self.assertEqual(e.expire('deadline')['status'],'TERMINATION_UNPROVEN');self.assertNotIn(('force_SIMULATED_ONLY',164),b.actions)
 def test_current_runtime_b_cannot_prepare(self):
  c,b,s,e,a=self.setup_engine('B');b.simulated=False
  with self.assertRaisesRegex(M.Refusal,'B_runtime_disabled'):e.prepare(a,SESSION)
  self.assertFalse(b.units)
 def test_early_timer_cannot_act(self):
  c,b,s,e,a=self.active()
  with self.assertRaises(M.Refusal):e.expire('grace')
  self.assertNotIn(('graceful',164),b.actions)
 def test_too_late_trigger_never_reports_on_time_success(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us']+M.MAX_LATENESS_US+1
  self.assertEqual(e.expire('grace')['status'],'STOPPED_LATE')
 def test_deadline_beyond_stop_by_not_success(self):
  c,b,s,e,a=self.active('B');c.value=s.plan()['stop_by_us']+1
  self.assertEqual(e.expire('deadline')['status'],'STOPPED_LATE')
 def test_natural_poweroff_before_expiration_has_no_action(self):
  c,b,s,e,a=self.active();b.status='stopped';c.value=s.plan()['grace_us'];e.expire('grace')
  self.assertNotIn(('graceful',164),b.actions)
 def test_lost_grace_ack_and_natural_poweroff_race(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us']
  def race():b.status='stopped';raise OSError('lost_ack')
  b.graceful=race;self.assertEqual(e.expire('grace')['status'],'STOPPED_OBSERVED')
 def test_wrong_vm_or_digest_at_expiration_never_acts(self):
  for variation in ('vmid','digest'):
   c,b,s,e,a=self.active();c.value=s.plan()['grace_us']
   if variation=='vmid':b.overrides['vmid']=163
   else:b.cfg['digest']='b'*40
   with self.assertRaises(M.Refusal):e.expire('grace')
   self.assertNotIn(('graceful',164),b.actions)
 def test_temporary_interface_error_before_action_is_retryable(self):
  c,b,s,e,a=self.active('B');c.value=s.plan()['deadline_us'];b.fail['snapshot']=OSError()
  with self.assertRaises(OSError):e.expire('deadline')
  del b.fail['snapshot'];self.assertEqual(e.expire('deadline')['status'],'STOPPED_OBSERVED')
 def test_completed_duplicate_no_second_command(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us'];e.expire('grace');e.expire('grace')
  self.assertEqual(b.actions.count(('graceful',164)),1)
 def test_failed_action_retry_is_bounded_without_extending(self):
  c,b,s,e,a=self.active();b.grace_stops=False;c.value=s.plan()['grace_us'];deadline=s.plan()['deadline_us']
  e.expire('grace');e.expire('grace')
  with self.assertRaises(M.Refusal):e.expire('grace')
  self.assertEqual(s.plan()['deadline_us'],deadline)
 def test_phase_concurrency_cannot_double_act(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us'];s.claim('grace')
  with self.assertRaises(M.Busy):e.expire('grace')
  self.assertNotIn(('graceful',164),b.actions);s.release('grace',False)
 def test_journal_failure_after_action_remains_incomplete(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us']
  def stop():b.status='stopped';s.fail_write=True
  b.graceful=stop;r=e.expire('grace');self.assertFalse(r['evidence_healthy']);self.assertFalse(r['expiration_guaranteed'])
 def test_claim_evidence_failure_is_blocker_not_pass(self):
  c,b,s,e,a=self.active();c.value=s.plan()['grace_us'];s.fail_write=True
  with self.assertRaises(OSError):e.expire('grace')
  self.assertEqual(b.units['deadline']['timer']['active'],'active')
class CleanupTests(NoEffects):
 def test_cannot_cancel_while_running(self):
  c,b,s,e,a=self.armed();e.start()
  with self.assertRaises(M.Refusal):e.cleanup()
  self.assertFalse(any(x[0].startswith('cancel_') for x in b.actions))
 def test_duplicate_cleanup_is_historical_no_action(self):
  c,b,s,e,a=self.armed();e.cleanup();before=list(b.actions);b.cfg['ide2']='none,media=cdrom'
  self.assertEqual(e.cleanup()['status'],'ALREADY_CLOSED_NO_ACTION');self.assertEqual(b.actions,before)
 def test_cleanup_interrupted_halfway_can_resume(self):
  c,b,s,e,a=self.armed();b.fail['cancel_deadline']=OSError()
  with self.assertRaises(OSError):e.cleanup()
  self.assertEqual(s.phase(),'CLOSING');self.assertEqual(b.units['deadline']['timer']['active'],'active')
  del b.fail['cancel_deadline'];self.assertEqual(e.cleanup()['status'],'CLOSED_EVIDENCE_RETAINED')
 def test_timer_fires_during_cleanup_no_other_vm_or_force(self):
  c,b,s,e,a=self.armed();c.value=s.plan()['deadline_us'];seen=[]
  b.stop_callback=lambda phase:seen.append(e.expire('deadline')['status']) if phase=='grace' else None
  e.cleanup();self.assertTrue(seen);self.assertFalse(any(x[0] in ('graceful','force_SIMULATED_ONLY') for x in b.actions))
 def test_retire_requires_new_approval_and_preserves_history(self):
  c,b,s,e,a=self.armed();e.cleanup()
  with self.assertRaises(M.Refusal):e.retire(a)
  new=copy.deepcopy(a);new['operator_reference']='NEW-FINITE-REVIEW';r=e.retire(new)
  self.assertEqual(r['status'],'RETIRED_REGISTRY_EVIDENCE_PRESERVED');self.assertEqual(len(s.history),1)
  e.prepare(new,'2'*32);self.assertEqual(s.phase(),'ARMED')
 def test_cannot_retire_unclosed_or_live_units(self):
  c,b,s,e,a=self.armed();new=copy.deepcopy(a);new['operator_reference']='NEW'
  with self.assertRaises(M.Refusal):e.retire(new)
  e.cleanup();b.units['grace']['timer']['active']='active'
  with self.assertRaises(M.Refusal):e.retire(new)

class AdditionalLifecycleTests(NoEffects):
 def test_host_reboot_while_session_active_never_resumes_lease(self):
  c,b,s,e,a=self.armed();e.start();before=len(b.actions);c.boot_id='bbbbbbbb-cccc-dddd-eeee-ffffffffffff';c.value=s.plan()['deadline_us']
  with self.assertRaises(M.Refusal):e.expire('deadline')
  with self.assertRaises(M.Refusal):e.start()
  self.assertEqual(len(b.actions),before)
 def test_manager_loses_units_verify_fails_without_claiming_survival(self):
  c,b,s,e,a=self.armed();e.start();b.units.clear()
  with self.assertRaises(KeyError):e.verify()
  self.assertFalse(e.receipt(s.plan(),'MANAGER_STATE_UNVERIFIED')['expiration_guaranteed'])
 def test_observe_preserves_failed_service_state_without_qualification(self):
  c,b,s,e,a=self.armed();e.start();b.units['grace']['service'].update(result='exit-code',active='failed',sub='failed')
  r=e.observe();self.assertEqual(r['units']['grace']['service']['result'],'exit-code');self.assertEqual(r['observed_vm_status'],'running');self.assertFalse(r['live_qualification'])
 def test_completed_lease_late_callback_cannot_touch_newly_started_vm(self):
  c,b,s,e,a=self.armed();e.cleanup();b.status='running';before=list(b.actions);c.value=s.plan()['deadline_us']
  self.assertEqual(e.expire('deadline')['status'],'ALREADY_CLOSED_NO_ACTION');self.assertEqual(b.actions,before)

class AuthorizationLifetimeTests(NoEffects):
 def test_existing_callback_does_not_demand_a_second_full_lease_window(self):
  c=sim.FakeClock();a=sim.approval(c,SOURCE);a['expires_at']='2026-11-06T21:11:00Z'
  M.validate_approval(a,c.utc(),c.boot_id,SOURCE)
  c.wall+=dt.timedelta(seconds=540)
  self.assertTrue(M.validate_approval(a,c.utc(),c.boot_id,SOURCE,require_full_window=False))
  with self.assertRaises(M.Refusal):M.validate_approval(a,c.utc(),c.boot_id,SOURCE)
 def test_expired_callback_authorization_is_not_extended(self):
  c=sim.FakeClock();a=sim.approval(c,SOURCE);c.wall=dt.datetime(2026,11,6,22,0,tzinfo=dt.timezone.utc)
  with self.assertRaises(M.Refusal):M.validate_approval(a,c.utc(),c.boot_id,SOURCE,require_full_window=False)
