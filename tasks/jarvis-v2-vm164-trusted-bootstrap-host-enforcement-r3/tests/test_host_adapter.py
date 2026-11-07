"""Independent-interface primitives tested with mocked Popen/private file fixtures."""
import copy,contextlib,datetime as dt,io,json,os,stat,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch,MagicMock
T=Path(__file__).resolve().parents[1];sys.path.insert(0,str(T/'src'))
import model as M,store as S,sim,host_adapter as H,systemd_codec as C,preflight as P
import cli
from test_enforcement import NoEffects,SESSION,SOURCE

def prereq():
 d={'host':copy.deepcopy(P.EXPECTED),'source_sha256':SOURCE,'binaries':{n:{'root_owned_chain':True,'regular_resolved_binary':True,'not_group_or_other_writable':True,'sha256':'4'*64} for n in P.BINARIES}}
 for k in ('python_supported','qemu_server_version_captured','qemu_version_captured','pve_command_help_reviewed',
           'systemd_show_codec_qualified','boottime_deadline_readback_qualified','wake_system_qualified',
           'exec_failure_observed','manager_reexec_behavior_qualified','reboot_invalidation_qualified',
           'journal_retention_qualified','no_other_controller_autostarts_vm164','private_install_and_state_custody','stage2_callbacks_unprivileged_verified'):d[k]=True
 d['timer_readback_clock_domain']='CLOCK_MONOTONIC';d['paired_clock_conversion_qualified']=True
 d['package_versions']={'pve-manager':'9.2.5','qemu-server':'9.fixture','pve-qemu-kvm':'10.fixture','systemd':'257.13-1~deb13u1'}
 d['stage2_callback_uid']=12345
 return d

def exec_text(argv):return '{ path=/usr/bin/python3 ; argv[]='+' '.join(argv)+' ; ignore_errors=no ; start_time=[n/a] ; stop_time=[n/a] ; pid=0 ; code=(null) ; status=0/0 }'
def show_fixture(plan,phase):
 n=plan['names'][phase];v=str(plan[phase+'_us']//1_000_000)+'s'
 t={'Id':n+'.timer','LoadState':'loaded','ActiveState':'active','SubState':'waiting','Transient':'yes','Result':'success',
    'Unit':n+'.service','WakeSystem':'yes','AccuracyUSec':'1us','RandomizedDelayUSec':'0','LastTriggerUSecMonotonic':'0',
    'NextElapseUSecMonotonic':v,'TimersMonotonic':'{ OnBootUSec='+v+' ; next_elapse='+v+' }','RemainAfterElapse':'yes'}
 s={'Id':n+'.service','LoadState':'loaded','ActiveState':'inactive','SubState':'dead','Transient':'yes','Result':'success',
    'Type':'exec','User':'root','Group':'root','Restart':'no','KillMode':'control-group',
    'RuntimeMaxUSec':'45s' if phase=='grace' else '30s','TimeoutStopUSec':'5s','ExecStart':exec_text(M.worker_argv(plan['session'],phase)),
    'ExecStartPre':'','ExecStartPost':'','ExecCondition':'','InvocationID':'','Environment':'','EnvironmentFiles':'',
    'UMask':'0077','MemoryMax':'134217728','TasksMax':'16','SendSIGKILL':'yes','StandardInput':'null','StandardOutput':'journal',
    'StandardError':'journal','TimeoutStartUSec':'10s'}
 def raw(d):return ''.join(k+'='+v+'\n' for k,v in d.items()).encode()
 return raw(t),raw(s)
class CodecTests(NoEffects):
 def test_timespan_exact_microseconds(self):
  for text,want in [('1us',1),('1ms',1000),('1min 2.5s',62_500_000),('1h 2min 3.000001s',3_723_000_001),('0',0)]:self.assertEqual(C.usec(text),want)
 def test_unsupported_duration_refuses(self):
  for text in ('infinity','NaN','-1s','1ms junk','1.0000001s','1 months',''):
   with self.assertRaises(M.Refusal):C.usec(text)
 def test_complete_synthetic_show_codec(self):
  c=sim.FakeClock();b=sim.FixtureBackend(c);s=S.MemoryStore();e=M.Engine(b,s,c,SOURCE);e.prepare(sim.approval(c,SOURCE),SESSION)
  plan=s.plan();t,sv=show_fixture(plan,'grace')
  self.assertTrue(M.verify_unit(plan,'grace',{'timer':C.normalize_deadline(C.timer(t),'CLOCK_MONOTONIC',0,0),'service':C.service(sv),'host_boot_id':c.boot_id,'observed_us':c.us()},c.us()))
 def test_duplicate_properties_refuse(self):
  with self.assertRaises(M.Refusal):C.properties(b'Id=one\nId=two\n')
 def test_execstart_multiple_commands_shell_or_escaping_refuse(self):
  for text in (exec_text(['/bin/sh','-c','echo']),exec_text(M.worker_argv(SESSION,'grace'))+' '+exec_text(M.worker_argv(SESSION,'grace')),exec_text(['/usr/bin/python3','bad\\x20path'])):
   with self.assertRaises(M.Refusal):C.argv_property(text)
 def test_timer_command_absolute_from_host_boottime_not_literal_offset(self):
  p={'session':SESSION,'names':M.names(SESSION),'grace_us':1_540_000_000};argv=C.timer_command(p,'grace')
  self.assertIn('--on-boot=1540.000000s',argv);self.assertNotIn('--on-boot=540s',argv)
  self.assertIn('--timer-property=WakeSystem=yes',argv);self.assertNotIn('--no-block',argv);self.assertNotIn('--collect',argv)
 def test_timer_property_missing_no_loose_default(self):
  with self.assertRaises(M.Refusal):C.timer(b'Id=one.timer\n')
class NativeTransportTests(NoEffects):
 def runner(self):return H.Runner(object.__new__(H.Permit),clock=sim.FakeClock())
 def test_only_fixed_vmid_shutdown_without_force_or_bypass(self):
  r=self.runner();self.assertTrue(r.allowed(['/usr/sbin/qm','shutdown','164','--timeout','15','--forceStop','0']))
  for cmd in (['/usr/sbin/qm','shutdown','163'],['/usr/sbin/qm','stop','164'],['/usr/sbin/qm','shutdown','164','--skiplock','1'],['/usr/sbin/qm','unlock','164']):self.assertFalse(r.allowed(cmd))
 def test_shell_string_and_arbitrary_command_refuse(self):
  for cmd in ('qm start 164',['/bin/sh','-c','qm start 164'],['/usr/sbin/qm','start','164;stop 163']):
   with self.assertRaises(M.Refusal):self.runner().run(cmd)
 def test_current_runtime_force_is_unreachable(self):
  native=object.__new__(H.NativeBackend)
  with self.assertRaisesRegex(M.Refusal,'FORCED_STOP_BUILD_DISABLED'):native.force('e'*64)
 def test_other_node_or_vm_query_never_allowlisted(self):
  for endpoint in ('/nodes/pve/qemu/163/config','/nodes/other/qemu/164/config','/cluster/resources'):
   self.assertFalse(self.runner().allowed(['/usr/bin/pvesh','get',endpoint,'--output-format','json']))
 def test_timer_command_reconstruction_rejects_added_property(self):
  p={'session':SESSION,'names':M.names(SESSION),'grace_us':1_540_000_000};argv=C.timer_command(p,'grace')
  self.assertTrue(self.runner().allowed(argv));self.assertFalse(self.runner().allowed(argv+['--property=ExecStart=/bin/sh']))
 def test_timeout_kills_and_reaps_whole_child_group(self):
  p=MagicMock();p.pid=999999;p.communicate.side_effect=[subprocess.TimeoutExpired('fixture',2),(b'',b'')]
  with patch('subprocess.Popen',return_value=p),patch('os.killpg') as kill:
   with self.assertRaises(subprocess.TimeoutExpired):self.runner().run(['/usr/sbin/qm','start','164'])
  kill.assert_called_once_with(999999,H.signal.SIGKILL);self.assertEqual(p.communicate.call_count,2)
 def test_reap_timeout_does_not_loop(self):
  p=MagicMock();p.pid=999999;p.communicate.side_effect=[subprocess.TimeoutExpired('fixture',2),subprocess.TimeoutExpired('fixture',1)]
  with patch('subprocess.Popen',return_value=p),patch('os.killpg'):
   with self.assertRaises(subprocess.TimeoutExpired):self.runner().run(['/usr/sbin/qm','start','164'])
  self.assertEqual(p.communicate.call_count,2)
 def test_deadline_exhaustion_spawns_nothing(self):
  c=sim.FakeClock();r=H.Runner(object.__new__(H.Permit),c,budget=1);c.advance(1_000_001)
  with self.assertRaises(M.Refusal):r.run(['/usr/sbin/qm','start','164'])
 def test_native_source_authorize_denies_repository_path_before_commands(self):
  with patch.object(H.os,'getuid',return_value=0),patch.object(H.os,'geteuid',return_value=0):
   with self.assertRaisesRegex(M.Refusal,'reviewed_install_path'):H.authorize(str(T/'src/cli.py'))
 def test_native_authorization_binds_actual_prerequisite_hash(self):
  c=sim.FakeClock();a=sim.approval(c,SOURCE);a['kind']='reviewed_host_root';q=prereq();r={'source_sha256':SOURCE,'scope':'stage3_non_root_policy_A_only','stage2_record_sha256':a['stage2_record_sha256']}
  records={str(H.AUTH):M.canonical(a),str(H.PREREQ):M.canonical(q),str(H.REVIEW):M.canonical(r)}
  with patch.object(H.os,'getuid',return_value=0),patch.object(H.os,'geteuid',return_value=0),patch.object(H,'protected'),patch.object(H,'bounded_read',side_effect=lambda p,*_:records[str(p)]),patch.object(H,'source_digest',return_value=SOURCE),patch.object(H,'Clock',return_value=c):
   with self.assertRaisesRegex(M.Refusal,'stage2_record_hash_mismatch'):H.authorize(M.BASE+'/cli.py')
 def test_native_authorization_binds_actual_review_hash(self):
  c=sim.FakeClock();a=sim.approval(c,SOURCE);a['kind']='reviewed_host_root';q=prereq();a['stage2_record_sha256']=M.sha(M.canonical(q));r={'source_sha256':SOURCE,'scope':'stage3_non_root_policy_A_only','stage2_record_sha256':a['stage2_record_sha256']}
  records={str(H.AUTH):M.canonical(a),str(H.PREREQ):M.canonical(q),str(H.REVIEW):M.canonical(r)}
  with patch.object(H.os,'getuid',return_value=0),patch.object(H.os,'geteuid',return_value=0),patch.object(H,'protected'),patch.object(H,'bounded_read',side_effect=lambda p,*_:records[str(p)]),patch.object(H,'source_digest',return_value=SOURCE),patch.object(H,'Clock',return_value=c):
   with self.assertRaisesRegex(M.Refusal,'review_record_hash_mismatch'):H.authorize(M.BASE+'/cli.py')
class PrerequisiteAndCLITests(NoEffects):
 def test_missing_extra_paths_or_qualifications_are_not_assumed(self):
  q=prereq();self.assertFalse(P.assess(q,SOURCE)['missing']);del q['binaries']['/usr/bin/pvesh']
  r=P.assess(q,SOURCE);self.assertIn('binary_custody:/usr/bin/pvesh',r['missing']);self.assertFalse(r['root_boot_go'])
 def test_reported_host_versions_wrong(self):
  q=prereq();q['host']['systemd']='259';self.assertTrue(P.assess(q,SOURCE)['missing'])
 def test_fabricated_good_record_does_not_grant_live_authority(self):
  r=P.assess(prereq(),SOURCE);self.assertFalse(r['live_origin_verified']);self.assertFalse(r['host_checks_executed'])
 def test_default_cli_and_named_prepare_without_flag_are_dry_run(self):
  for action in ([],['prepare'],['worker','--phase','deadline'],['cleanup']):
   out=io.StringIO()
   with patch.object(sys,'argv',[str(T/'src/cli.py'),*action]),contextlib.redirect_stdout(out):self.assertEqual(cli.main(),0)
   self.assertEqual(json.loads(out.getvalue())['status'],'DRY_RUN_NO_ACTION')
 def test_conflicting_flags_refuse_before_host_authorization(self):
  with patch.object(sys,'argv',['cli','prepare','--dry-run','--execute-reviewed-host']),patch.object(cli,'authorize') as authorize:
   with self.assertRaises(M.Refusal):cli.main()
   authorize.assert_not_called()
class FileEvidenceTests(NoEffects):
 def setUp(self):
  super().setUp();self.tmp=tempfile.TemporaryDirectory(dir=T/'evidence');self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name);self.root.chmod(0o700)
 def prepared(self):
  c=sim.FakeClock();b=sim.FixtureBackend(c);s=S.FileStore(self.root);e=M.Engine(b,s,c,SOURCE);a=sim.approval(c,SOURCE)
  with s:e.prepare(a,SESSION)
  return c,b,s,e,a
 def test_two_simultaneous_operators_excluded(self):
  a=S.FileStore(self.root);b=S.FileStore(self.root)
  with a:
   with self.assertRaises(M.Busy):b.lock()
 def test_interrupted_registry_setup_blocks_reuse(self):
  S.exclusive(self.root/'active.json',M.canonical({'session':SESSION}))
  s=S.FileStore(self.root)
  with s:
   with self.assertRaises(M.Refusal):s.create({'session':'2'*32})
 def test_hash_chain_tamper_or_partial_write_refuses(self):
  c,b,s,e,a=self.prepared();p=s.directory()/'events.ndjson';raw=p.read_bytes();p.write_bytes(raw+b'{')
  with self.assertRaises(M.Refusal):s.records()
 def test_immutable_plan_tamper_refuses(self):
  c,b,s,e,a=self.prepared();p=s.directory()/'plan.json';p.write_bytes(b'{}')
  with self.assertRaises(M.Refusal):s.plan()
 def test_symlink_or_fifo_evidence_refused(self):
  p=self.root/'target';p.write_bytes(b'x');link=self.root/'link';link.symlink_to(p)
  with self.assertRaises(OSError):S.bounded_read(link)
  fifo=self.root/'fifo';os.mkfifo(fifo)
  with self.assertRaises(M.Refusal):S.bounded_read(fifo)
 def test_independent_worker_does_not_wait_on_operator_control_lock(self):
  c,b,s,e,a=self.prepared();b.status='running';c.value=s.plan()['grace_us']
  worker=S.FileStore(self.root);engine=M.Engine(b,worker,c,SOURCE)
  with s:self.assertEqual(engine.expire('grace')['status'],'STOPPED_OBSERVED')
 def test_worker_phase_lock_excludes_duplicate_and_releases_for_retry(self):
  c,b,s,e,a=self.prepared();other=S.FileStore(self.root)
  self.assertTrue(s.claim('grace'))
  with self.assertRaises(M.Busy):other.claim('grace')
  s.release('grace',False);self.assertTrue(other.claim('grace'));other.release('grace',True)
  self.assertFalse(s.claim('grace'))
 def test_retirement_renames_pointer_preserving_all_session_evidence(self):
  c,b,s,e,a=self.prepared();new=copy.deepcopy(a);new['operator_reference']='NEW-REVIEW'
  with s:
   e.cleanup();before=(self.root/'active.json').read_bytes();e.retire(new)
  self.assertFalse((self.root/'active.json').exists());self.assertEqual((self.root/SESSION/'retired-active.json').read_bytes(),before)
  self.assertTrue((self.root/SESSION/'events.ndjson').exists())
  with s:e.prepare(new,'2'*32)
  self.assertEqual(s.session(),'2'*32)
 def test_retirement_interrupted_before_rename_preserves_pointer(self):
  c,b,s,e,a=self.prepared();new=copy.deepcopy(a);new['operator_reference']='NEW-REVIEW'
  with s:
   e.cleanup()
   with patch.object(S.os,'rename',side_effect=OSError()):
    with self.assertRaises(OSError):e.retire(new)
  self.assertTrue((self.root/'active.json').exists());self.assertEqual(s.phase(),'CLOSED')
 def test_closed_is_absorbing_after_late_events(self):
  c,b,s,e,a=self.prepared()
  with s:e.cleanup()
  s.event('STOPPED_OBSERVED',{'late':True});self.assertEqual(s.phase(),'CLOSED')

class ClockAndRecoveryTests(NoEffects):
 def test_large_historical_suspend_offset_converts_without_assuming_same_clock(self):
  raw={'next_us':6_400_000_000}
  t=C.normalize_deadline(raw,'CLOCK_MONOTONIC',3_600_000_000,3_600_000_500)
  self.assertEqual(t['next_boot_min_us'],10_000_000_000);self.assertEqual(t['next_boot_max_us'],10_000_000_500)
 def test_boottime_readback_not_double_corrected(self):
  t=C.normalize_deadline({'next_us':10_000_000_000},'CLOCK_BOOTTIME',3_600_000_000,3_600_000_500)
  self.assertEqual(t['next_boot_min_us'],10_000_000_000);self.assertEqual(t['readback_offset_high_us'],0)
 def test_unknown_clock_or_suspend_during_capture_refuses(self):
  for domain,low,high in [('CLOCK_TAI',0,0),('CLOCK_MONOTONIC',0,1001),('CLOCK_MONOTONIC',-1001,0)]:
   with self.assertRaises(M.Refusal):C.normalize_deadline({'next_us':10_000_000},domain,low,high)
 def test_unknown_qualified_clock_is_prerequisite_blocker(self):
  q=prereq();q['timer_readback_clock_domain']=None
  self.assertIn('timer_readback_clock_domain',P.assess(q,SOURCE)['missing'])
 def test_missing_units_after_reboot_need_no_cancellation(self):
  b=object.__new__(H.NativeBackend);plan={'names':M.names(SESSION)}
  def show(name,_props):return ('Id='+name+'\nLoadState=not-found\nActiveState=inactive\nSubState=dead\n').encode()
  b._show=show;b.r=MagicMock();b.stop_own_units(plan,'grace');b.r.run.assert_not_called();self.assertTrue(b.units_inactive(plan,'grace'))
 def test_wrong_unit_identity_never_canceled(self):
  b=object.__new__(H.NativeBackend);b._show=lambda *_:b'Id=other-vm.service\nLoadState=loaded\nActiveState=inactive\nSubState=dead\n';b.r=MagicMock()
  with self.assertRaises(M.Refusal):b.stop_own_units({'names':M.names(SESSION)},'grace')
  b.r.run.assert_not_called()
 def test_stage2_canary_default_dry_and_root_callback_refused(self):
  import stage2_canary as cb
  out=io.StringIO()
  with patch.object(sys,'argv',['canary']),contextlib.redirect_stdout(out):self.assertEqual(cb.main(),0)
  self.assertEqual(json.loads(out.getvalue())['status'],'DRY_RUN_NON_ROOT_NON_VM_NO_ACTION')
  with patch.object(sys,'argv',['canary','--approved-nonvm-callback']),patch.object(cb.os,'getuid',return_value=0),patch.object(cb.os,'geteuid',return_value=0):
   with self.assertRaisesRegex(ValueError,'must_not_be_root'):cb.main()

class FinalPrerequisiteTests(NoEffects):
 def test_runtime_package_change_duplicate_or_truncated_output_blocks(self):
  expected=prereq()['package_versions'];raw=''.join(k+'='+v+'\n' for k,v in expected.items()).encode()
  self.assertEqual(P.runtime_packages(raw,expected),expected)
  for bad in (raw.replace(b'9.2.5',b'9.2.6'),raw+b'systemd=257.13-1~deb13u1\n',raw.splitlines()[0]):
   with self.assertRaises(M.Refusal):P.runtime_packages(bad,expected)
 def test_package_command_is_fixed_readonly_metadata(self):
  r=H.Runner(object.__new__(H.Permit),clock=sim.FakeClock());self.assertTrue(r.allowed(P.PACKAGE_COMMAND))
  self.assertFalse(r.allowed(P.PACKAGE_COMMAND+['unrelated-package']))
 def test_unprivileged_callback_proof_is_required(self):
  q=prereq();q['stage2_callback_uid']=0
  self.assertIn('stage2_callback_must_be_verified_nonroot_uid',P.assess(q,SOURCE)['missing'])
 def test_shared_worker_budget_cannot_restart_after_authorization(self):
  c=sim.FakeClock();absolute=c.us()+25_000_000;c.advance(10_000_000)
  r=H.Runner(object.__new__(H.Permit),c,budget=25,deadline_us=absolute)
  self.assertEqual(r.end,absolute)
 def test_weakened_resource_readback_and_boolean_numbers_reject(self):
  c=sim.FakeClock();b=sim.FixtureBackend(c);s=S.MemoryStore();e=M.Engine(b,s,c,SOURCE);e.prepare(sim.approval(c,SOURCE),SESSION)
  for k,v in [('umask','0000'),('memory_max','infinity'),('stdin','tty')]:
   proof=b.unit_proof(s.plan(),'grace');proof['service'][k]=v
   with self.assertRaises(M.Refusal):M.verify_unit(s.plan(),'grace',proof,c.us())
  proof=b.unit_proof(s.plan(),'grace');proof['timer']['accuracy_us']=True
  with self.assertRaises(M.Refusal):M.verify_unit(s.plan(),'grace',proof,c.us())
