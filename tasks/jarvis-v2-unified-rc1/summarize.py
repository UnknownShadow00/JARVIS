"""Account actual merged-source node IDs without adding historical or duplicate runs."""
from pathlib import Path
import json,hashlib,re,shutil,collections
P=Path(__file__).resolve().parent;W=P.parents[2]/'JARVIS-unified-rc1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(n,v):(P/n).write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def norm(n):
 if '/' not in n.split('::',1)[0]:n='tests/'+n
 for prefix in ['/input/tests/','/input/regressions/']:
  if n.startswith(prefix):n='tests/'+n[len(prefix):]
 return re.sub(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}','<fixture-uuid>',n)
source={str(f.relative_to(W)):sha(f) for f in sorted((W/'app').rglob('*.py'))}
final={};history=[]
for d in sorted((P/'runs').iterdir()):
 if not (d/'RUN.json').exists():continue
 r=json.loads((d/'RUN.json').read_text());history.append({'run':d.name,'mode':r['mode'],'status':r['status'],'child_status':(r.get('child') or {}).get('status')})
 if r['status']=='PASS' and r['source_sha256']==source and r['runner_sha256']==sha(P/'run_checks.py'):final[r['mode']]=(d,r)
assert set(final)=={'core','full-app','focused','enrollment','recovery','benchmark','broad-collect','broad-safe','broad-legacy','broad-security'}
passed=set();outcomes=[];warnings=[];runs={}
for m,(d,r) in final.items():
 c=r['child'];rows=c.get('outcomes',c.get('node_outcomes',[]))
 assert not r['guard_stop']
 for row in rows:
  assert row['outcome']=='passed',row
  if row['when']=='call':passed.add(norm(row['nodeid']));outcomes.append({'mode':m,'nodeid':row['nodeid'],'identity':norm(row['nodeid'])})
 for warning in c.get('pytest_warnings',[]):warnings.append({'mode':m,**warning})
 runs[m]={'run':d.name,'status':r['status'],'tests':c.get('tests',c.get('regressions')),'wall_seconds':r['elapsed_seconds'],'peak_rss':r['peak_observed_rss'],'source_sha256':r['source_sha256'],'input_manifest_sha256':r['input_manifest_sha256'],'runner_sha256':r['runner_sha256']}
cat=final['broad-collect'][1]['child'];assert not cat['collection_errors'] and not cat['collection_skips']
catalog={norm(x['nodeid']) for x in cat['collected_nodes']};assert len(catalog)==len(cat['collected_nodes'])
excluded=[n for n in cat['collected_nodes'] if set(n['markers'])&{'manual','hardware','desktop','e2e','perf'}]
assert catalog-passed=={norm(n['nodeid']) for n in excluded},catalog-passed
assert len(excluded)==9
supplemental=passed-catalog;assert len(supplemental)==80
assert len(passed)==1023
security=[];security_passed=set()
for n in ['http_regressions_updated_final','execution_regressions_updated_final','transport_regressions_updated_final','durability_regressions_final']:
 f=P/'agents/regression/artifacts'/(n+'_pinned.txt');lines=f.read_text().splitlines()
 capture=next(x for x in lines if 'UNIFIED_OUTCOMES=' in x)
 r=json.loads(capture.split('UNIFIED_OUTCOMES=',1)[1]);assert r['exitstatus']==0
 nodes=[]
 for row in r['outcomes']:
  assert row['outcome']=='passed',row
  if row['when']=='call':
   node=norm(row['nodeid'].replace('tests/','tests/',1))
   if '/target/tests/' in node:node='tests/'+node.split('/target/tests/',1)[1]
   nodes.append(node);security_passed.add(node)
 security.append({'harness':n,'passed_cases':len(nodes),'normalized_nodeids':nodes,'artifact_sha256':sha(f)})
# Codex2 renamed this one pre-existing behavior-only test; no extra case is claimed.
alias={'tests/test_blank_token_does_not_grant_task_authority':'tests/test_empty_token_cannot_access_authority'}
assert not security_passed-passed,security_passed-passed
crash={}
for mode,name,label in [('focused','TRANSPORT-CRASHES.jsonl','signed_transport'),('recovery','CRASH-RECOVERY.jsonl','registry_witness')]:
 f=final[mode][0]/'output'/name;crash[label]=[json.loads(x) for x in f.read_text().splitlines()]
assert len(crash['signed_transport'])==15 and len(crash['registry_witness'])==22
assert all(c['exitcode']==-9 and c['new_endpoint_invocations']==0 for c in crash['signed_transport'])
write('CRASH-RECOVERY.json',{'fresh_current_source_cases':crash,'total':37,'physical_power_loss_qualified':False})
for mode,names in {'full-app':['INTEGRATED-DEMONSTRATION.json','RECOVERY-DECISIONS-DEMONSTRATION.json','ENROLLMENT-DEMONSTRATION.json','DISASTER-DEMONSTRATION.json'],'benchmark':['BENCHMARKS.json','ENROLLMENT-BENCHMARKS.json','RECOVERY-BENCHMARKS.json','INTEGRATION-BENCHMARKS.json'],'broad-security':['ANCESTOR-HYPOTHESIS.json']}.items():
 for n in names:shutil.copyfile(final[mode][0]/'output'/n,P/n)
b=final['benchmark'][1]['child'];benchmarks=len(b['benchmarks']['samples'])+len(b['enrollment_benchmarks'])+len(b['recovery_benchmarks'])+len(b['integration_benchmarks'])
assert benchmarks==13
write('TEST-INVENTORY.json',{'collected':cat['collected_nodes'],'excluded':excluded,'passed_unique_normalized_nodeids':sorted(passed),'supplemental_packet_nodeids':sorted(supplemental),'normalization':'Retain original nodeids separately; canonicalize /input paths and replace random fixture UUIDs only. Normalized repository identities verified collision-free.','security_alias_from_predecessor':alias,'helper_not_collected':{'tests/ollama_test.py':'Manual script; zero test functions, optional SDK raises SystemExit. Explicitly ignored, not a pass.'}})
write('TEST-OUTCOMES.json',outcomes);write('WARNINGS.json',warnings)
write('SECURITY-SELECTED-RESULTS.json',{'groups':security,'unique_cases':len(security_passed),'all_are_repeats_of_full_suite':True,'historical_codex2_count':168,'historical_count_added_to_unified_total':False,'scope':'Same four selected harness groups rerun on merged tests, preserving stronger Codex1 cases and new lifespan regressions.'})
result={'status':'PASS_OFFLINE_UNIFIED_CANDIDATE','source_root':str(W),'application_sources':len(source),'source_sha256':source,'final_runs':runs,'repository_collected':len(catalog),'repository_passed':len(catalog&passed),'repository_excluded':len(excluded),'repository_collection_errors':0,'repository_skipped':0,'supplemental_packet_cases':len(supplemental),'actual_unique_pytest_passed':len(passed),'final_failures':0,'final_skips':0,'full_app_repeated_cases':103,'application_scenario_groups':len(final['full-app'][1]['child']['cases']),'security_selected_repeated_cases':len(security_passed),'additional_security_integrated_scenario_groups':4,'crash_cases':37,'benchmark_cases':benchmarks,'warning_occurrences':len(warnings),'warning_categories':dict(collections.Counter(x['category'] for x in warnings)),'all_attempts':history,'live_or_hardware_readiness_claimed':False}
write('RESULTS.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['source_sha256','final_runs','all_attempts']},indent=2))
