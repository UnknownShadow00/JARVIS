"""Assemble current sprint evidence only; never rewrite predecessor packets."""
from datetime import UTC,datetime
import difflib
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[2]
PACKET=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(name,value):
    (PACKET/name).write_text(json.dumps(value,indent=2)+'\n')


def main():
    baseline=json.loads((PACKET/'BASELINE.json').read_text())
    drift=[name for name,digest in baseline['prior_files'].items() if sha(ROOT/name)!=digest]
    assert not drift,drift
    log=(ROOT/'tasks/loop-log.md').read_bytes()
    assert hashlib.sha256(log[:baseline['log_bytes']]).hexdigest()==baseline['log_sha256']
    write('EVIDENCE-VERIFICATION.json',{'at':datetime.now(UTC).isoformat(),
        'prior_sealed_files_verified':len(baseline['prior_files']),
        'prior_changed_files':drift,'canonical_log_prefix_preserved':True})
    allruns=[];final={}
    current={str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'app').rglob('*.py'))}
    for path in sorted((PACKET/'runs').glob('*/RUN.json')):
        run=json.loads(path.read_text());allruns.append({'run':path.parent.name,'mode':run['mode'],'status':run['status']})
        if run['status']=='PASS' and run['source_sha256']==current and run['runner_sha256']==sha(PACKET/'run_checks.py'):final[run['mode']]=(path.parent,run)
    assert set(final)=={'focused','enrollment','recovery','core','full-app','benchmark'},set(final)
    counts={};summaries={}
    for mode,(path,r) in final.items():
        child=r['child'];key='regressions' if mode=='full-app' else 'tests'
        if key in child:counts[mode]=child[key]
        summaries[mode]={'run':path.name,'wall_seconds':r['elapsed_seconds'],'guard_stop':r['guard_stop'],
            'peak_rss':r['peak_observed_rss'],'peak_files':r['peak_observed_files'],'peak_bytes':r['peak_observed_bytes'],
            'input_manifest_sha256':r['input_manifest_sha256'],'runner_sha256':r['runner_sha256']}
        assert r['guard_stop'] is None
    assert len({r['runner_sha256'] for _,r in final.values()})==1
    total=sum(c['collected'] for c in counts.values())
    assert all(c['failed']==0 and c['skipped']==0 and c['exitstatus']==0 for c in counts.values())
    write('RESULTS.json',{'at':datetime.now(UTC).isoformat(),'final_runs':summaries,'counts':counts,
        'distinct_pytest_passes':total,'application_scenarios':len(final['full-app'][1]['child']['cases']),
        'native_probes':len(final['full-app'][1]['child']['native_execution']),
        'application_source_count':len(current),'all_runs':allruns,'complete_repository_suite_claimed':False})
    for mode,names in {'full-app':['INTEGRATED-DEMONSTRATION.json','RECOVERY-DECISIONS-DEMONSTRATION.json','ENROLLMENT-DEMONSTRATION.json','DISASTER-DEMONSTRATION.json'],
                       'benchmark':['INTEGRATION-BENCHMARKS.json','RECOVERY-BENCHMARKS.json','ENROLLMENT-BENCHMARKS.json','BENCHMARKS.json']}.items():
        for name in names:
            source=final[mode][0]/'output'/name
            if source.exists():shutil.copyfile(source,PACKET/name)
    crash=[json.loads(line) for line in (final['focused'][0]/'output/TRANSPORT-CRASHES.jsonl').read_text().splitlines()]
    write('CRASH-RECOVERY.json',{'new_independent_transport_SIGKILL_cases':len(crash),'cases':crash,
          'physical_power_loss_qualified':False})
    changes=[];patch=[]
    currentfiles=[]
    for directory in ('app','tests','docs'):
        currentfiles.extend(p for p in (ROOT/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    currentfiles.extend(ROOT/n for n in ('README.md','PROJECT_STATUS.md'))
    for path in sorted(currentfiles):
        name=str(path.relative_to(ROOT));before=PACKET/'before'/name
        old=before.read_bytes() if before.exists() else b'';new=path.read_bytes()
        if old!=new:
            changes.append(name);target=PACKET/'source'/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(new)
            patch.extend(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='before/'+name,tofile='source/'+name))
    write('CHANGES.json',changes);(PACKET/'SOURCE.patch').write_text(''.join(patch))
    identities={**current}
    for name in changes:identities[name]=sha(ROOT/name)
    for path in sorted(PACKET.glob('*.py')):identities[str(path.relative_to(ROOT))]=sha(path)
    write('SOURCE-SHA256.json',identities)
    write('SYMLINKS.json',{str(p.relative_to(PACKET)):str(p.readlink()) for p in sorted(PACKET.rglob('*')) if p.is_symlink()})
    manifest=[]
    for path in sorted(PACKET.rglob('*')):
        if path.is_file() and not path.is_symlink() and path.name!='SHA256SUMS':
            manifest.append(sha(path)+'  '+str(path.relative_to(PACKET))+'\n')
    (PACKET/'SHA256SUMS').write_text(''.join(manifest))
    print(json.dumps({'pytest':total,'crashes':len(crash),'changes':len(changes),'seal':sha(PACKET/'SHA256SUMS')},indent=2))

if __name__=='__main__':main()
