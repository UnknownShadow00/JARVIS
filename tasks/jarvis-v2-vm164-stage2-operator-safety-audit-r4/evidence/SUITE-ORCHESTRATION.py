from pathlib import Path
import json,subprocess,concurrent.futures,shutil
s=json.loads(Path('/tmp/r4audit-state.json').read_text());A=Path(s['audit']);P=Path(s['candidate']);T=Path(s['disposable']);B=Path(s['original_audit'])
commands=[(n,['python3','-I','-B','-S',str(P/'tests/replay_after.py'),n]) for n in ['baseline','r2','negative','adversarial','astra39','r4']]+[('original39',['python3','-I','-B','-S',str(B/'tests/run_fresh.py')])]
def run(pair):
 n,a=pair;r=subprocess.run(a,cwd=T,capture_output=True,text=True,timeout=240);(A/'evidence'/f'{n}.stdout').write_text(r.stdout);(A/'evidence'/f'{n}.stderr').write_text(r.stderr);return {'phase':n,'argv':a,'timeout_seconds':240,'exit':r.returncode}
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:rows=list(ex.map(run,commands))
for n in ['BASELINE','R2','NEGATIVE','ADVERSARIAL','ASTRA39','R4']:shutil.copyfile(P/'evidence'/f'{n}-RESULTS.json',A/'evidence'/f'{n}-RESULTS.json')
for f in (P/'evidence').glob('*.log'):shutil.copyfile(f,A/'evidence'/f.name)
for n in ['FRESH.log','FRESH-RESULTS.json','FRESH-OBSERVED.json']:shutil.copyfile(B/'evidence'/n,A/'evidence'/('ORIGINAL-'+n))
(A/'evidence/SUITE-PROCESSES.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows,indent=2))
