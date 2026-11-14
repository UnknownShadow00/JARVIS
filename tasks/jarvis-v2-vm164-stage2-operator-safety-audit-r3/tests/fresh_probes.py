"""Fresh independent semantic mutations. No host operations; synthetic fixtures only."""
import copy,json,unittest,datetime,hashlib,io,gzip,time
from pathlib import Path
import packet as p,binding as b,results,collision,bounded,local_gate
BASE=None
OBSERVED=[]
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sha(x):return hashlib.sha256(x).hexdigest()
def seed():return copy.deepcopy(BASE)
def seal(r):
 r['command_ledger']=[dict(case=c,generation=r['cases'][c]['plan']['generation'],receipt_sha256=sha(canonical(rc))) for c in p.CASES for rc in r['cases'][c]['receipts']]
 r['consumed_generations']=[r['cases'][c]['plan']['generation'] for c in p.CASES]
 env=copy.deepcopy({k:v for k,v in r.items() if k not in ('cases','evidence_manifest','evidence_manifest_sha256')})
 for row in r['cases'].values():row['review_envelope']=copy.deepcopy(env)
 artifacts={'cases/'+c+'.json':canonical(r['cases'][c]) for c in p.CASES}
 r['evidence_manifest']={k:dict(sha256=sha(v),bytes=len(v)) for k,v in artifacts.items()}
 r['evidence_manifest_sha256']=sha(canonical(r['evidence_manifest']))
 return artifacts
def validate(r):
 a=seal(r)
 return results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256=BASE['packet_manifest_sha256'])
def sync(obs,role='service'):
 raw=''.join(k+'='+v+'\n' for k,v in sorted(obs[role].items()))
 obs['raw_'+role]=raw;obs['capture_receipts'][role]['raw_stdout']=raw

def reject(test,r):
 try:result=validate(r)
 except ValueError as e:
  OBSERVED.append(dict(test=test.id(),blocked=str(e)));return
 OBSERVED.append(dict(test=test.id(),accepted=result,changed_case_hashes=r['evidence_manifest']))
 test.fail('Contradictory complete/resealed evidence was accepted: '+result['status'])

class Fresh(unittest.TestCase):
 def test_valid_published_control(self):self.assertEqual(validate(seed())['status'],'PASS_SYNTHETIC_ONLY')
 def test_completion_invocation_substitution(self):
  r=seed();o=r['cases']['success']['completion'];o['service']['InvocationID']='9'*32;sync(o);reject(self,r)
 def test_completion_start_before_authorization(self):
  r=seed();o=r['cases']['success']['completion'];o['service']['ExecMainStartTimestampMonotonic']='1';sync(o);reject(self,r)
 def test_completion_exit_after_capture(self):
  r=seed();o=r['cases']['success']['completion'];o['service']['ExecMainExitTimestampMonotonic']=str(o['sample']['boot_us']+100000000);sync(o);reject(self,r)
 def test_completion_exit_before_start(self):
  r=seed();o=r['cases']['success']['completion'];o['service']['ExecMainExitTimestampMonotonic']='1';sync(o);reject(self,r)
 def test_waiting_control_process_present(self):
  r=seed();o=r['cases']['success']['waiting'][0];o['service']['ControlPID']='12345';sync(o);reject(self,r)
 def test_waiting_executed_trailer(self):
  r=seed();o=r['cases']['success']['waiting'][0];o['service']['ExecStart']=o['service']['ExecStart'].replace('pid=0 ; code=(null) ; status=0','pid=12345 ; code=exited ; status=7');sync(o);reject(self,r)
 def test_waiting_failure_exit_status(self):
  r=seed();o=r['cases']['success']['waiting'][0];o['service'].update(ExecMainCode='1',ExecMainStatus='7');sync(o);reject(self,r)
 def test_command_receipt_untrusted_environment(self):
  r=seed();r['cases']['success']['receipts'][0]['environment']={'PYTHONPATH':'SYNTHETIC_UNTRUSTED','PATH':'/SYNTHETIC'};reject(self,r)
 def test_receipt_wrong_operation(self):
  r=seed();r['cases']['success']['final']['capture_receipts']['timer']['operation']='install';reject(self,r)
 def test_final_start_timestamp_text_before_authorization(self):
  r=seed();o=r['cases']['success']['final'];o['service']['ExecStart']=o['service']['ExecStart'].replace('start_time=[]','start_time=[Mon 2020-01-01 00:00:00 UTC]');sync(o);reject(self,r)
 def test_callback_before_guard(self):
  r=seed();row=r['cases']['success'];guard=row['events'][0];guard['payload']['boottime_us']+=500000
  lines=[json.loads(s) for s in row['raw_journal'].splitlines()]
  for line in lines:
   if line['__CURSOR']==guard['cursor']:
    line['MESSAGE']=json.dumps(guard['payload']);line['__MONOTONIC_TIMESTAMP']=str(int(line['__MONOTONIC_TIMESTAMP'])+500000);line['__REALTIME_TIMESTAMP']=str(int(line['__REALTIME_TIMESTAMP'])+500000)
  lines.sort(key=lambda x:int(x['__MONOTONIC_TIMESTAMP']));row['events']=list(reversed(row['events']))
  row['raw_journal']=''.join(json.dumps(x)+'\n' for x in lines)
  row['journal_receipt']['raw_stdout']=row['completion_journal_receipt']['raw_stdout']=row['raw_journal'];reject(self,r)
 def test_later_namespace_must_allow_retained_owned_unit(self):
  r=seed();row=r['cases']['exit7'];proof=row['collision_preflight'];prior=r['cases']['success']['plan']['timer']
  proof['namespace_inventory']=[prior];proof['captures']['loaded']['raw_stdout']=prior+' loaded inactive elapsed JARVIS previous owned timer\n'
  try:collision.absent(r['session'],'exit7',proof)
  except ValueError as e:
   OBSERVED.append(dict(test=self.id(),blocked=str(e),reason='An earlier owned retained timer is required by final closure, not a target name collision'))
   self.fail('Required retained earlier generation prevents the second trial: '+str(e))
 def test_no_callback_after_expiry(self):
  r=seed();row=r['cases']['late'];row['events'][1]['payload']['boottime_us']=r['session']['start_boot_us']+2700000000
  for line in [json.loads(s) for s in row['raw_journal'].splitlines()]:pass
  reject(self,r)
 def test_incorrect_boot_after_correct_order(self):
  r=seed();r['cases']['success']['completion']['capture_receipts']['service']['boot_id']='00000000-0000-0000-0000-000000000000';reject(self,r)
 def test_missing_effective_cancellation(self):
  r=seed();r['cases']['cancel']['cancellation'].pop('effective_observation');
  with self.assertRaises((ValueError,KeyError)):validate(r)
 def test_ack_without_inactivity(self):
  r=seed();o=r['cases']['cancel']['cancellation']['effective_observation'];o['service'].update(ActiveState='active',SubState='running',MainPID='100');sync(o);reject(self,r)
 def test_partial_cleanup_marked_complete(self):
  r=seed();r['cases']['cancel']['receipts'].pop();reject(self,r)
 def test_cleanup_receipt_after_expiry(self):
  r=seed();r['cases']['success']['receipts'][-1]['finished_boot_us']=r['session']['start_boot_us']+2700000000;reject(self,r)
 def test_duplicate_capture_property(self):
  r=seed();o=r['cases']['success']['final'];o['raw_service']+='Result=success\n';o['capture_receipts']['service']['raw_stdout']=o['raw_service'];reject(self,r)
 def test_cross_generation_journal(self):
  r=seed();r['cases']['rearm-b']['raw_journal']=r['cases']['success']['raw_journal'];r['cases']['rearm-b']['journal_receipt']['raw_stdout']=r['cases']['rearm-b']['raw_journal'];reject(self,r)
 def test_cgroup_process_leak(self):
  r=seed();cg=r['cases']['success']['final']['cgroup'];cg['raw']['cgroup.procs']='12345\n';raw=json.loads(cg['receipt']['raw_stdout']);raw['raw']=cg['raw'];cg['receipt']['raw_stdout']=json.dumps(raw);reject(self,r)
 def test_missing_review_input(self):
  r=seed();r['review_artifacts']['vm_authority_absent_review']['inputs']={};reject(self,r)
 def test_network_nss(self):
  with self.assertRaises(ValueError):local_gate.nss_gate(b'passwd: ldap\ngroup: files\ninitgroups: files\nsudoers: files\nhosts: files\nnetgroup: files\n')
 def test_missing_nss_backend(self):
  with self.assertRaises(ValueError):local_gate.nss_gate(b'passwd: files\ngroup: files\n')
 def test_environment_minimal_guard(self):
  with self.assertRaises(ValueError):local_gate.runtime_environment({**local_gate.SAFE_ENV,'INVOCATION_ID':'a'*32,'HOME':'/SYNTHETIC'})
 def test_oversized_stream(self):
  with self.assertRaises(ValueError):bounded.read_stream(io.BytesIO(b'abcde'),4,time.monotonic()+1)
 def test_truncated_stream(self):
  with self.assertRaises(ValueError):bounded.read_stream(io.BytesIO(b'abc'),5,time.monotonic()+1,expected_size=5)
 def test_decompression_expansion(self):
  with self.assertRaises(ValueError):bounded.gunzip_bounded(gzip.compress(b'x'*2000000),8388608,time.monotonic()+1)
 def test_bounded_timeout(self):
  with self.assertRaises(ValueError):bounded.read_stream(io.BytesIO(b'a'),5,0,clock=lambda:1)

 def test_coherent_late_creation(self):
  r=seed();rc=r['cases']['success']['receipts'][0];shift_receipt(rc,50000000);reject(self,r)
 def test_coherent_stale_final_show(self):
  r=seed();o=r['cases']['success']['final']
  for k in ('timer','service'):shift_receipt(o['capture_receipts'][k],-879000000)
  reject(self,r)
 def test_coherent_cancellation_late_ack(self):
  r=seed();row=r['cases']['cancel'];stops=[x for x in row['receipts'] if x['operation']=='stop']
  for rc in stops:shift_receipt(rc,35000000)
  row['cancel_boot_us']=stops[0]['sample']['boot_us'];row['cancellation']['requested_boot_us']=stops[0]['sample']['boot_us'];row['cancellation']['acknowledged_boot_us']=stops[1]['finished_boot_us'];reject(self,r)
 def test_coherent_postexpiry_callback(self):
  r=seed();row=r['cases']['late'];event=row['events'][1];delta=r['session']['start_boot_us']+2800000000-event['payload']['boottime_us']
  event['payload']['boottime_us']+=delta;event['payload']['monotonic_us']+=delta
  lines=[json.loads(s) for s in row['raw_journal'].splitlines()]
  for line in lines:
   if line['__CURSOR']==event['cursor']:
    line['MESSAGE']=json.dumps(event['payload']);line['__MONOTONIC_TIMESTAMP']=str(int(line['__MONOTONIC_TIMESTAMP'])+delta);line['__REALTIME_TIMESTAMP']=str(int(line['__REALTIME_TIMESTAMP'])+delta)
  row['raw_journal']=''.join(json.dumps(x)+'\n' for x in lines);row['journal_receipt']['raw_stdout']=row['completion_journal_receipt']['raw_stdout']=row['raw_journal'];reject(self,r)
 def test_repeated_cleanup_cannot_hide_failed_prior_stop(self):
  r=seed();row=r['cases']['cancel'];row['receipts'][1]['exit_code']=1;reject(self,r)
 def test_canceled_bound_callback_firing(self):
  from launch_guard import guard_binding
  r=seed();row=r['cases']['cancel'];source=copy.deepcopy(r['cases']['success']);plan=row['plan'];delta=plan['deadline_boot_us']-source['plan']['deadline_boot_us'];inv='8'*32
  for e in source['events']:
   e['unit']=plan['service'];e['invocation_id']=inv;e['cursor']='cancel-'+e['cursor'];body=e['payload'];body['boottime_us']+=delta
   if 'monotonic_us' in body:body['monotonic_us']+=delta
   if 'binding' in body:body['binding']=guard_binding(plan);body['invocation_id']=inv
  row['events']=source['events'];lines=[]
  for e in row['events']:
   bt=e['payload']['boottime_us'];lines.append(dict(_BOOT_ID=plan['boot_id'].replace('-',''),_SYSTEMD_UNIT=plan['service'],_SYSTEMD_INVOCATION_ID=inv,_UID='65534',__CURSOR=e['cursor'],__MONOTONIC_TIMESTAMP=str(bt-12000000),__REALTIME_TIMESTAMP=str(int(datetime.datetime.fromisoformat(r['session']['starts_utc'].replace('Z','+00:00')).timestamp()*1000000)+bt-r['session']['start_boot_us']),MESSAGE=json.dumps(e['payload'])))
  row['raw_journal']=''.join(json.dumps(x)+'\n' for x in lines);row['journal_receipt']['raw_stdout']=row['completion_journal_receipt']['raw_stdout']=row['raw_journal']
  # Leave mandatory no-invocation readback intact: observed callback explicitly contradicts it.
  reject(self,r)

def shift_receipt(rc,delta):
 for key in ('started_utc','finished_utc'):
  stamp=datetime.datetime.fromisoformat(rc[key].replace('Z','+00:00'))+datetime.timedelta(microseconds=delta);rc[key]=stamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
 rc['sample']['utc']=(datetime.datetime.fromisoformat(rc['sample']['utc'].replace('Z','+00:00'))+datetime.timedelta(microseconds=delta)).strftime('%Y-%m-%dT%H:%M:%SZ')
 rc['sample']['boot_us']+=delta;rc['finished_boot_us']+=delta

class Extra(unittest.TestCase):
 def test_duplicate_signal_exit_masquerades_as_refusal(self):
  r=seed();rc=r['cases']['collision']['receipts'][1];rc['exit_code']=-9;rc['signal']=None;reject(self,r)
 def test_duplicate_impossible_exit_code(self):
  r=seed();r['cases']['collision']['receipts'][1]['exit_code']=999;reject(self,r)
 def test_raw_clock_utc_precedes_capture_request(self):
  r=seed();rc=r['cases']['success']['final']['capture_receipts']['clock']
  for k in ('started_utc','finished_utc'):rc[k]=(datetime.datetime.fromisoformat(rc[k].replace('Z','+00:00'))+datetime.timedelta(microseconds=900000)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
  # Clock output UTC is .000100; request now .900000 in the same second.
  # Raw output is thus 899900us before request, despite a 1000us capture duration.
  reject(self,r)
