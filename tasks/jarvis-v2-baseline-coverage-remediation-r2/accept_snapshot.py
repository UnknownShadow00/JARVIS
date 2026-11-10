"""Offline acceptance on a retained read-only public snapshot, outputs separate.

Owner-only permissions are not independent custody. A same-UID/root writer can
change permissions; before/after hashes detect lasting source changes, not all
transient tampering. Never regenerates either acceptance inventory.
"""
from pathlib import Path
import os,sys,json,hashlib,shutil,tempfile,subprocess,concurrent.futures,stat
os.umask(0o077)
ROOT=Path(__file__).resolve().parents[2];TOOLS=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,mode=0o700,exist_ok=False)
PUBLIC_FILES=('pytest.ini','config.yaml.example','docker-compose.yml','frontend/pwa/app.js','frontend/hologram/app.js','frontend/electron/preload.js')
SCRIPTS=('gauntlet_protocol.py','reliability_gauntlet.py','reliability_gate_checks.py','required_test_inventory.py','required_tests.json','test_enrollment.py','test_enrollment.json','coverage_modules.json','propose_required_inventory.py','sensor_node.py')
def files(root):
 result=[f for folder in ('app','tests','evals') for f in (root/folder).rglob('*') if f.is_file() and '__pycache__' not in f.parts]
 result += [root/n for n in PUBLIC_FILES]+[root/'scripts'/n for n in SCRIPTS]
 result += [root/'tasks/jarvis-v2-baseline-coverage-remediation-r2'/n for n in ('accept_snapshot.py','check_gate_contracts.py','check_adversaries.py')]
 return sorted(set(result))
def hashes(root):return {str(f.relative_to(root)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files(root)}
before=hashes(ROOT)
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
if not set(before)<=tracked:raise SystemExit('all acceptance inputs must be committed')
commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip();tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip()
if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True):raise SystemExit('committed clean source required')
snapshot=Path(tempfile.mkdtemp(prefix='jarvis-coverage-acceptance-'))/'source';snapshot.mkdir()
for name in before:
 src=ROOT/name
 if src.is_symlink():raise SystemExit('source symlink requires explicit review')
 dst=snapshot/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);dst.chmod(0o444)
for d in sorted((x for x in snapshot.rglob('*') if x.is_dir()),key=lambda x:len(x.parts),reverse=True):d.chmod(0o555)
snapshot.chmod(0o555)
assert hashes(snapshot)==before
jobs={n:['scripts/reliability_gauntlet.py',*flags,'--output',str(OUT/(n+'.json'))] for n,flags in [('coverage',['--coverage']),('reconciliation',['--reconciliation']),('r3',['--r3']),('r2',['--r2']),('original',[]),('existing',['--existing']),('coverage-seed42',['--coverage','--seed','42']),('reconciliation-seed42',['--reconciliation','--seed','42']),('r3-seed42',['--r3','--seed','42']),('r2-seed42',['--r2','--seed','42']),('original-seed42',['--seed','42'])]}
jobs['negative14']=['scripts/reliability_gate_checks.py','--output-dir',str(OUT/'negative14')]
jobs['gate22']=[str(TOOLS/'check_gate_contracts.py'),'--source-root',str(snapshot),'--output-dir',str(OUT/'gate22')]
jobs['adversaries11']=[str(TOOLS/'check_adversaries.py'),str(OUT/'adversaries11'),str(snapshot)]
def run(pair):
 name,args=pair;command=[sys.executable,'-B',*args]
 with (OUT/(name+'.log')).open('x') as log:p=subprocess.run(command,cwd=snapshot,stdout=log,stderr=subprocess.STDOUT)
 return dict(name=name,command=command,exit=p.returncode)
runs=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(run,jobs.items()))
after=hashes(ROOT);snapshot_after=hashes(snapshot);integrity_ok=before==after==snapshot_after
ids=[];suites=[]
for n in ('coverage','reconciliation','r3','r2','original','existing'):
 body=json.loads((OUT/(n+'.json')).read_text());ids +=[s['id'] for s in body.get('scenarios',[])];suites.append(dict(name=n,counts=body.get('counts'),missing=body.get('required_missing'),unexpected=body.get('unexpected_collected'),exit=body['gate_exit_code']))
 ok=body['status']=='PASS' and body['gate_exit_code']==0 and body['required_missing']==body['unexpected_collected']==0 and body['executed']==body['required_count']
 ok=ok and all(s['complete'] and [p['phase'] for p in s['phases']]==['setup','call','teardown'] and all(p['outcome']=='passed' for p in s['phases']) for s in body['scenarios'])
 integrity_ok=integrity_ok and ok
for n in ('coverage','reconciliation','r3','r2','original'):
 a=json.loads((OUT/(n+'.json')).read_text());b=json.loads((OUT/(n+'-seed42.json')).read_text());integrity_ok &= b['status']=='PASS' and {s['id'] for s in a['scenarios']}=={s['id'] for s in b['scenarios']}
complete=integrity_ok and all(r['exit']==0 for r in runs) and len(ids)==len(set(ids))
report=dict(status='PASS' if complete else 'FAIL',qualification='OFFLINE_SNAPSHOT_ONLY',source_commit=commit,git_tree=tree,source_snapshot=str(snapshot),source_sha256=before,source_after_sha256=after,snapshot_after_sha256=snapshot_after,source_integrity=before==after==snapshot_after,content_tree_sha256=hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest(),required_inventory_sha256=before['scripts/required_tests.json'],module_policy_sha256=before['scripts/test_enrollment.json'],distinct_positive=len(set(ids)),repeat_executions=sum(json.loads((OUT/(n+'-seed42.json')).read_text())['counts']['PASS'] for n in ('coverage','reconciliation','r3','r2','original')),suites=suites,runs=runs,output_mode=oct(stat.S_IMODE(OUT.stat().st_mode)),independent_custody=False)
(OUT/'RESULT.json').write_text(json.dumps(report,indent=2))
(OUT/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(OUT))+'\n' for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS'))
print(report['status'],report['distinct_positive'],[(x['name'],x['exit']) for x in runs]);raise SystemExit(0 if complete else 1)
