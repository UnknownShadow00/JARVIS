"""Replay Codex2 selected groups and independent socket fixture sequentially."""
from pathlib import Path
import json,subprocess
P=Path(__file__).resolve().parent;MAIN=P.parents[1]
results=[]
for owner,name in [('regression','http_regressions_updated_final'),('regression','execution_regressions_updated_final'),('regression','transport_regressions_updated_final'),('regression','durability_regressions_final'),('authority','authority_socket_final_checked'),('integration','sprint6_replay_final'),('configuration','dependency_configuration')]:
    script=P/'agents'/owner/'scratch'/(name+'.py')
    log=P/(name+'-replay.txt')
    with log.open('x') as out:
        r=subprocess.run(['/usr/bin/python3','-I','-B','-S',str(P/'security_runner.py'),owner,str(script),'merged'],cwd=MAIN,stdout=out,stderr=subprocess.STDOUT,timeout=45)
    results.append({'owner':owner,'harness':name,'exitcode':r.returncode,'log':log.name})
    (P/'SECURITY-INVOCATIONS.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results[-1]),flush=True)
    if r.returncode:raise SystemExit(r.returncode)
