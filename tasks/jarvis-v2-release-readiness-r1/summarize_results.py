"""Select source-bound final runs and account for repository coverage without repeats."""
from pathlib import Path
from collections import Counter
import hashlib,json,shutil
P=Path(__file__).resolve().parent
ROOT=P.parents[1].parent/'JARVIS-release-r1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):(P/name).write_text(json.dumps(value,indent=2)+'\n')
def main():
    source={str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'app').rglob('*.py'))}
    final={};history=[];aborted=[]
    for d in sorted((P/'runs').iterdir()):
        f=d/'RUN.json'
        if not f.exists():aborted.append(d.name);continue
        r=json.loads(f.read_text());history.append({'run':d.name,'mode':r['mode'],'status':r['status'],'tests':(r.get('child') or {}).get('tests')})
        if r['status']=='PASS' and r['source_sha256']==source and r['runner_sha256']==sha(P/'run_checks.py'):final[r['mode']]=(d,r)
    modes={'core','broad-collect','broad-safe','broad-legacy','broad-security','focused','full-app','enrollment','recovery','benchmark'}
    assert set(final)==modes,set(final)
    assert all(r['guard_stop'] is None for d,r in final.values())
    counts={};runs={}
    for mode,(d,r) in final.items():
        child=r['child'];key='regressions' if mode=='full-app' else 'tests'
        if key in child:
            c=child[key];assert c['failed']==0 and c['exitstatus']==0 and c.get('skipped',0)==0
            if mode.startswith('broad-') and mode!='broad-collect':
                assert not any(o['outcome']!='passed' for o in child['outcomes'])
                assert sum(o['when']=='call' and o['outcome']=='passed' for o in child['outcomes'])==c['collected']
            counts[mode]=c
        runs[mode]={'run':d.name,'wall_seconds':r['elapsed_seconds'],'peak_rss':r['peak_observed_rss'],'peak_files':r['peak_observed_files'],'peak_bytes':r['peak_observed_bytes'],'input_manifest_sha256':r['input_manifest_sha256'],'runner_sha256':r['runner_sha256']}
    catalog=final['broad-collect'][1]['child'];assert not catalog['collection_errors'] and not catalog['collection_skips']
    modules=Counter(n['nodeid'].split('::')[0] for n in catalog['collected_nodes'])
    selection=json.loads((P/'selection.json').read_text())
    root_heavy={'tests/test_execution_pipeline.py','tests/test_operator_ledger.py','tests/test_audit_disaster.py','tests/test_authority_enrollment.py','tests/test_recovery_decisions.py','tests/test_secure_transport.py'}
    selected_files=set().union(*(set(v) for v in selection.values()),root_heavy)
    assert set(modules)==selected_files,(set(modules)-selected_files,selected_files-set(modules))
    exclusions=[n for n in catalog['collected_nodes'] if set(n['markers'])&{'manual','hardware','desktop','e2e','perf'}]
    root_extra_modes=['focused','enrollment','recovery']
    root_core_files={'tests/test_execution_pipeline.py','tests/test_operator_ledger.py','tests/test_audit_disaster.py'}
    root_core_cases=sum(modules[n] for n in root_core_files)
    root_passes=sum(counts[m]['collected'] for m in ['broad-safe','broad-legacy','broad-security',*root_extra_modes])+root_core_cases
    supplemental=counts['core']['collected']-root_core_cases
    assert root_passes+len(exclusions)==counts['broad-collect']['collected']
    # Full-app pytest files are an exact repeated subset, not extra distinct cases.
    app_dir=final['full-app'][0]/'input/regressions'
    repeat_files=[]
    for f in app_dir.glob('test*.py'):
        assert f.read_bytes()==(ROOT/'tests'/f.name).read_bytes();repeat_files.append('tests/'+f.name)
    assert sum(modules[n] for n in repeat_files)==counts['full-app']['collected']
    benchmark=final['benchmark'][1]['child']
    benchmark_count=len(benchmark['benchmarks']['samples'])+len(benchmark['enrollment_benchmarks'])+len(benchmark['recovery_benchmarks'])+len(benchmark['integration_benchmarks'])
    result={'status':'PASS_OFFLINE_CANDIDATE','source_root':str(ROOT),'application_sources':len(source),'source_sha256':source,'final_runs':runs,'counts':counts,'repository_collected':counts['broad-collect']['collected'],'repository_passed':root_passes,'repository_deselected':len(exclusions),'repository_collection_errors':0,'repository_skipped':0,'supplemental_authority_packet_cases':supplemental,'distinct_pytest_cases_passed':root_passes+supplemental,'full_app_repeated_pytest_cases':counts['full-app']['collected'],'full_app_repeat_files':repeat_files,'application_scenario_groups':len(final['full-app'][1]['child']['cases']),'native_probes':len(final['full-app'][1]['child']['native_execution']),'benchmark_cases':benchmark_count,'all_runs':history,'aborted_preflight_run_dirs':aborted,'live_or_full_hardware_suite_claimed':False}
    write('RESULTS.json',result)
    write('TEST-INVENTORY.json',{'module_cases':dict(modules),'collected':catalog['collected_nodes'],'deselected':exclusions,'helper_not_collected':{'tests/ollama_test.py':'manual CLI script contains zero test functions; import raises SystemExit without optional ollama SDK. Explicitly ignored, not counted as a passing test.'},'retired_contract_files':['test_agent_stubs.py','test_scheduler.py','test_task_queue_persistence.py','test_task_queue_store_safety.py','test_task_queue_callers.py','test_scheduler_reliability.py'],'original_sources':'before/tests; initial collection and failed legacy run retained'})
    names={'full-app':['INTEGRATED-DEMONSTRATION.json','RECOVERY-DECISIONS-DEMONSTRATION.json','ENROLLMENT-DEMONSTRATION.json','DISASTER-DEMONSTRATION.json'], 'benchmark':['BENCHMARKS.json','ENROLLMENT-BENCHMARKS.json','RECOVERY-BENCHMARKS.json','INTEGRATION-BENCHMARKS.json'],'broad-security':['ANCESTOR-HYPOTHESIS.json']}
    for mode,files in names.items():
        for n in files:shutil.copyfile(final[mode][0]/'output'/n,P/n)
    crash={}
    for mode,name,label in [('focused','TRANSPORT-CRASHES.jsonl','signed_transport'),('recovery','CRASH-RECOVERY.jsonl','registry_witness')]:
        f=final[mode][0]/'output'/name
        if f.exists():crash[label]=[json.loads(line) for line in f.read_text().splitlines()]
    assert len(crash['signed_transport'])==15
    assert all(c['exitcode']==-9 and c['new_endpoint_invocations']==0 for c in crash['signed_transport'])
    write('CRASH-RECOVERY.json',{'observed_current_source_cases':crash,'physical_power_loss_qualified':False,'note':'Retained crash shapes rerun against final candidate; no historical observations counted as fresh.'})
    print(json.dumps({k:result[k] for k in ['repository_collected','repository_passed','repository_deselected','supplemental_authority_packet_cases','distinct_pytest_cases_passed','application_scenario_groups','benchmark_cases']},indent=2))
if __name__=='__main__':main()
