#!/usr/bin/env python3
"""Fresh networkless cage, verified read-only dependencies, owned bounded files."""
from datetime import UTC, datetime
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
PRIOR = ROOT / "tasks/jarvis-fixture-integration-r1"


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def limits():
    for key, pair in [(resource.RLIMIT_AS, (1073741824, 1073741824)), (resource.RLIMIT_CPU, (120,121)), (resource.RLIMIT_FSIZE, (67108864,67108864)), (resource.RLIMIT_NOFILE, (64,64)), (resource.RLIMIT_CORE, (0,0))]:
        resource.setrlimit(key, pair)


def descendants(root):
    rows = {}
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit(): continue
        try:
            data = (entry/'stat').read_text().rsplit(')',1)[1].split()
            rows[int(entry.name)] = (int(data[1]), data[19], int(data[21])*os.sysconf('SC_PAGE_SIZE'))
        except (FileNotFoundError, ProcessLookupError, PermissionError): continue
    owned = {root}
    while True:
        new = {pid for pid, row in rows.items() if row[0] in owned}
        if new <= owned: break
        owned |= new
    return {pid: rows[pid] for pid in owned if pid in rows}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=['core','full-app','focused','benchmark'],default='core')
    parser.add_argument('--target',type=Path,required=True)
    args=parser.parse_args()
    now = datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ')
    run = PACKET / 'runs' / now
    run.mkdir(mode=0o700, parents=True)
    memory = {line.split(':')[0]:line.split(':')[1].strip() for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:', 'SwapFree:'))}
    headroom = {'at': now, 'memory': memory, 'load':os.getloadavg(), 'cpus':os.cpu_count(), 'disk_free':shutil.disk_usage(ROOT).free, 'worktrees':subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True)}
    (run/'HEADROOM.json').write_text(json.dumps(headroom,indent=2)+'\n')
    assert int(memory['MemAvailable'].split()[0]) >= 3*1024**2
    assert headroom['disk_free'] >= 3*1024**3 and headroom['load'][0] < os.cpu_count()
    assert sha(PRIOR/'SHA256SUMS') == '8ebf51763947ca18a9cff2be2308fe9e764a26aa9c6000b02510ecf2b8e31761'
    assert sha(PRIOR/'MATERIALIZED-SHA256SUMS') == '6701baa39697b9e250429f8b77938fa3032ac747b1d9798fdee0196e11937a7d'
    for line in (PRIOR/'MATERIALIZED-SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        p=PRIOR/name
        assert not p.is_symlink() and sha(p)==digest,name
    assert sha(Path('/usr/bin/bwrap')) == '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
    assert sha(Path('/usr/bin/python3.14')) == '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
    old=json.loads((PRIOR/'SOURCE-ENVIRONMENT-AND-LIMITS.json').read_text())
    guard_hash=old['fixture_and_runner_sha256']['integration_child.py']
    assert sha(PRIOR/'integration_child.py')==guard_hash
    inputs,output=run/'input',run/'output'
    inputs.mkdir(mode=0o700);output.mkdir(mode=0o700);(output/'tmp').mkdir(mode=0o700)
    outside=run/'outside-canary.txt';outside.write_text('synthetic outside canary only\n')
    canary=b'synthetic readonly input\n';(inputs/'readonly-canary.txt').write_bytes(canary)
    (inputs/'guard.py').write_bytes((PRIOR/'integration_child.py').read_bytes())
    sources={}
    for source in sorted((ROOT/'app').rglob('*.py')):
        if source.is_symlink(): raise RuntimeError('source symlink refused')
        name=str(source.relative_to(ROOT));target=inputs/'source'/name
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());sources[name]=sha(source)
    # Public example only; never inspect real config/runtime state/credentials.
    if (ROOT/'config.yaml.example').exists():
        (inputs/'source/config.yaml').write_bytes((ROOT/'config.yaml.example').read_bytes())
    shutil.copytree(PACKET/'tests',inputs/'tests')
    for name in ['test_execution_pipeline.py', 'execution_process_actor.py', 'test_operator_ledger.py', 'ledger_process_actor.py','test_audit_disaster.py','audit_process_actor.py']:
        shutil.copyfile(ROOT/'tests'/name,inputs/'tests'/name)
    regressions=inputs/'regressions'
    regressions.mkdir()
    for name in ['test_reporter.py','test_resource_manager.py','test_server_auth.py','test_cancel_token.py','test_health_check.py','test_operator_app.py']:
        shutil.copyfile(ROOT/'tests'/name,regressions/name)
    if args.mode=='benchmark':
        shutil.copyfile(PACKET/'benchmark_workload.py',inputs/'benchmark_workload.py')
    child_name={'core':'child.py','full-app':'full_app_child.py','focused':'focused_child.py','benchmark':'benchmark_child.py'}[args.mode]
    (inputs/'child.py').write_bytes((PACKET/child_name).read_bytes())
    expected={'parent_namespaces':{n:os.readlink('/proc/self/ns/'+n) for n in ['user','mnt','pid','net','ipc','uts']},'outside_canary_path':str(outside),'readable_canary_sha256':hashlib.sha256(canary).hexdigest(),'guard_sha256':guard_hash,'source_sha256':sources,'versions':old['installed_versions_inside_child']}
    target=PRIOR/'work/integration-output/site-packages'
    if args.target:
        plan_path=ROOT/'tasks/jarvis-authority-readiness-r1/DEPENDENCY-PLAN.json'
        assert sha(plan_path)=='4d4614a61d80463b1b003d6c3d64ec474a0bcb630a130a9eb475716f4990ab16'
        assert sha(ROOT/'tasks/jarvis-authority-readiness-r1/full-app.lock')=='e2c32573cdd9b0b71f832ae6db6bc09b5222aef053ed815bfc317c0523f892b7'
        plan=json.loads(plan_path.read_text())
        assert plan['status']=='OFFICIAL_WHEEL_METADATA_PLAN_READY_NOT_INSTALLED' and not plan['blockers']
        expected['plan_sha256']=sha(plan_path)
        expected['versions']={n:r['version'] for n,r in plan['selected'].items()}
        (inputs/'plan.json').write_bytes(plan_path.read_bytes())
    if args.target:
        target=args.target.resolve()
        assert target.is_relative_to((ROOT/'tasks/jarvis-authority-readiness-r1/runs').resolve()) and target.name=='site-packages'
        manifest=target.parent.parent/'TARGET-SHA256SUMS'
        expected['target_manifest_sha256']=sha(manifest)
        prior_result=json.loads((target.parent.parent/'RUN.json').read_text())
        assert prior_result['status']=='PASS' and prior_result['child']['status']=='EXACT28_MATERIALIZED'
        names=set()
        for line in manifest.read_text().splitlines():
            digest,name=line.split('  ',1)
            assert '..' not in Path(name).parts and not Path(name).is_absolute()
            names.add(name)
            p=target/name
            assert not p.is_symlink() and sha(p)==digest,name
        actual=set()
        for p in target.rglob('*'):
            assert not p.is_symlink()
            if p.is_file():actual.add(str(p.relative_to(target)))
        assert actual==names,'materialized target inventory changed'
    if args.mode=='full-app':assert args.target,'full app requires fresh exact28 target'
    (inputs/'runner.py').write_bytes(Path(__file__).read_bytes())
    expected['runner_sha256']=sha(Path(__file__))
    (inputs/'expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    input_hashes={str(p.relative_to(inputs)):sha(p) for p in sorted(inputs.rglob('*')) if p.is_file()}
    (run/'INPUT-SHA256SUMS').write_text(''.join(f'{digest}  {name}\n' for name,digest in input_hashes.items()))
    argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--setenv','TZ','UTC','--cap-drop','ALL','--dir','/usr','--ro-bind','/usr/bin','/usr/bin','--ro-bind','/usr/lib','/usr/lib','--dir','/usr/share','--ro-bind','/usr/share/zoneinfo','/usr/share/zoneinfo','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--dir','/run','--ro-bind',str(inputs),'/input','--ro-bind',str(PRIOR/'work/integration-output/site-packages'),'/deps','--bind',str(output),'/work','--symlink','/work/tmp','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3','-I','-B','-S','/input/child.py']
    argv[argv.index(str(PRIOR/'work/integration-output/site-packages'))]=str(target)
    start=time.monotonic();stop=None;peak_rss=peak_files=peak_bytes=peak_processes=0
    with (run/'stdout.txt').open('x') as out,(run/'stderr.txt').open('x') as err:
        process=subprocess.Popen(argv,cwd=ROOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,start_new_session=True,preexec_fn=limits)
        while process.poll() is None:
            owned=descendants(process.pid)
            rss=sum(r[2] for r in owned.values());peak_rss=max(peak_rss,rss);peak_processes=max(peak_processes,len(owned))
            count=size=0
            for p in run.rglob('*'):
                try:
                    if not p.is_symlink() and p.is_file():count+=1;size+=p.stat().st_size
                except FileNotFoundError:pass
            peak_files=max(peak_files,count);peak_bytes=max(peak_bytes,size)
            if len(owned)>4 or rss>768*1024**2 or count>20000 or size>256*1024**2 or time.monotonic()-start>120:
                stop='owned workload guard threshold'
                for pid,row in reversed(list(owned.items())):
                    try:
                        current=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
                        if current[19]==row[1]:os.kill(pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    except FileNotFoundError:pass
                break
            time.sleep(.025)
        process.wait(timeout=5)
    child=json.loads((output/'RESULT.json').read_text()) if (output/'RESULT.json').exists() else None
    for name,digest in sources.items():assert sha(ROOT/name)==digest,name
    result={'at':now,'runner_sha256':expected['runner_sha256'],'input_manifest_sha256':sha(run/'INPUT-SHA256SUMS'),'exitcode':process.returncode,'elapsed_seconds':time.monotonic()-start,'guard_stop':stop,'limits':{'per_process_AS':1073741824,'aggregate_RSS':768*1024**2,'CPU':[120,121],'FSIZE':67108864,'NOFILE':64,'CORE':0,'wall_seconds':120,'controlled_files':20000,'controlled_bytes':256*1024**2,'maximum_payload_processes':2},'peak_observed_rss':peak_rss,'peak_observed_files':peak_files,'peak_observed_bytes':peak_bytes,'peak_owned_processes_including_bwrap':peak_processes,'argv':argv,'source_sha256':sources,'child':child,'status':'PASS' if process.returncode==0 and not stop else 'FAIL'}
    (run/'RUN.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'run':str(run.relative_to(ROOT)),'status':result['status'],'exitcode':process.returncode,'child':child},indent=2))
    return 0 if result['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
