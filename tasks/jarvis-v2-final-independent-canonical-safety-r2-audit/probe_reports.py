"""Safe in-memory subprocess/evidence faults against actual outer CLI.

Uses retained fresh child reports as simulated job outputs; these are negative
contracts, not additional real test executions. Source remains unchanged.
"""
from pathlib import Path
import contextlib, copy, importlib.util, io, json, shutil, subprocess, sys
A=Path(__file__).resolve().parent
C=Path(json.loads((A/'CHECKOUT.json').read_text())['path'])
BASE=A/'acceptance-script'
spec=importlib.util.spec_from_file_location('independent_outer_probe',C/'scripts/offline_acceptance.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
original_run=m.subprocess.run
rows=[]
for fault in ['missing','duplicate','substitution','skip','interruption','collection_incomplete','malformed','no_terminal','valid_control']:
 out=A/'outer-report-probes-v2'/fault
 def fake_run(command, **kwargs):
  if '--output' not in command and '--output-dir' not in command:
   return original_run(command, **kwargs)
  if '--output' in command:
   dest=Path(command[command.index('--output')+1]);src=BASE/dest.name;shutil.copyfile(src,dest)
   if dest.name=='safety.json':
    b=json.loads(dest.read_text())
    if fault=='missing':
     b['scenarios'].pop();b['executed']-=1;b['counts']['PASS']-=1
    elif fault=='duplicate':b['scenarios'][1]['id']=b['scenarios'][0]['id']
    elif fault=='substitution':b['scenarios'][0]['id']='0'*64
    elif fault=='skip':b['scenarios'][0]['phases'][1]['outcome']='skipped'
    elif fault=='interruption':b['session']['interrupted']=True
    elif fault=='collection_incomplete':b['session']['collected']=False
    if fault=='malformed':dest.write_text('{')
    elif fault=='no_terminal':dest.unlink()
    else:dest.write_text(json.dumps(b))
  else:
   dest=Path(command[command.index('--output-dir')+1]);shutil.copytree(BASE/dest.name,dest)
  return subprocess.CompletedProcess(command,0)
 m.subprocess.run=fake_run
 sys.argv=[str(C/'scripts/offline_acceptance.py'),'--output-dir',str(out)]
 capture=io.StringIO()
 try:
  with contextlib.redirect_stdout(capture):exitcode=m.main()
 finally:m.subprocess.run=original_run
 body=json.loads((out/'RESULT.json').read_text())
 ok=exitcode==0 and body['status']=='PASS' if fault=='valid_control' else exitcode!=0 and body['status']!='PASS'
 assert ok,(fault,exitcode,body['status'])
 rows.append(dict(case=fault,simulated_subprocess_exit=0,outer_exit=exitcode,status=body['status'],passed=ok,runs_preserved=(out/'RUNS.json').exists(),stdout=capture.getvalue()))
(A/'REPORT-PROBES.json').write_text(json.dumps(rows,indent=2)+'\n')
print([(r['case'],r['outer_exit'],r['status']) for r in rows])
