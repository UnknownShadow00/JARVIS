"""Independent R4 negative probes. Pure synthetic records; reject unsafe acceptance."""
import copy,datetime,json,re,hashlib,unittest
import packet as p,binding as b,results,retention,lifecycle,fixtures as f
from common import canonical,sha
BASE=None
OBSERVED=[]

def delta(a,z,path=()):
 if isinstance(a,dict) and isinstance(z,dict):
  out=[]
  for k in sorted(set(a)|set(z)):
   if k not in a:out.append(dict(op='add',path=list(path)+( [k]),value=z[k]))
   elif k not in z:out.append(dict(op='remove',path=list(path)+[k]))
   else:out+=delta(a[k],z[k],path+(k,))
  return out
 if isinstance(a,list) and isinstance(z,list) and len(a)==len(z):return [v for i,(x,y) in enumerate(zip(a,z)) for v in delta(x,y,path+(i,))]
 return [] if a==z else [dict(op='replace',path=list(path),value=z)]
def seed():return copy.deepcopy(BASE)
def verify(r):
 r,a=f.seal(r);return results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256=BASE['packet_manifest_sha256'])
def reject(test,r,call=None):
 changes=delta(BASE,r)
 try:value=call() if call else verify(r)
 except ValueError as e:OBSERVED.append(dict(test=test.id(),result='BLOCKED',reason=str(e),patch=changes));return
 OBSERVED.append(dict(test=test.id(),result='UNSAFE_ACCEPTED',returned=value,patch=changes))
 test.fail('Unsafe resealed synthetic evidence accepted: '+str(value))
def both(r,field,fun):
 for k in ('completion','final'):
  o=r['cases']['rearm-b'][k];o['service'][field]=fun(o['service'][field]);f.sync(o)
def guardstart(r,shift):
 row=r['cases']['rearm-b'];both(r,'ExecCondition',lambda v:re.sub(r'start_time=\[[^\]]*\]',lambda m:'start_time=['+f.stamp(row['plan']['deadline_boot_us']+shift)+']',v))
def rewrite_journal(row,lines):
 raw=''.join(json.dumps(x)+'\n' for x in lines);row['raw_journal']=raw
 for k in ('journal_receipt','completion_journal_receipt'):row[k]['raw_stdout']=raw
 # Derive selected JSON records from modified raw bytes, keeping independent raw/decoded agreement.
 events={e['cursor']:e for e in row['events']}
 for line in lines:
  if line['__CURSOR'] in events:events[line['__CURSOR']]['payload']=json.loads(line['MESSAGE'])
def add_exit(r,**fields):
 row=r['cases']['rearm-b'];lines=[json.loads(x) for x in row['raw_journal'].splitlines()];line=copy.deepcopy(lines[-1]);mono=int(row['completion']['service']['ExecMainExitTimestampMonotonic']);line.update(MESSAGE='Main process exited, code=exited, status=0',__CURSOR='fresh-exit',__REALTIME_TIMESTAMP=str(int(line['__REALTIME_TIMESTAMP'])+mono-int(line['__MONOTONIC_TIMESTAMP'])),__MONOTONIC_TIMESTAMP=str(mono));line.update(fields);lines.append(line);rewrite_journal(row,lines)
def history(r,case='missingdep'):
 name=r['cases'][case]['plan']['name'];return r['cases']['rearm-b']['collision_preflight']['history'][name]
def remove_plain_history(r):
 h=history(r);h['journal_receipt']['raw_stdout']=''.join(line+'\n' for line in h['journal_receipt']['raw_stdout'].splitlines() if json.loads(line)['MESSAGE'].startswith('{'))
def corrupted_event(r,field,value):
 row=r['cases']['rearm-b'];lines=[json.loads(x) for x in row['raw_journal'].splitlines()];lines[-1][field]=value;rewrite_journal(row,lines)

class Controls(unittest.TestCase):
 def test_complete_twelve(self):self.assertEqual(verify(seed())['status'],'PASS_SYNTHETIC_ONLY')
 def test_bound_plain_exit(self):
  r=seed();add_exit(r);self.assertEqual(verify(r)['status'],'PASS_SYNTHETIC_ONLY')
 def test_standalone_completion(self):
  r=seed();row=r['cases']['success'];raw=canonical(row);self.assertEqual(retention.verified_anchor(row,raw,sha(raw),r['session'],r['clock_domain'],{})['name'],row['plan']['name'])

class NewGaps(unittest.TestCase):
 def test_guard_started_before_timer_creation(self):
  r=seed();guardstart(r,-60000000);reject(self,r)
 def test_guard_started_during_never_invoked_waiting(self):
  r=seed();guardstart(r,-28500000);reject(self,r)
 def test_guard_started_before_timer_trigger(self):
  r=seed();guardstart(r,-1000000);reject(self,r)
 def test_guard_exceeds_reviewed_start_timeout(self):
  r=seed();guardstart(r,-6000000);reject(self,r)
 def test_plain_exit_malformed_invocation(self):
  r=seed();add_exit(r,_SYSTEMD_INVOCATION_ID='INVALID');reject(self,r)
 def test_plain_exit_prior_generation_invocation(self):
  r=seed();add_exit(r,_SYSTEMD_INVOCATION_ID=r['cases']['success']['completion']['service']['InvocationID']);reject(self,r)
 def test_plain_exit_conflicting_unit_fields(self):
  r=seed();add_exit(r,_SYSTEMD_UNIT='foreign.service',UNIT=r['cases']['rearm-b']['plan']['service']);reject(self,r)
 def test_retained_journal_loses_required_diagnostic(self):
  r=seed();remove_plain_history(r);reject(self,r)
 def test_retained_journal_loses_diagnostic_at_admission(self):
  r=seed();remove_plain_history(r);proof=r['cases']['rearm-b']['collision_preflight'];ledger={n:sha(canonical(h['anchor'])) for n,h in proof['history'].items()};import collision
  reject(self,r,lambda:collision.absent(r['session'],'rearm-b',proof,retained=ledger))
 def test_stale_guard_accepted_for_completed_case_anchor(self):
  r=seed();row=r['cases']['success'];d=row['plan']['deadline_boot_us']
  row['completion']['service']['ExecCondition']=re.sub(r'start_time=\[[^\]]*\]',lambda _:'start_time=['+f.stamp(d-60000000)+']',row['completion']['service']['ExecCondition']);f.sync(row['completion']);raw=canonical(row)
  reject(self,r,lambda:retention.verified_anchor(row,raw,sha(raw),r['session'],r['clock_domain'],{}))

class Boundaries(unittest.TestCase):pass

def add(name,mut):
 def test(self):r=seed();mut(r);reject(self,r)
 setattr(Boundaries,'test_'+name,test)

def show(r,where,role,key,value):
 o=r['cases']['rearm-b'][where];o=o[0] if isinstance(o,list) else o;o[role][key]=value;f.sync(o)
def canceled_running(r):
 o=r['cases']['rearm-a']['cancellation']['effective_observation'];o['service'].update(ActiveState='active',SubState='running',MainPID='12');f.sync(o)
def cancel_after_execution(r):
 row=r['cases']['rearm-a'];row['events']=copy.deepcopy(r['cases']['rearm-b']['events'])
def expired_callback(r):
 row=r['cases']['rearm-b'];lines=[json.loads(x) for x in row['raw_journal'].splitlines()];e=lines[-1];body=json.loads(e['MESSAGE']);shift=r['session']['start_boot_us']+2700000000-body['boottime_us'];body['boottime_us']+=shift;body['monotonic_us']+=shift;e['MESSAGE']=json.dumps(body);e['__MONOTONIC_TIMESTAMP']=str(int(e['__MONOTONIC_TIMESTAMP'])+shift);e['__REALTIME_TIMESTAMP']=str(int(e['__REALTIME_TIMESTAMP'])+shift);rewrite_journal(row,lines)
def end_expired(r):
 both(r,'ExecMainExitTimestampMonotonic',lambda _:str(r['session']['start_boot_us']+2700000000-12000000))
def old_active(r):
 h=history(r,'success');o=retention.expand(h['plan'],h['capture']);o['service'].update(MainPID='99',ActiveState='active',SubState='running');f.sync(o);h['capture']=retention.compact(o)
def bad_clock(r):
 o=r['cases']['rearm-b']['final'];cr=o['capture_receipts']['clock'];d=json.loads(cr['raw_stdout']);d['monotonic_us']=d['b2_us'];cr['raw_stdout']=json.dumps(d)
for name,mut in {
 'cancellation_while_callback_running':canceled_running,
 'canceled_generation_fired':cancel_after_execution,
 'callback_at_exact_expiry':expired_callback,
 'callback_finishes_after_expiry':end_expired,
 'failed_timer_with_stale_success':lambda r:r['cases']['failedtimer']['receipts'][0].update(generation=r['cases']['success']['plan']['generation']),
 'timer_never_fired':lambda r:show(r,'completion','timer','LastTriggerUSecMonotonic','0'),
 'successful_callback_failed_service':lambda r:show(r,'completion','service','Result','exit-code'),
 'historical_owner_still_active':old_active,
 'missing_raw_completion_show':lambda r:r['cases']['rearm-b']['completion']['capture_receipts'].pop('service'),
 'malformed_payload_invocation':lambda r:corrupted_event(r,'_SYSTEMD_INVOCATION_ID','bad'),
 'duplicated_journal_cursor':lambda r:corrupted_event(r,'__CURSOR',r['cases']['rearm-b']['events'][0]['cursor']),
 'partial_cleanup_readback':lambda r:r['cases']['rearm-b']['final']['capture_receipts'].pop('timer'),
 'changed_clock_domain':bad_clock,
 'wrong_receipt_environment':lambda r:r['cases']['rearm-b']['receipts'][0]['environment'].update(PYTHONHOME='SYNTHETIC'),
 'reordered_stop_receipts':lambda r:r['cases']['rearm-b']['receipts'].reverse(),
 'missing_receipt_units':lambda r:r['cases']['rearm-b']['receipts'][0].pop('units'),
 'receipt_wrong_epoch':lambda r:r['cases']['rearm-b']['receipts'][0].update(boot_id='00000000-0000-0000-0000-000000000000'),
 'receipt_unexpected_field':lambda r:r['cases']['rearm-b']['receipts'][0].update(untrusted='SYNTHETIC'),
 'collision_signal_plus_expected_diagnostic':lambda r:r['cases']['collision']['receipts'][1].update(signal=9),
 'collision_unrelated_manager_error':lambda r:r['cases']['collision']['receipts'][1].update(raw_stderr='Failed to connect to bus\n'),
 'collision_wrong_unit_error':lambda r:r['cases']['collision']['receipts'][1].update(raw_stderr='Failed to start transient timer unit: Unit foreign.timer already exists.\n'),
 'duplicate_retained_unit':lambda r:r['cases']['rearm-b']['collision_preflight']['namespace_inventory'].append(r['cases']['success']['plan']['timer']),
 'wrong_retained_generation':lambda r:history(r)['plan'].update(generation='0'*64),
 'missing_prior_anchor':lambda r:history(r).pop('anchor'),
 'guard_completes_after_callback':lambda r:both(r,'ExecCondition',lambda v:re.sub(r'stop_time=\[[^\]]*\]',lambda _:'stop_time=['+f.stamp(r['cases']['rearm-b']['plan']['deadline_boot_us']+100000)+']',v)),
 'main_wall_mono_conflict':lambda r:both(r,'ExecStart',lambda v:re.sub(r'start_time=\[[^\]]*\]',lambda _:'start_time=['+f.stamp(r['cases']['rearm-b']['plan']['deadline_boot_us']-12000000)+']',v)),
 'plain_exit_contradictory_status':lambda r:add_exit(r,MESSAGE='Main process exited, code=exited, status=7'),
 'plain_exit_wrong_boot':lambda r:add_exit(r,_BOOT_ID='0'*32),
 'post_stop_leaked_process':lambda r:show(r,'final','service','ControlPID','88'),
}.items():add(name,mut)
