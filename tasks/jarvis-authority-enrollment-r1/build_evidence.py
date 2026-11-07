#!/usr/bin/env python3
"""Assemble this development packet from exact cage results, using stdlib only."""
from datetime import UTC,datetime
from pathlib import Path
import ast
import difflib
import hashlib
import json
import shutil

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(name,data):(PACKET/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')

def main():
    baseline=json.loads((PACKET/'BASELINE.json').read_text())
    runs=[(p,json.loads((p/'RUN.json').read_text())) for p in sorted((PACKET/'runs').iterdir()) if (p/'RUN.json').exists()]
    selected={mode:next((p,r) for p,r in reversed(runs) if r.get('mode')==mode and r['status']=='PASS') for mode in ('core','focused','full-app','benchmark')}
    sources=selected['core'][1]['source_sha256'];assert len(sources)==99
    for mode,(p,r) in selected.items():
        assert r['source_sha256']==sources and not r['guard_stop'],mode
        if mode in ('core','focused','full-app'):
            count={'core':254,'focused':59,'full-app':58}[mode]
            result=r['child']['regressions'] if mode=='full-app' else r['child']['tests']
            assert result=={'collected':count,'failed':0,'skipped':0,'exitstatus':0}
    for f,h in sources.items():assert sha(ROOT/f)==h,f
    added=['app/agent/enrollment.py','app/agent/branch_verification.py','tests/test_authority_enrollment.py',
           'tests/enrollment_process_actor.py','tests/enrollment_fixtures.py','tests/synthetic_authority.py',
           'tests/test_enrollment_app.py','docs/authority_enrollment.md']
    changed=[f for f,h in baseline['source_sha256'].items() if sha(ROOT/f)!=h]
    files=sorted(added+changed);assert len(files)==29
    patch=[]
    for f in files:
        out=PACKET/'source'/f;out.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/f,out)
        before=(PACKET/'before'/f).read_text() if f in changed else ''
        patch.extend(difflib.unified_diff(before.splitlines(True),(ROOT/f).read_text().splitlines(True),fromfile='before/'+f if f in changed else '/dev/null',tofile='after/'+f))
    (PACKET/'SOURCE.patch').write_text(''.join(patch))
    write('CHANGES.json',{'modified':changed,'added':added,'comparison':'Captured actual workspace baseline, preserving all prior uncommitted implementation; not git HEAD.'})
    all_sources=dict(sources)
    for f in files:all_sources[f]=sha(ROOT/f)
    for mode,(directory,_) in selected.items():
        for group in ('tests','regressions'):
            for copied in (directory/'input'/group).glob('*.py'):
                actual=ROOT/'tests'/copied.name
                if actual.is_file():assert sha(actual)==sha(copied),str(actual);all_sources[str(actual.relative_to(ROOT))]=sha(actual)
    for f in PACKET.glob('*.py'):all_sources[str(f.relative_to(ROOT))]=sha(f)
    for f in (PACKET/'tests').glob('*.py'):all_sources[str(f.relative_to(ROOT))]=sha(f)
    write('SOURCE-SHA256.json',all_sources)
    app=selected['full-app'][0];bench=selected['benchmark'][0];focused=selected['focused'][0]
    for name in ('ENROLLMENT-DEMONSTRATION.json','DISASTER-DEMONSTRATION.json','OPERATOR-DEMONSTRATION.json','DEMONSTRATION.json'):
        shutil.copyfile(app/'output'/name,PACKET/name)
    demonstration=json.loads((PACKET/'ENROLLMENT-DEMONSTRATION.json').read_text())
    write('BRANCH-PROPOSAL.json',demonstration['branch_verification'])
    for name in ('BENCHMARKS.json','ENROLLMENT-BENCHMARKS.json'):shutil.copyfile(bench/'output'/name,PACKET/name)
    legacy_bench=json.loads((PACKET/'BENCHMARKS.json').read_text());enroll_bench=json.loads((PACKET/'ENROLLMENT-BENCHMARKS.json').read_text())
    assert len(legacy_bench['samples'])==4 and len(enroll_bench)==3
    assert all(row['uncertain_reexecution_count']==0 for row in legacy_bench['samples']+enroll_bench)
    assert len(selected['full-app'][1]['child']['cases'])==13
    assert len(selected['full-app'][1]['child']['native_execution'])==3
    app_out=(app/'stdout.txt').read_text();err=(app/'stderr.txt').read_text()
    assert '58 passed, 2 warnings' in app_out and len(err.splitlines())==27
    assert not (focused/'stderr.txt').read_text() and not (selected['core'][0]/'stderr.txt').read_text()
    cases=[]
    for command in sorted((focused/'output/pytest').glob('test_independent_sigkill_enrol*/case/command.json')):
        cfg=json.loads(command.read_text());cases.append({'stage':cfg['stage'],'result':'PASS','artifacts':str(command.parent.relative_to(PACKET))})
    assert len(cases)==13
    write('CRASH-RECOVERY.json',{'new_independent_SIGKILL':cases,'prior_independent_core_cases_rerun':40,'additional_actual_app_process_crash_case':1,
        'total_distinct_independent_core_cases':53,'partial_sql':'preserved_for_manual_quarantine_no_reset',
        'exact_seed':'authenticated_genesis_continuation','prepared':'verified_no_replace_publication',
        'final_missing_database':'blocked_never_recreated','power_loss_qualification':False,
        'storage_exhaustion':'deterministic_ENOSPC_EACCES_injection_not_host_disk_filling'})
    resources={mode:{k:r[k] for k in ('elapsed_seconds','peak_observed_rss','peak_observed_files','peak_observed_bytes','peak_owned_processes_including_bwrap','limits','guard_stop')} for mode,(_,r) in selected.items()}
    inventory=[]
    for p,r in runs:inventory.append({'run':p.name,'mode':r.get('mode','development_pre_mode_field'),'status':r['status'],'tests':r['child'].get('tests',r['child'].get('regressions')),'child_status':r['child']['status'],'guard_stop':r['guard_stop']})
    write('RESULTS.json',{'at':datetime.now(UTC).isoformat(),'status':'PASS','final_runs':{m:p.name for m,(p,_) in selected.items()},
        'pytest':{'core_regressions':254,'enrollment_branch':59,'application_regressions':58,'passed':371,'failed':0,'skipped':0,'new_sprint_cases':63,'previous_cases_rerun':308},
        'application_scenario_groups':13,'native_probes':3,'benchmark_cases':7,'same_application_source_count':99,'resources':resources,
        'all_runs':inventory,'full_repository_suite_claimed':False,'live_qualification_claimed':False,'physical_power_loss_claimed':False,
        'warnings':{'upstream_deprecations':2,'expected_synthetic_startup_lines':27}})
    rows=[]
    for x in enroll_bench:
        rows.append('| '+' | '.join([str(x['held_tasks'])]+[f"{x[k]*1000:.3f}" for k in ('enrollment_seconds','enrollment_verify_seconds','checkpoint_verify_seconds','first_owner_seconds','export_seconds','restore_seconds','branch_verify_seconds','restart_seconds')]+[str(x['generations']),str(x['apparent_bytes'])])+' |')
    (PACKET/'PERFORMANCE.md').write_text('''# Bounded offline performance measurements

All seven cases use the final99 application hashes and unchanged cage/resource
limits. Raw samples: [BENCHMARKS.json](BENCHMARKS.json) (four state/history cases)
and [ENROLLMENT-BENCHMARKS.json](ENROLLMENT-BENCHMARKS.json) (three actual ceremonies).
The latter use real enrollment, first owner takeover, original UNKNOWN operation,
task population, audit export, inert restore, branch proposal and restart checks.

| Held tasks (+1 UNKNOWN) | Enrollment ms | Verify enrollment ms | Verify checkpoint ms | First owner ms | Export ms | Restore ms | Branch verify ms | Restart ms | Generations | Apparent bytes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
'''+ '\n'.join(rows)+'''

Each new ceremony cost is one warmed measurement per disposable case, not a
statistical percentile. File counts, apparent/allocated storage and cumulative
process peak RSS are retained in raw JSON. Population uses individual real held
task admissions; max_pending and checkpoint capacities are unchanged. All seven
cases preserve UNKNOWN; uncertain reexecution count is zero.

The four history regressions retain17/129/513-task snapshots and256 control
mutations, three warmed verification/query samples, checkpoint/rollover commit
overhead, export/restore throughput and startup/reconciliation. Their legacy
setup uses explicit trusted synthetic compatibility capabilities, not the new
genesis ceremony. Protected full-state/history verification remains linear.
No cold-cache, production SLO, million-row scale, physical power loss or unlimited
retention claim is made. No resource guard fired or limit was increased.
''')
    print(json.dumps({'final_runs':{m:p.name for m,(p,_) in selected.items()},'project_files':len(files),'source_hashes':len(all_sources),'SIGKILL_cases':len(cases)}))

if __name__=='__main__':main()
