#!/usr/bin/env python3
"""One focused lightweight reader run, existing cage/deps, no installer/services."""
import ast
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import subprocess
import time

ROOT=Path(__file__).resolve().parents[2]
PACKET=Path(__file__).resolve().parent
PRIOR=ROOT/'tasks/jarvis-authority-readiness-r1'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert sha(PRIOR/'SHA256SUMS')=='840451e8b09397793e72fbada08ef7dc82d86b5f41ea93e8d731162d283202a8'
    review=json.loads((PRIOR/'RESULTS.json').read_text())['reviewed_source_sha256']
    for name,digest in review.items():assert sha(ROOT/name)==digest,name
    original=PRIOR/'run_checks.py'
    pinned=next(line.split('  ',1)[0] for line in (PRIOR/'SOURCE-SHA256SUMS').read_text().splitlines() if line.endswith('  tasks/jarvis-authority-readiness-r1/run_checks.py'))
    assert sha(original)==pinned
    helpers=[n for n in ast.parse(original.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name in {'limits','descendants'}]
    assert len(helpers)==2
    exec(compile(ast.Module(body=helpers,type_ignores=[]),str(original),'exec'),globals())
    guard=ROOT/'tasks/jarvis-fixture-integration-r1/integration_child.py'
    assert sha(guard)=='6b17e85d8ceb342e35d5880e0e041bdd48cd35a44afec1484c26830e969cad86'
    assert sha(Path('/usr/bin/bwrap'))=='523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
    assert sha(Path('/usr/bin/python3.14'))=='52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
    target_run=PRIOR/'runs/20261031T090522534346Z'
    manifest=target_run/'TARGET-SHA256SUMS'
    assert sha(manifest)=='5ebe69febf0efdbc3c47ba528fb3c3e9ad083e99c4a201c87e0bef69db854635'
    target=target_run/'output/site-packages';names=set()
    for line in manifest.read_text().splitlines():
        digest,name=line.split('  ',1);path=target/name
        assert not path.is_symlink() and sha(path)==digest
        names.add(name)
    assert {str(p.relative_to(target)) for p in target.rglob('*') if p.is_file()}==names
    now=datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ');run=PACKET/'runs'/now
    run.mkdir(mode=0o700,parents=True)
    memory={s.split(':',1)[0]:s.split(':',1)[1].strip() for s in Path('/proc/meminfo').read_text().splitlines() if s.startswith(('MemAvailable:','SwapFree:'))}
    headroom={'at':now,'memory':memory,'load':os.getloadavg(),'cpus':os.cpu_count(),'disk_free':shutil.disk_usage(ROOT).free,'worktrees':subprocess.check_output(['git','worktree','list','--porcelain'],cwd=ROOT,text=True),'scheduling':'parent released NEW Nexus reservation; D4.1 active; focused reader only','own_overlap':subprocess.run(['pgrep','-af','^python3 -I -B -S tasks/jarvis-client-compatibility-r1/run_reader_checks.py$'],capture_output=True,text=True).stdout}
    (run/'HEADROOM.json').write_text(json.dumps(headroom,indent=2)+'\n')
    assert int(memory['MemAvailable'].split()[0])>=3*1024**2 and headroom['disk_free']>=3*1024**3 and headroom['load'][0]<os.cpu_count()
    # pgrep can report this runner itself; an additional matching runner blocks.
    assert len(headroom['own_overlap'].splitlines())<=1
    inputs,output=run/'input',run/'output'
    inputs.mkdir(mode=0o700);output.mkdir(mode=0o700);(output/'tmp').mkdir(mode=0o700)
    outside=run/'outside-canary.txt';outside.write_text('synthetic outside sentinel\n')
    canary=b'new reader readonly sentinel\n';(inputs/'readonly-canary.txt').write_bytes(canary)
    (inputs/'guard.py').write_bytes(guard.read_bytes())
    sources={}
    for path in sorted((ROOT/'app').rglob('*.py')):
        assert not path.is_symlink()
        name=str(path.relative_to(ROOT));dest=inputs/'source'/name
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(path.read_bytes());sources[name]=sha(path)
    (inputs/'child.py').write_bytes((PACKET/'child.py').read_bytes())
    (inputs/'test_reporter.py').write_bytes((ROOT/'tests/test_reporter.py').read_bytes())
    (inputs/'example.yaml').write_bytes((ROOT/'config.yaml.example').read_bytes())
    versions=json.loads((target_run/'RUN.json').read_text())['child']['versions']
    expected={'parent_namespaces':{n:os.readlink('/proc/self/ns/'+n) for n in ['user','mnt','pid','net','ipc','uts']},'outside_canary_path':str(outside),'readable_canary_sha256':hashlib.sha256(canary).hexdigest(),'guard_sha256':sha(guard),'source_sha256':sources,'tests_sha256':sha(ROOT/'tests/test_reporter.py'),'versions':versions}
    (inputs/'expected.json').write_text(json.dumps(expected,indent=2)+'\n')
    argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','LANG','C.UTF-8','--setenv','TZ','UTC','--cap-drop','ALL','--dir','/usr','--ro-bind','/usr/bin','/usr/bin','--ro-bind','/usr/lib','/usr/lib','--dir','/usr/share','--ro-bind','/usr/share/zoneinfo','/usr/share/zoneinfo','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--proc','/proc','--dev','/dev','--dir','/run','--ro-bind',str(inputs),'/input','--ro-bind',str(target),'/deps','--bind',str(output),'/work','--symlink','/work/tmp','/tmp','--chdir','/work','--remount-ro','/','--','/usr/bin/python3','-I','-B','-S','/input/child.py']
    start=time.monotonic();stop=None;peak_rss=peak_files=peak_bytes=peak_processes=0
    with (run/'stdout.txt').open('x') as out,(run/'stderr.txt').open('x') as err:
        child=subprocess.Popen(argv,cwd=ROOT,env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8'},stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,start_new_session=True,preexec_fn=limits)
        while child.poll() is None:
            owned=descendants(child.pid);rss=sum(r[2] for r in owned.values());peak_rss=max(peak_rss,rss);peak_processes=max(peak_processes,len(owned))
            files=[]
            for p in run.rglob('*'):
                try:
                    if not p.is_symlink() and p.is_file():files.append(p.stat().st_size)
                except FileNotFoundError:pass
            peak_files=max(peak_files,len(files));peak_bytes=max(peak_bytes,sum(files))
            if len(owned)>3 or rss>128*1024**2 or len(files)>2000 or sum(files)>16*1024**2 or time.monotonic()-start>15:
                stop='focused owned-workload threshold'
                for pid,row in reversed(list(owned.items())):
                    try:
                        current=Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()
                        if current[19]==row[1]:os.kill(pid,signal.SIGKILL)
                    except (FileNotFoundError,ProcessLookupError):pass
                break
            time.sleep(.025)
        child.wait(timeout=2)
    result=json.loads((output/'RESULT.json').read_text()) if (output/'RESULT.json').exists() else None
    for name,digest in sources.items():assert sha(ROOT/name)==digest,name
    assert sha(ROOT/'tests/test_reporter.py')==expected['tests_sha256']
    report={'status':'PASS' if child.returncode==0 and not stop else 'FAIL','exitcode':child.returncode,'elapsed_seconds':time.monotonic()-start,'guard_stop':stop,'peak_observed_aggregate_rss':peak_rss,'peak_controlled_files':peak_files,'peak_controlled_bytes':peak_bytes,'peak_owned_processes_with_supervisors':peak_processes,'limits':{'aggregate_RSS':128*1024**2,'wall_seconds':15,'controlled_files':2000,'controlled_bytes':16*1024**2,'payload_processes':1,'inherited_AS':1073741824,'inherited_CPU':[120,121],'inherited_FSIZE':67108864,'inherited_NOFILE':64,'inherited_CORE':0},'source_sha256':sources,'preserved_backend_sha256':review,'target_manifest_sha256':sha(manifest),'target_files':len(names),'installer_invoked':False,'child':result,'argv':argv}
    (run/'RUN.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'run':str(run.relative_to(ROOT)),'status':report['status'],'child':result,'elapsed_seconds':report['elapsed_seconds'],'peak_observed_aggregate_rss':peak_rss},indent=2))
    return 0 if report['status']=='PASS' else 2


if __name__=='__main__':raise SystemExit(main())
