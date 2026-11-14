"""Independent adversarial assertions. A failed assertion is a remaining R2 defect.

Uses the published, clearly SYNTHETIC 12-case record as a valid seed. Every
mutated case is rehashed so probes test semantic validation, not broken digests.
No host command body, NSS/credential query or child process is executed.
"""
import copy,datetime,gzip,hashlib,io,json,os,tempfile,time,unittest
from pathlib import Path
from unittest.mock import patch
import packet as p,binding as b,bounded as bounds,local_gate as gate,results,catalog,inspection
ROOT=Path(__file__).resolve().parents[1];R2=ROOT.parent/'jarvis-v2-vm164-stage2-operator-safety-remediation-r2'
BASE=json.loads((R2/'evidence/SYNTHETIC-12-CASE.json').read_bytes())
CANONICAL=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
SHA=lambda x:hashlib.sha256(x).hexdigest()
OBSERVED=[]
NSS=b'passwd: files\ngroup: files\ninitgroups: files\nsudoers: files\nhosts: files\nnetgroup: files\n'

def seed():return copy.deepcopy(BASE)
def seal(r):
 artifacts={'cases/'+c+'.json':CANONICAL(row) for c,row in r['cases'].items()}
 r['evidence_manifest']={k:{'sha256':SHA(v),'bytes':len(v)} for k,v in artifacts.items()};r['evidence_manifest_sha256']=SHA(CANONICAL(r['evidence_manifest']))
 return artifacts

def validate(r,artifacts=None):
 if artifacts is None:artifacts=seal(r)
 return results.validate(r,artifacts,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256=BASE['packet_manifest_sha256'])
def sample(seconds):
 s=BASE['session'];date=datetime.datetime.fromisoformat(s['starts_utc'].replace('Z','+00:00'))+datetime.timedelta(seconds=seconds)
 return dict(boot_id=s['boot_id'],utc=date.strftime('%Y-%m-%dT%H:%M:%SZ'),boot_us=s['start_boot_us']+seconds*1000000,offset_low_us=s['start_offset_low_us'],offset_high_us=s['start_offset_high_us'])
def sync_show(obs,role):
 raw=''.join(k+'='+v+'\n' for k,v in sorted(obs[role].items()))
 obs['raw_'+role]=raw;obs['capture_receipts'][role]['raw_stdout']=raw

def sync_journal(row):
 lines=[json.loads(x) for x in row['raw_journal'].splitlines()]
 by_cursor={e['cursor']:e for e in row['events']}
 for line in lines:
  if line['__CURSOR'] in by_cursor:line['MESSAGE']=json.dumps(by_cursor[line['__CURSOR']]['payload'])
 row['raw_journal']=''.join(json.dumps(x)+'\n' for x in lines);row['journal_receipt']['raw_stdout']=row['raw_journal']

def expect_block(test,r,label):
 artifacts=seal(r)
 try:outcome=validate(r,artifacts)
 except (ValueError,TypeError,KeyError):return
 OBSERVED.append({'probe':label,'unexpected_result':outcome,'case_hashes':r['evidence_manifest'],'note':'Contradictory disposable synthetic data; not host evidence'})
 test.fail('Unsafe/inconsistent synthetic record accepted: '+label+' -> '+outcome['status'])

class Controls(unittest.TestCase):
 def test_published_twelve_case_positive_control(self):self.assertEqual(validate(seed())['status'],'PASS_SYNTHETIC_ONLY')
 def test_network_nss_backends_blocked(self):
  for backend in ('sss','ldap','nis','winbind','dns','compat','systemd'):
   with self.assertRaises(ValueError):gate.nss_gate(NSS.replace(b'passwd: files',('passwd: '+backend).encode()))
 def test_ambiguous_nss_blocked(self):
  for raw in (NSS.replace(b'group: files\n',b''),NSS+b'passwd: files\n',NSS.replace(b'passwd: files',b'passwd: files [SUCCESS=return]'),NSS.replace(b'passwd: files',b'passwd: files\\\n sss')):
   with self.assertRaises(ValueError):gate.nss_gate(raw)
 def test_missing_policy_prerequisites_block(self):
  with self.assertRaises(ValueError):gate.policy_gate(NSS,b'nobody:x:65534:65534::/nonexistent:/usr/sbin/nologin\n',b'nogroup:x:65534:\n',b'',{})
 def test_no_nss_sudo_or_vm_program_in_catalogue(self):
  for argv in catalog.build()['read'].values():self.assertNotIn(Path(argv[0]).name,('getent','id','sudo','qm','pvesh','pvesm'))
 def test_oversize_regular_file_before_data_read(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'x';path.write_bytes(b'oversized');path.chmod(0o600)
   with path.open('rb') as f,patch.object(bounds,'read_stream',side_effect=AssertionError('read before size bound')):
    with self.assertRaises(ValueError):bounds.read_fd(f.fileno(),4,time.monotonic()+1,owner=os.getuid())
 def test_gzip_bomb_blocked(self):
  with self.assertRaises(ValueError):bounds.gunzip_bounded(gzip.compress(b'A'*1000000),8388608,time.monotonic()+1)
 def test_gzip_trailer_corruption_and_truncation(self):
  original=gzip.compress(bytes(range(256))*5)
  for raw in (original[:-1],original[:-8]+b'\xff'*8,b'not-a-gzip-header-and-payload'):
   with self.assertRaises(ValueError):bounds.gunzip_bounded(raw,8192,time.monotonic()+1)
 def test_gzip_concatenated_bomb_blocked(self):
  raw=gzip.compress(b'a'*50000)*10
  with self.assertRaises(ValueError):bounds.gunzip_bounded(raw,8388608,time.monotonic()+1)
 def test_partial_stream_and_early_eof(self):
  class Partial(io.BytesIO):
   def read(self,n):return super().read(min(n,2))
  self.assertEqual(bounds.read_stream(Partial(b'abcde'),5,time.monotonic()+1,expected_size=5),b'abcde')
  with self.assertRaises(ValueError):bounds.read_stream(Partial(b'abc'),5,time.monotonic()+1,expected_size=5)
 def test_memory_failure_and_deadline_block(self):
  class Bad:
   def read(self,n):raise MemoryError()
  with self.assertRaises(ValueError):bounds.read_stream(Bad(),5,time.monotonic()+1)
  with self.assertRaises(ValueError):bounds.read_stream(io.BytesIO(b'a'),5,0,clock=lambda:1)
 def test_evidence_leaf_symlink_rejected(self):
  import artifacts
  r=seed();data=seal(r)
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);(root/'cases').mkdir()
   for name,raw in data.items():(root/name).write_bytes(raw);(root/name).chmod(0o600)
   path=root/'cases/success.json';path.unlink();path.symlink_to('exit7.json')
   with self.assertRaises(OSError):artifacts.load(root,r['evidence_manifest'])
 def test_resource_caps_in_future_python_inspection(self):
  for key,argv in catalog.build()['read'].items():
   if '-c' in argv and key!='R01-clock':
    for token in ('RLIMIT_AS,(134217728,134217728)','RLIMIT_CPU,(3,3)','RLIMIT_NOFILE,(64,64)'):self.assertIn(token,argv[5])
 def test_every_external_operation_has_cap(self):
  self.assertEqual(set(p.CAPS),{'read','manual','install','create','duplicate','show','journal','cgroup','stop'})
  for cap,limit in p.CAPS.values():self.assertTrue(0<cap<=20 and 0<limit<=8388608)
 def test_timeout_never_success(self):
  r=seed();rc=r['cases']['success']['receipts'][0];env=p.command_envelope(rc['argv'],'create',r['session'],rc['sample']);rc['timeout']=True
  with self.assertRaises(ValueError):p.command_receipt(env,rc)
 def test_missing_elapsed_time_rejected(self):
  r=seed();r['cases']['success']['receipts'][0].pop('elapsed_us');expect_block(self,r,'missing elapsed')
 def test_command_reserve_prevents_expiry_overrun(self):
  with self.assertRaises(ValueError):p.command_envelope(['/usr/bin/systemctl'],'stop',BASE['session'],sample(2695))
 def test_exact_expiry_blocks(self):
  with self.assertRaises(ValueError):p.window(BASE['session'],sample(2700),creation=False)
 def test_collision_inventory_malformed_rejected(self):
  r=seed()
  for bad in (None,{},'already.timer',['foreign.timer'],[r['cases']['success']['plan']['timer']]*2):
   with self.assertRaises(ValueError):p.plan(r['session'],sample(120),'success',r['identity'],occupied=bad)
 def test_wrong_timer_pair_rejected(self):
  r=seed();o=r['cases']['success']['final'];o['timer']['Unit']='unrelated.service';sync_show(o,'timer');expect_block(self,r,'wrong service pairing')
 def test_boot_missing_or_wrong_rejected(self):
  for value in (None,'00000000-0000-0000-0000-000000000000'):
   r=seed();r['cases']['success']['final']['boot_id']=value;expect_block(self,r,'boot')
 def test_missing_clock_receipt_rejected(self):
  r=seed();r['cases']['success']['final']['capture_receipts'].pop('clock');expect_block(self,r,'missing clock')
 def test_wrong_effective_uid_rejected(self):
  r=seed();row=r['cases']['success'];row['events'][1]['payload']['euid']=0;sync_journal(row);expect_block(self,r,'wrong euid')
 def test_stale_rearm_b_guard_generation_rejected(self):
  r=seed();row=r['cases']['rearm-b'];row['events'][0]['payload']['binding']['generation']=r['cases']['rearm-a']['plan']['generation'];sync_journal(row);expect_block(self,r,'old generation')
 def test_fired_rearm_a_complete_binding_rejected(self):
  r=seed();row=r['cases']['rearm-a'];row['events']=copy.deepcopy(r['cases']['success']['events']);expect_block(self,r,'canceled callback fired')
 def test_missing_cleanup_receipt_rejected(self):
  r=seed();r['cases']['cancel']['receipts'].pop();expect_block(self,r,'missing stop receipt')
 def test_active_unit_not_closed(self):
  r=seed();o=r['cases']['success']['final'];o['service'].update(ActiveState='active',SubState='running');sync_show(o,'service');expect_block(self,r,'active service')
 def test_foreign_cleanup_target_rejected(self):
  r=seed();row=r['cases']['success'];o=copy.deepcopy(row['final']);o['name']='foreign'
  with self.assertRaises(ValueError):p.cleanup_argv(r['session']['nonce'],'success',row['plan'],o)
 def test_duplicate_cleanup_no_mutation(self):
  r=seed();row=r['cases']['success']
  self.assertEqual(p.cleanup_argv(r['session']['nonce'],'success',row['plan'],row['final']),[])
  self.assertEqual(p.cleanup_argv(r['session']['nonce'],'success',row['plan'],row['final']),[])
 def test_untrusted_environment_rejected(self):
  for key in ('LD_PRELOAD','LD_LIBRARY_PATH','PYTHONPATH','PYTHONHOME','HOME','TMPDIR','SECRET'):
   with self.assertRaises(ValueError):gate.runtime_environment({**gate.SAFE_ENV,'INVOCATION_ID':'a'*32,key:'not-logged'})
 def test_missing_environment_review_blocks(self):
  with self.assertRaises(ValueError):gate.environment_gate({}, {})
 def test_byte_tampering_rejected(self):
  r=seed();a=seal(r);a['cases/success.json']+=b' '
  with self.assertRaises(ValueError):validate(r,a)
 def test_success_exit7_rejected(self):
  r=seed();o=r['cases']['success']['final'];o['service'].update(ExecMainStatus='7',Result='exit-code');sync_show(o,'service');expect_block(self,r,'success actually exit7')
 def test_first_action_matches_audit_and_no_execution(self):
  a=json.loads((R2/'FIRST-SUPERVISED-ACTION.json').read_bytes());old=json.loads((ROOT.parent/'jarvis-v2-vm164-stage2-operator-safety-audit-r1/FIRST-SUPERVISED-ACTION.json').read_bytes())
  self.assertEqual(a,old);self.assertFalse(a['allowed_now'])

class RemainingGaps(unittest.TestCase):
 def test_stale_show_receipt_must_not_prove_current_cleanup(self):
  r=seed();row=r['cases']['success'];o=row['final']
  o['capture_receipts']['timer']['sample']=sample(121);o['capture_receipts']['service']['sample']=sample(121)
  expect_block(self,r,'final show receipts 879 seconds older than claimed observation')
 def test_old_cancellation_journal_must_not_prove_no_late_firing(self):
  r=seed();row=r['cases']['rearm-a'];start=(row['plan']['deadline_boot_us']-r['session']['start_boot_us'])//1000000-30
  row['journal_receipt']['sample']=sample(start+1)
  expect_block(self,r,'empty journal captured before cancellation but declared complete through closure')
 def test_stop_receipt_after_deadline_must_fail_cancellation(self):
  r=seed();row=r['cases']['rearm-a'];deadline=(row['plan']['deadline_boot_us']-r['session']['start_boot_us'])//1000000
  for rc in row['receipts'][1:]:rc['sample']=sample(deadline+10)
  expect_block(self,r,'actual stop receipts late despite earlier claimed cancel_boot_us')
 def test_canceled_service_failure_must_not_be_expected_cancellation(self):
  r=seed();o=r['cases']['rearm-a']['final'];o['service'].update(ActiveState='failed',SubState='failed',Result='resources');sync_show(o,'service')
  expect_block(self,r,'unexpected canceled-service resources failure')
 def test_creation_receipt_after_deadline_must_fail(self):
  r=seed();row=r['cases']['success'];row['receipts'][0]['sample']=sample(170)
  expect_block(self,r,'timer creation after its deadline and both waiting captures')
 def test_duplicate_after_firing_must_not_pass_waiting_collision(self):
  r=seed();row=r['cases']['collision'];seconds=(row['plan']['deadline_boot_us']-r['session']['start_boot_us'])//1000000+10
  row['receipts'][1]['sample']=sample(seconds)
  expect_block(self,r,'duplicate issued after firing using old before/after waiting snapshots')
 def test_journal_timestamp_before_session_must_fail(self):
  r=seed();row=r['cases']['success'];lines=[json.loads(s) for s in row['raw_journal'].splitlines()]
  for line in lines:line['__MONOTONIC_TIMESTAMP']='0'
  row['raw_journal']=''.join(json.dumps(x)+'\n' for x in lines);row['journal_receipt']['raw_stdout']=row['raw_journal']
  expect_block(self,r,'trusted journal timestamp zero inconsistent with fresh callback clocks')
 def test_late_callback_after_authorization_expiry_must_fail(self):
  r=seed();row=r['cases']['late'];payload=row['events'][1]['payload'];payload['boottime_us']=r['session']['start_boot_us']+2800000000;payload['monotonic_us']=payload['boottime_us']-12000000;sync_journal(row)
  expect_block(self,r,'callback after UTC/BOOTTIME expiration and after final capture')
 def test_service_failed_state_cannot_be_success(self):
  r=seed();o=r['cases']['success']['final'];o['service'].update(ActiveState='failed',SubState='failed');sync_show(o,'service')
  expect_block(self,r,'failed service with contradictory success exit fields')
 def test_execstart_exit_disagreement_must_fail(self):
  r=seed();o=r['cases']['success']['final'];o['service']['ExecStart']=o['service']['ExecStart'].replace('code=(null) ; status=0','code=exited ; status=7');sync_show(o,'service')
  expect_block(self,r,'ExecStart exit7 disagrees with ExecMainStatus0')
 def test_failedtimer_later_service_invocation_must_fail(self):
  r=seed();o=r['cases']['failedtimer']['final'];o['service'].update(InvocationID='a'*32,ExecMainCode='1',ExecMainStatus='7',Result='exit-code',ActiveState='failed',SubState='failed');sync_show(o,'service')
  expect_block(self,r,'failedtimer service later executed but earlier no-invocation snapshot retained')
 def test_changed_privilege_review_requires_new_external_seal(self):
  r=seed();a=seal(r);r['identity']['vm_authority_absent_review']='0'*64
  try:outcome=validate(r,a)
  except (ValueError,TypeError,KeyError):return
  OBSERVED.append({'probe':'top-level privilege review changed without changing independent case seal','unexpected_result':outcome})
  self.fail('External evidence seal does not cover changed privilege-review identity')
 def test_missing_raw_cgroup_capture_must_fail(self):
  r=seed()
  self.assertTrue(all('raw' not in x['final']['cgroup'] for x in r['cases'].values()))
  expect_block(self,r,'all twelve cgroups are summaries without raw command receipts')
 def test_collision_proof_timeout_must_fail(self):
  import collision
  r=seed();proof=r['cases']['success']['collision_preflight'];proof['units'][r['cases']['success']['plan']['timer']]['timeout']=True
  with self.assertRaises(ValueError):collision.absent(r['session'],'success',proof)
 def test_metadata_command_must_support_required_root_path(self):
  # Execute only the pre-open lexical validation, with empty imports removed.
  # This cannot read a host path or apply RLIMITs.
  prefix=inspection.METADATA_BODY.split("parts=path.split")[0]
  body='\n'.join(line for line in prefix.splitlines() if not line.startswith('import '))
  import types
  try:exec(compile(body,'<synthetic metadata path validation>','exec'),{'sys':types.SimpleNamespace(argv=['synthetic','/']),'need':__import__('common').need})
  except ValueError:self.fail('R21 rejects / although procedure requires it to inspect /')

class AdditionalAdmission(unittest.TestCase):
 def test_renderer_must_reject_stale_collision_proof(self):
  import render,contextlib,sys
  r=seed();data=dict(kind='MANDATORY_STAGE2_PREFLIGHT',session=r['session'],identity=r['identity'],sample=sample(180),collision=r['cases']['success']['collision_preflight'],occupied=[],used=[])
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/'input.json';path.write_bytes(CANONICAL(data));path.chmod(0o600)
   with patch.object(sys,'argv',['render','--input',str(path),'--case','success']),contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(ValueError):render.main()
 def test_interrupted_cleanup_only_stops_owned_service(self):
  r=seed();row=r['cases']['success'];o=copy.deepcopy(row['final']);o['service'].update(ActiveState='active',SubState='running',MainPID='12345');sync_show(o,'service')
  self.assertEqual(p.cleanup_argv(r['session']['nonce'],'success',row['plan'],o),[['/usr/bin/systemctl','--system','--no-ask-password','stop',row['plan']['service']]])
