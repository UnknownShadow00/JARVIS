"""Run exact current source offline with immutable test mounts and before/after hashes."""
from pathlib import Path
import hashlib,json,subprocess,concurrent.futures,sys
ROOT=Path(__file__).resolve().parents[2];TOOL=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else TOOL
if OUT!=TOOL:OUT.mkdir(parents=True,exist_ok=False)

def snapshot():
    paths=[p for folder in ('app','tests') for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT/'scripts'/n for n in ('gauntlet_protocol.py','reliability_gauntlet.py','required_test_inventory.py','required_tests.json','test_enrollment.py','test_enrollment.json','propose_required_inventory.py')]
    paths += [ROOT/'pytest.ini',ROOT/'config.yaml.example']
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
before=snapshot();jobs={n:['scripts/reliability_gauntlet.py',*flags,'--output',str(OUT/('final-'+n+'.json'))] for n,flags in [('reconciliation',['--reconciliation']),('r3',['--r3']),('r2',['--r2']),('original',[]),('existing',['--existing']),('reconciliation-seed42',['--reconciliation','--seed','42']),('r3-seed42',['--r3','--seed','42']),('r2-seed42',['--r2','--seed','42']),('original-seed42',['--seed','42'])]}
jobs['negative14']=['scripts/reliability_gate_checks.py','--output-dir',str(OUT/'final-negative14')]
jobs['gate22']=[str(TOOL/'check_gate_contracts.py'),'--output-dir',str(OUT/'final-gate22')]
def run(pair):
 name,args=pair;cmd=['python3','-B',*args]
 with (OUT/('final-'+name+'.txt')).open('x') as f:process=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 return dict(name=name,command=cmd,exit=process.returncode)
results=list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(run,jobs.items()));after=snapshot()
(OUT/'FINAL-RUNS.json').write_text(json.dumps(dict(runs=results,source_before=before,source_after=after,source_unchanged=before==after),indent=2))
print([(r['name'],r['exit']) for r in results]);assert before==after and all(r['exit']==0 for r in results)
