"""Read-only packet/archive verification; never imports application or opens stores."""
import argparse,ast,gzip,hashlib,io,json,stat,tarfile
from pathlib import Path
P=Path(__file__).resolve().parent
MAIN=P.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((P/name).read_text())
def manifest(base,file):
    names=set()
    for line in file.read_text().splitlines():
        h,n=line.split('  ',1);part=Path(n)
        assert not part.is_absolute() and '..' not in part.parts and n not in names,n
        f=base/part;assert not f.is_symlink() and f.is_file() and sha(f)==h,n
        names.add(n)
    return names

def verify_archive():
    build=read('release/BUILD.json');path=P/build['archive'];assert sha(path)==build['archive_sha256']
    assert path.stat().st_mode & 0o222==0,'candidate archive writable'
    source=read('release/SOURCE-SHA256.json');raw=(P/'release/SOURCE-SHA256.json').read_bytes()
    assert hashlib.sha256(raw).hexdigest()==build['source_manifest_sha256']
    assert build['release_id']=='jarvis-v2-offline-rc1-'+hashlib.sha256(raw).hexdigest()[:16]
    assert source==build['source_sha256']
    archive_files={}
    with tarfile.open(path,mode='r:gz') as t:
        members=t.getmembers();names=[m.name for m in members]
        assert names==sorted(set(names))
        for m in members:
            part=Path(m.name)
            assert m.isfile() and not part.is_absolute() and '..' not in part.parts
            assert m.uid==m.gid==m.mtime==0 and m.mode==0o644
            data=t.extractfile(m).read();assert len(data)==m.size
            archive_files[m.name]=data
    assert set(archive_files)==set(source)|{'_release/SOURCE-SHA256.json','_release/requirements-offline.lock','_release/CANDIDATE.json'}
    for n,h in source.items():assert hashlib.sha256(archive_files[n]).hexdigest()==h,n
    assert archive_files['_release/SOURCE-SHA256.json']==raw
    assert archive_files['_release/requirements-offline.lock']==(P/'release/requirements-offline.lock').read_bytes()
    info=json.loads(archive_files['_release/CANDIDATE.json']);assert info['release_id']==build['release_id'] and info['real_execution_enabled'] is False
    for n,h in read('INDEPENDENT-REVIEW.json')['source_sha256'].items():assert hashlib.sha256(archive_files[n]).hexdigest()==h,n
    assert read('CANDIDATE-PUBLICATION-REPLAY.json')['archive_unchanged']
    for n in source:
        parts=Path(n).parts
        assert parts[0] not in {'data','logs','models'} and not set(parts)&{'node_modules','.git'} and Path(n).name!='config.yaml' and not Path(n).name.startswith('.env')
    for n,data in archive_files.items():
        if n.startswith('app/') and n.endswith('.py'):ast.parse(data,filename=n)
    return build,archive_files

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--archive-only',action='store_true');ap.add_argument('--check-working-source',action='store_true');args=ap.parse_args()
    build,archive=verify_archive()
    result={'status':'PASS','release_id':build['release_id'],'archive_sha256':build['archive_sha256'],'public_source_files':len(build['source_sha256']),'real_execution_enabled':False}
    if args.archive_only:
        print(json.dumps(result,indent=2));return
    names=manifest(P,P/'SHA256SUMS')
    actual={str(f.relative_to(P)) for f in P.rglob('*') if f.is_file() and not f.is_symlink() and f!=P/'SHA256SUMS'}
    assert names==actual,'packet inventory drift'
    links={str(f.relative_to(P)):str(f.readlink()) for f in P.rglob('*') if f.is_symlink()}
    assert links==read('SYMLINKS.json')
    baseline=read('BASELINE.json')
    for n,h in baseline['prior_files'].items():assert sha(MAIN/n)==h,n
    log=(MAIN/'tasks/loop-log.md').read_bytes();assert hashlib.sha256(log[:baseline['log_bytes']]).hexdigest()==baseline['log_sha256']
    completion=read('COMPLETION-LOG.json');entry=completion['entry'].encode()
    assert log[completion['offset']:completion['offset']+len(entry)]==entry
    assert hashlib.sha256(entry).hexdigest()==completion['sha256']
    results=read('RESULTS.json');app={n:h for n,h in build['source_sha256'].items() if n.startswith('app/') and n.endswith('.py')}
    assert len(app)==102
    for mode,info in results['final_runs'].items():
        d=P/'runs'/info['run'];r=json.loads((d/'RUN.json').read_text())
        assert r['mode']==mode and r['status']=='PASS' and r['guard_stop'] is None and r['source_sha256']==app
        assert r['runner_sha256']==sha(P/'run_checks.py')==info['runner_sha256']
        assert sha(d/'INPUT-SHA256SUMS')==r['input_manifest_sha256']==info['input_manifest_sha256']
        manifest(d/'input',d/'INPUT-SHA256SUMS')
        for folder in ['tests','regressions','repository/tests']:
            for f in (d/'input'/folder).rglob('*.py'):
                n='tests/'+str(f.relative_to(d/'input'/folder))
                if n in archive:assert f.read_bytes()==archive[n],str(f)
    optional=read('OPTIONAL-DEPENDENCIES.json')
    assert set(optional['files'])=={str(f.relative_to(P/'optional-target')) for f in (P/'optional-target').rglob('*') if f.is_file()}
    for n,h in optional['files'].items():assert sha(P/'optional-target'/n)==h,n
    crash=read('CRASH-RECOVERY.json')['observed_current_source_cases']
    assert len(crash['signed_transport'])==15 and len(crash['registry_witness'])==22
    assert all(c['exitcode']==-9 and c['new_endpoint_invocations']==0 for c in crash['signed_transport'])
    assert results['repository_collected']==927 and results['repository_passed']==918 and results['repository_deselected']==9
    assert results['distinct_pytest_cases_passed']==998 and results['supplemental_authority_packet_cases']==80
    assert results['application_scenario_groups']==20 and results['benchmark_cases']==13
    proposal=read('LIVE-READONLY-PROPOSAL.json');assert proposal['candidate_archive_sha256']==build['archive_sha256'] and proposal['request_id'] is None and proposal['maximum_guest_actions']==1
    for n,h in proposal['standalone_broker_source_sha256'].items():assert sha(MAIN/n)==h,n
    if args.check_working_source:
        root=MAIN.parent/'JARVIS-release-r1'
        for n,h in build['source_sha256'].items():assert sha(root/n)==h,n
        result['working_candidate_matches']=True
    result.update(packet_files=len(names),symlinks=len(links),prior_files_verified=len(baseline['prior_files']),distinct_pytest_cases=998,repository_deselected=9,recorded_SIGKILL_cases=37,canonical_log_preserved=True,packet_manifest_sha256=sha(P/'SHA256SUMS'))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
