"""Replay into a new exclusive packet; never mutate this sealed release packet."""
from pathlib import Path
from datetime import datetime,UTC
import hashlib,json,shutil,subprocess
P=Path(__file__).resolve().parent;MAIN=P.parents[1];W=MAIN.parent/'JARVIS-unified-rc1'
build=json.loads((P/'release/BUILD.json').read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=W,text=True).strip()==build['git_revision']
assert subprocess.check_output(['git','status','--porcelain'],cwd=W)==b''
for n,h in build['source_sha256'].items():assert hashlib.sha256((W/n).read_bytes()).hexdigest()==h,n
new=MAIN/'tasks'/('jarvis-v2-unified-rc1-replay-'+datetime.now(UTC).strftime('%Y%m%dT%H%M%S%fZ'));new.mkdir(mode=0o700)
for name in ['run_checks.py','run_all.py','child.py','broad_child.py','focused_child.py','full_app_child.py','enrollment_child.py','recovery_child.py','benchmark_child.py','benchmark_workload.py','integration_application.py','integration_benchmark.py','enrollment_application.py','enrollment_benchmark.py','recovery_application.py','recovery_benchmark.py','ancestor_hypothesis.py','OPTIONAL-DEPENDENCIES.json','selection.json','security_runner.py','run_security_pinned.py','SECURITY-DEPENDENCY-SHA256.json']:
 shutil.copyfile(P/name,new/name)
for name in ['tests','before','fixtures','security-source']:shutil.copytree(P/name,new/name)
for owner in ['regression','authority','integration','configuration']:
 target=new/'agents'/owner/'scratch';target.mkdir(parents=True)
 for f in (P/'agents'/owner/'scratch').glob('*.py'):
  if not f.stem.endswith('_pinned'):shutil.copyfile(f,target/f.name)
(new/'ORIGIN.json').write_text(json.dumps({'original_packet':str(P),'archive_sha256':build['archive_sha256'],'git_revision':build['git_revision']},indent=2)+'\n')
print('Fresh replay packet:',new,flush=True)
for name in ['run_all.py','run_security_pinned.py']:
 r=subprocess.run(['/usr/bin/python3','-I','-B','-S',str(new/name)],cwd=MAIN)
 if r.returncode:raise SystemExit(r.returncode)
print('All replay modes passed. Original sealed packet unchanged.',flush=True)
