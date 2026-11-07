"""Read-only offline verification of the sealed Sprint 6 evidence packet."""
import ast
import hashlib
import json
from pathlib import Path

PACKET=Path(__file__).resolve().parent
ROOT=PACKET.parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(name):return json.loads((PACKET/name).read_text())
def verify_manifest(base,manifest):
    count=0
    for line in manifest.read_text().splitlines():
        digest,name=line.split('  ',1)
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts,name
        path=base/relative
        assert not path.is_symlink() and path.is_file() and sha(path)==digest,name
        count+=1
    return count

def main():
    files=verify_manifest(PACKET,PACKET/'SHA256SUMS')
    manifest_names={line.split('  ',1)[1] for line in (PACKET/'SHA256SUMS').read_text().splitlines()}
    actual_names={str(f.relative_to(PACKET)) for f in PACKET.rglob('*') if f.is_file() and not f.is_symlink() and f.name!='SHA256SUMS'}
    assert actual_names==manifest_names,'unexpected/missing packet files'
    links={str(f.relative_to(PACKET)):str(f.readlink()) for f in PACKET.rglob('*') if f.is_symlink()}
    assert links==read('SYMLINKS.json'),'symlink drift'
    baseline=read('BASELINE.json')
    for name,digest in baseline['prior_files'].items():assert sha(ROOT/name)==digest,name
    log=(ROOT/'tasks/loop-log.md').read_bytes()
    assert hashlib.sha256(log[:baseline['log_bytes']]).hexdigest()==baseline['log_sha256']
    completion=read('COMPLETION-LOG.json')
    raw=completion['entry'].encode()
    assert log[completion['offset']:completion['offset']+len(raw)]==raw
    assert hashlib.sha256(raw).hexdigest()==completion['sha256']
    for name,digest in read('SOURCE-SHA256.json').items():assert sha(ROOT/name)==digest,name
    for name,digest in read('INDEPENDENT-REVIEW.json')['source_sha256'].items():assert sha(ROOT/name)==digest,name
    current={str(f.relative_to(ROOT)):sha(f) for f in sorted((ROOT/'app').rglob('*.py'))}
    results=read('RESULTS.json');total=0
    for mode,info in results['final_runs'].items():
        run=PACKET/'runs'/info['run'];r=json.loads((run/'RUN.json').read_text())
        assert r['mode']==mode and r['status']=='PASS' and r['guard_stop'] is None
        assert r['source_sha256']==current
        assert sha(PACKET/'run_checks.py')==r['runner_sha256']==info['runner_sha256']
        assert sha(run/'INPUT-SHA256SUMS')==r['input_manifest_sha256']==info['input_manifest_sha256']
        verify_manifest(run/'input',run/'INPUT-SHA256SUMS')
        key='regressions' if mode=='full-app' else 'tests'
        if key in r['child']:
            c=r['child'][key];assert c['failed']==c['skipped']==c['exitstatus']==0
            total+=c['collected']
        for folder in ('tests','regressions'):
            for f in (run/'input'/folder).glob('*.py'):
                original=ROOT/'tests'/f.name
                if original.exists():assert f.read_bytes()==original.read_bytes(),str(f)
    assert total==548==results['distinct_pytest_passes']
    crash=read('CRASH-RECOVERY.json')['cases']
    assert len(crash)==15 and all(c['exitcode']==-9 and c['new_endpoint_invocations']==0 for c in crash)
    for f in (ROOT/'app').rglob('*.py'):ast.parse(f.read_bytes(),filename=str(f))
    print(json.dumps({'status':'PASS','packet_files':files,'symlinks':len(links),'prior_files_verified':len(baseline['prior_files']),
        'current_application_sources':len(current),'pytest_passes':total,'new_SIGKILL_cases':len(crash),
        'canonical_log_prefix_and_completion_verified':True,'source_and_independent_review_pins_verified':True,
        'manifest_sha256':sha(PACKET/'SHA256SUMS')},indent=2))

if __name__=='__main__':main()
