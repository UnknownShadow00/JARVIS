"""Sequential offline modes; all detailed results remain in exclusive run folders."""
from pathlib import Path
import subprocess,json,time
P=Path(__file__).resolve().parent;MAIN=P.parents[1]
results=[]
for mode in ['core','focused','full-app','enrollment','recovery','benchmark']:
    log=P/(mode+'-verification-r2.txt')
    with log.open('x') as out:
        r=subprocess.run(['/usr/bin/python3','-I','-B','-S',str(P/'run_checks.py'),'--mode',mode,'--target',str(MAIN/'tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages')],cwd=MAIN,stdout=out,stderr=subprocess.STDOUT,timeout=200)
    results.append({'mode':mode,'exitcode':r.returncode,'log':log.name})
    print(json.dumps(results[-1]),flush=True)
    (P/'REMAINING-INVOCATIONS.json').write_text(json.dumps(results,indent=2)+'\n')
    if r.returncode:raise SystemExit(r.returncode)
