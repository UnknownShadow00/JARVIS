import copy,gzip,io,os,tempfile,time,unittest
from unittest.mock import patch
from pathlib import Path
import packet as p,binding as b,results,bounded as bound,local_gate as gate
from common import decode,canonical,sha
import fixtures as f

NSS=b'passwd: files\ngroup: files\ninitgroups: files\nsudoers: files\nhosts: files\nnetgroup: files\n'
PASSWD=b'root:x:0:0:root:/root:/usr/sbin/nologin\nnobody:x:65534:65534:nobody:/nonexistent:/usr/sbin/nologin\n'
GROUP=b'root:x:0:\nnogroup:x:65534:\n'

class Regression(unittest.TestCase):
 def test_full_synthetic_twelve(self):
  r,a=f.record();self.assertEqual(self.validate(r,a)['status'],'PASS_SYNTHETIC_ONLY')
 def validate(self,r,a):return results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256='e'*64)
 def reject(self,mutate):
  r,a=f.record();mutate(r);r,a=f.seal(r)
  with self.assertRaises(ValueError):self.validate(r,a)
 def test_local_nss_positive(self):self.assertEqual(gate.nss_gate(NSS)['kind'],'LOCAL_FILES_NSS_ONLY')
 def test_local_identity_positive(self):self.assertEqual(gate.local_identity(PASSWD,GROUP)['uid'],65534)
 def test_allowlisted_runtime_environment(self):self.assertTrue(gate.runtime_environment({**gate.SAFE_ENV,'INVOCATION_ID':'a'*32}))
 def test_bounded_gzip_valid(self):
  x=gzip.compress(bytes(range(256))*20);self.assertEqual(bound.gunzip_bounded(x,8192,time.monotonic()+2),bytes(range(256))*20)
 def test_bounded_gzip_bomb(self):
  with self.assertRaises(ValueError):bound.gunzip_bounded(gzip.compress(b'A'*2000000),8388608,time.monotonic()+2)
 def test_bounded_gzip_truncated(self):
  with self.assertRaises(ValueError):bound.gunzip_bounded(gzip.compress(b'hello')[:-1],8192,time.monotonic()+2)
 def test_bounded_gzip_malformed(self):
  with self.assertRaises(ValueError):bound.gunzip_bounded(b'X'*100,8192,time.monotonic()+2)
 def test_bounded_gzip_compressed_oversize(self):
  with self.assertRaises(ValueError):bound.gunzip_bounded(b'X'*(1048576+1),8192,time.monotonic()+2)
 def test_bounded_stream_partial_reads(self):
  class Partial(io.BytesIO):
   def read(self,n):return super().read(min(n,3))
  self.assertEqual(bound.read_stream(Partial(b'1234567'),7,time.monotonic()+2,expected_size=7),b'1234567')
 def test_bounded_stream_truncated(self):
  with self.assertRaises(ValueError):bound.read_stream(io.BytesIO(b'a'),5,time.monotonic()+2,expected_size=5)
 def test_bounded_stream_oversize(self):
  with self.assertRaises(ValueError):bound.read_stream(io.BytesIO(b'abcdef'),5,time.monotonic()+2)
 def test_bounded_stream_memory_failure(self):
  class Bad:
   def read(self,n):raise MemoryError()
  with self.assertRaises(ValueError):bound.read_stream(Bad(),5,time.monotonic()+2)
 def test_bounded_stream_deadline_before_read(self):
  class Bad:
   def read(self,n):raise AssertionError('read after deadline')
  with self.assertRaises(ValueError):bound.read_stream(Bad(),5,0,clock=lambda:1)
 def test_fd_oversize_before_read(self):
  with tempfile.TemporaryFile() as file:
   file.write(b'abcdef');file.flush();file.seek(0)
   with patch.object(bound,'read_stream',side_effect=AssertionError('read before size gate')):
    with self.assertRaises(ValueError):bound.read_fd(file.fileno(),5,time.monotonic()+2,owner=os.getuid())
 def test_fd_exact_hash_and_type(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'input';path.write_bytes(b'hello');path.chmod(0o600)
   with path.open('rb') as file:self.assertEqual(bound.read_fd(file.fileno(),5,time.monotonic()+2,owner=os.getuid(),expected_sha=sha(b'hello')),b'hello')
 def test_fd_changed_during_read(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'input';path.write_bytes(b'hello');path.chmod(0o600)
   original=bound.read_stream
   def mutate(*a,**kw):
    value=original(*a,**kw);path.write_bytes(b'changed');return value
   with path.open('rb') as file,patch.object(bound,'read_stream',mutate):
    with self.assertRaises(ValueError):bound.read_fd(file.fileno(),8,time.monotonic()+2,owner=os.getuid())
 def test_fd_writable_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'input';path.write_bytes(b'hello');path.chmod(0o666)
   with path.open('rb') as file:
    with self.assertRaises(ValueError):bound.read_fd(file.fileno(),8,time.monotonic()+2,owner=os.getuid())
 def test_cleanup_interruption_and_duplicate(self):
  plan,obs=f.ownership();self.assertEqual(len(p.cleanup_argv('b'*32,'success',plan,dict(obs))),2)
  obs['states']=['inactive','active'];self.assertEqual(len(p.cleanup_argv('b'*32,'success',plan,dict(obs))),1)
  obs['states']=['inactive','inactive'];self.assertEqual(p.cleanup_argv('b'*32,'success',plan,dict(obs)),[]);self.assertEqual(p.cleanup_argv('b'*32,'success',plan,dict(obs)),[])
 def test_expired_cleanup_not_implicitly_extended(self):
  plan,obs=f.ownership();obs['sample']=f.sample(2700)
  with self.assertRaises(ValueError):p.cleanup_argv('b'*32,'success',plan,dict(obs))
 def test_rearm_a_firing_with_complete_binding_fails(self):
  r,a=f.record();row=r['cases']['rearm-a'];success=r['cases']['success'];row['events']=success['events']
  r,a=f.seal(r)
  with self.assertRaises(ValueError):self.validate(r,a)
 def test_tampered_artifact_bytes(self):
  r,a=f.record();a['cases/success.json']+=b' '
  with self.assertRaises(ValueError):self.validate(r,a)
 def test_resealed_tampering_external_pin(self):
  r,a=f.record();expected=r['evidence_manifest_sha256'];r['cases']['success']['extra']='changed';r,a=f.seal(r)
  with self.assertRaises(ValueError):results.validate(r,a,expected_manifest_sha256=expected,expected_packet_manifest_sha256='e'*64)
 def test_duplicate_json_key(self):
  with self.assertRaises(ValueError):decode(b'{"x":1,"x":2}')
 def test_timeout_receipt_is_failure(self):
  plan,obs=f.ownership();env=p.command_envelope(plan['argv'],'create',f.session(),f.sample());r=f.receipt(plan,'create',plan['argv'],120);r['timeout']=True
  with self.assertRaises(ValueError):p.command_receipt(env,r)
 def test_command_reserve_at_expiry(self):
  with self.assertRaises(ValueError):p.command_envelope(['/usr/bin/systemctl'],'stop',f.session(),f.sample(2695))
 def test_minimal_command_environment(self):
  plan,obs=f.ownership();self.assertEqual(p.command_envelope(plan['argv'],'create',f.session(),f.sample())['environment'],gate.SAFE_ENV)
 def test_manager_environment_secret_not_echoed(self):
  with self.assertRaises(ValueError) as c:gate.environment_gate({'SECRET':'do-not-log'}, {})
  self.assertNotIn('do-not-log',str(c.exception));self.assertNotIn('SECRET',str(c.exception))

# Each generated method is one uniquely named test, no subtest count inflation.
def add(name,call):
 def run(self):call(self)
 setattr(Regression,'test_'+name,run)
for label,value in [('sss',b'sss'),('ldap',b'ldap'),('nis',b'nis'),('compat',b'compat'),('systemd',b'systemd'),('dns',b'dns'),('actions',b'files [SUCCESS=return]'),('duplicate',b'files\npasswd: files'),('missing',b'')]:
 def run(self,value=value):
  raw=NSS.replace(b'passwd: files',b'passwd: '+value)
  with self.assertRaises(ValueError):gate.nss_gate(raw)
 add('nss_'+label,run)
for label,mut in {
 'missing_callback':lambda r:r['cases']['success']['events'].pop(),
 'wrong_callback_uid':lambda r:r['cases']['success']['events'][1]['payload'].update(euid=0),
 'missing_callback_boot':lambda r:r['cases']['success']['events'][1]['payload'].pop('host_boot_id'),
 'old_callback_invocation':lambda r:r['cases']['rearm-b']['events'][1].update(invocation_id='0'*32),
 'old_callback_generation':lambda r:r['cases']['rearm-b']['events'][0]['payload']['binding'].update(generation='0'*64),
 'wrong_timer_pair':lambda r:r['cases']['success']['final']['timer'].update(Unit='foreign.service'),
 'incomplete_raw_show':lambda r:r['cases']['success']['final'].update(raw_timer='Id=x\n'),
 'missing_boot':lambda r:r['cases']['success']['final'].pop('boot_id'),
 'wrong_boot':lambda r:r['cases']['success']['final'].update(boot_id='00000000-0000-0000-0000-000000000000'),
 'wrong_current_name':lambda r:r['cases']['success']['final'].update(name='foreign'),
 'stale_observation':lambda r:r['cases']['success']['final'].update(observed_boot_us=8000000000),
 'interrupted_cleanup':lambda r:r['cases']['success'].update(cleanup_complete=False),
 'missing_cleanup_receipt':lambda r:r['cases']['success']['receipts'].pop(),
 'foreign_cleanup_argv':lambda r:r['cases']['success']['receipts'][1]['argv'].__setitem__(-1,'foreign.timer'),
 'cleanup_active':lambda r:r['cases']['success']['final']['service'].update(ActiveState='active'),
 'cgroup_populated':lambda r:r['cases']['success']['final']['cgroup'].update(populated=1),
 'cgroup_missing':lambda r:r['cases']['success']['final'].pop('cgroup'),
 'cancel_late_journal':lambda r:r['cases']['cancel']['journal_interval'].update(from_boot_us=999999999999),
 'cancel_incomplete_journal':lambda r:r['cases']['cancel']['journal_interval'].update(complete=False),
 'cancel_late_time':lambda r:r['cases']['cancel'].update(cancel_boot_us=r['cases']['cancel']['plan']['deadline_boot_us']+1),
 'rearm_hides_failure':lambda r:r['cases']['rearm-a'].update(failures=['earlier-failure']),
 'success_negative_status':lambda r:r['cases']['success'].update(status='EXPECTED_NEGATIVE'),
 'clock_unknown':lambda r:r.update(clock_domain='UNKNOWN'),
 'source_mismatch':lambda r:r.update(stage2_sha256='0'*64),
 'missing_operator':lambda r:r.pop('operator'),
 'missing_authorization':lambda r:r.pop('authorization_reference'),
 'missing_case':lambda r:r['cases'].pop('timeout'),
 'duplicate_generation':lambda r:r['cases']['rearm-b'].update(plan=r['cases']['rearm-a']['plan']),
 'environment_unset_missing':lambda r:r['cases']['success']['final']['service'].pop('UnsetEnvironment'),
 'failure_kept':lambda r:r.update(failures=['failure']),
 'missing_failed_timer':lambda r:r['cases']['failedtimer'].pop('timer_failure'),
 'collision_no_refusal':lambda r:r['cases']['collision']['receipts'].pop(1),
 'callback_duplicate':lambda r:r['cases']['success']['events'].append(r['cases']['success']['events'][-1]),
}.items():add(label,lambda self,mut=mut:self.reject(mut))

class Extended(unittest.TestCase):
 def test_first_action_exact_audit_array(self):
  import catalog,json
  original=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS/tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r1/FIRST-SUPERVISED-ACTION.json')
  self.assertEqual(catalog.build()['read']['R01-clock'],json.loads(original.read_bytes())['argv'])
 def test_all_literal_future_bodies_compile_without_execution(self):
  import catalog
  cat=catalog.build()
  for argv in [*cat['read'].values(),cat['install']]:
   if '-c' in argv:compile(argv[argv.index('-c')+1],'<INERT>','exec')
 def test_catalog_no_identity_or_vm_executable(self):
  import catalog
  for argv in catalog.build()['read'].values():
   self.assertNotIn(Path(argv[0]).name,('getent','id','sudo','qm','pvesh','pvesm'))
 def test_exec_guard_exact_source_and_argv(self):
  from launch_guard import condition_argv,GUARD
  plan=p.plan(f.session(),f.sample(),'success',f.ident());argv=condition_argv(plan)
  self.assertIn(GUARD.encode().hex(),argv[5]);compile(GUARD,'<INERT_GUARD>','exec')
 def test_consumed_generation_denied(self):
  with self.assertRaises(ValueError):p.plan(f.session(),f.sample(),'success',f.ident(),used=[p.unit('b'*32,'success')])
 def test_collision_inventory_type_matrix(self):
  for bad in (None,'name',{},[1],['foreign.service'],[p.unit('b'*32,'success')+'.service']*2):
   with self.assertRaises(ValueError):p.plan(f.session(),f.sample(),'success',f.ident(),occupied=bad)
 def test_collision_complete_and_mutated_proofs(self):
  import collision
  s=f.session();name=p.unit(s['nonce'],'success');paths=['/run/systemd/transient','/etc/systemd/system'];proof=dict(boot_id=s['boot_id'],sample=f.sample(),unit_paths=paths,unit_paths_complete=True,namespace_inventory=[],units={})
  for unit in (name+'.timer',name+'.service',name+'-absent.service'):
   proof['units'][unit]=dict(raw_show=f.raw(dict(Id=unit,Names=unit,LoadState='not-found',ActiveState='inactive',SubState='dead',Job='0',FragmentPath='',SourcePath='',Transient='no')),show_exit=1,files={path+'/'+unit:dict(absent=True,errno='ENOENT') for path in paths})
  self.assertTrue(collision.absent(s,'success',proof))
  for mut in (lambda x:x.pop('boot_id'),lambda x:x.update(namespace_inventory=[name+'.timer']),lambda x:x['units'][name+'.timer']['files'].pop(paths[0]+'/'+name+'.timer'),lambda x:x['units'][name+'.timer'].update(raw_show='Id='+name+'.timer\n')):
   x=copy.deepcopy(proof);mut(x)
   with self.assertRaises(ValueError):collision.absent(s,'success',x)
 def test_artifact_loading_hash_and_symlink(self):
  import artifacts
  r,a=f.record()
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'cases').mkdir()
   for name,data in a.items():(root/name).write_bytes(data);(root/name).chmod(0o600)
   self.assertEqual(artifacts.load(root,r['evidence_manifest']),a)
   path=root/'cases/success.json';path.unlink();path.symlink_to('exit7.json')
   with self.assertRaises(OSError):artifacts.load(root,r['evidence_manifest'])
 def test_privileged_group_and_duplicate_uid(self):
  with self.assertRaises(ValueError):gate.local_identity(PASSWD,GROUP+b'privileged:x:22:nobody\n')
  with self.assertRaises(ValueError):gate.local_identity(PASSWD+PASSWD,GROUP)
 def test_network_policy_attestation_blocked(self):
  review={k:True for k in ('all_includes_local','no_remote_policy','no_network_pam','no_custom_helpers','vm_authority_denied','credentials_denied','local_mounts_no_autofs','complete_inventory')};review.update(files={'/etc/nsswitch.conf':sha(NSS)},independent_review_sha256='d'*64)
  self.assertEqual(gate.policy_gate(NSS,PASSWD,GROUP,b'# default\n',review)['queries_authorized'],False)
  with self.assertRaises(ValueError):gate.policy_gate(NSS,PASSWD,GROUP,b'Plugin custom\n',review)
  review['no_remote_policy']=False
  with self.assertRaises(ValueError):gate.policy_gate(NSS,PASSWD,GROUP,b'',review)
 def test_unset_environment_not_sufficient(self):
  for extra in ('LD_PRELOAD','PYTHONPATH','SECRET','HOME'):
   with self.assertRaises(ValueError):gate.runtime_environment({**gate.SAFE_ENV,'INVOCATION_ID':'a'*32,extra:'hidden'})
 def test_cleanup_missing_raw_and_transitions(self):
  plan,obs=f.ownership()
  for states in (('active','activating'),('deactivating','inactive'),('unknown','inactive')):
   x=dict(obs);x=copy.deepcopy(x);x['timer']['ActiveState']=states[0];x['service']['ActiveState']=states[1];f.sync(x)
   with self.assertRaises(ValueError):p.cleanup_argv('b'*32,'success',plan,x)
 def test_callback_wrong_boot_with_expected_plan(self):
  r,a=f.record();row=r['cases']['success'];payload=copy.deepcopy(row['events'][1]['payload']);payload['host_boot_id']='00000000-0000-0000-0000-000000000000'
  with self.assertRaises(ValueError):p.outcome('success',callback_row=payload,result='success',code=1,status=0,deadline=row['plan']['deadline_boot_us'],expected=row['plan'])
 def test_rearm_a_direct_complete_context_cannot_fire(self):
  r,a=f.record();row=r['cases']['rearm-a'];payload=r['cases']['success']['events'][1]['payload']
  with self.assertRaises(ValueError):p.outcome('rearm-a',callback_row=payload,result='success',code=1,status=0,deadline=row['plan']['deadline_boot_us'],expected=row['plan'])
 def test_raw_journal_omitted_callback_rejected(self):
  r,a=f.record();r['cases']['success']['events']=r['cases']['success']['events'][:1];r,a=f.seal(r)
  with self.assertRaises(ValueError):results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256='e'*64)
 def test_raw_journal_wrong_epoch(self):
  r,a=f.record();row=r['cases']['success'];row['raw_journal']=row['raw_journal'].replace(row['plan']['boot_id'].replace('-',''),'0'*32);r,a=f.seal(r)
  with self.assertRaises(ValueError):results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256='e'*64)

class GuardTests(unittest.TestCase):
 def guard(self,second=150,uid=65534,extra=None,boot=None):
  import contextlib,datetime,json
  from launch_guard import GUARD,guard_binding
  plan=p.plan(f.session(),f.sample(),'success',f.ident());bound=guard_binding(plan)
  class Clock(datetime.datetime):
   @classmethod
   def now(cls,tz=None):return datetime.datetime(2031,2,3,10,tzinfo=datetime.timezone.utc)+datetime.timedelta(seconds=second)
  output=io.StringIO()
  with contextlib.ExitStack() as stack:
   for name in ('getuid','geteuid','getgid','getegid'):stack.enter_context(patch.object(os,name,return_value=uid))
   stack.enter_context(patch.object(os,'getgroups',return_value=[uid]));stack.enter_context(patch.dict(os.environ,{**gate.SAFE_ENV,'INVOCATION_ID':'a'*32,**(extra or {})},clear=True))
   stack.enter_context(patch.object(time,'clock_gettime_ns',return_value=f.sample(second)['boot_us']*1000))
   stack.enter_context(patch.object(datetime,'datetime',Clock));stack.enter_context(patch.object(Path,'read_text',return_value=boot or plan['boot_id']))
   stack.enter_context(patch.object(__import__('sys'),'argv',['synthetic',canonical(bound).hex()]));stack.enter_context(contextlib.redirect_stdout(output))
   code=0
   try:exec(compile(GUARD,'<SYNTHETIC_GUARD_ONLY>','exec'),{})
   except SystemExit as exc:code=exc.code
  return code,output.getvalue()
 def test_guard_positive_synthetic(self):self.assertEqual(self.guard()[0],0)
 def test_guard_expired(self):self.assertEqual(self.guard(second=2700)[0],255)
 def test_guard_insufficient_runtime_reserve(self):self.assertEqual(self.guard(second=2690)[0],255)
 def test_guard_wrong_uid(self):self.assertEqual(self.guard(uid=0)[0],255)
 def test_guard_environment_secret_redacted(self):
  code,out=self.guard(extra={'SECRET':'never-print-this'});self.assertEqual(code,255);self.assertNotIn('never-print-this',out)
 def test_guard_wrong_boot(self):self.assertEqual(self.guard(boot='00000000-0000-0000-0000-000000000000')[0],255)
