"""Actual CLI refuses new/deleted/modified unreviewed modules before imports."""
from pathlib import Path
import shutil,tempfile,subprocess,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
if len(sys.argv)>1:OUT.mkdir(parents=True,exist_ok=False)
results=[]
for fault in ('added','deleted','changed','policy_tamper'):
 with tempfile.TemporaryDirectory(prefix='jarvis-enrollment-negative-') as tmp:
  r=Path(tmp)
  for folder in ('app','scripts','tests'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for f in ('pytest.ini','config.yaml.example'):shutil.copy2(ROOT/f,r/f)
  if fault=='added':(r/'tests/test_new_unreviewed.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_MUST_NOT_IMPORT')\n")
  if fault=='deleted':(r/'tests/test_scheduler_hardening_r2.py').unlink()
  if fault=='changed':(r/'tests/test_scheduler_hardening_r2.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_MUST_NOT_IMPORT')\n")
  if fault=='policy_tamper':(r/'scripts/test_enrollment.json').write_text('{}')
  cmd=['python3','-B',str(r/'scripts/reliability_gauntlet.py'),'--r2','--output',str(OUT/('enrollment-'+fault+'.json'))]
  with (OUT/('enrollment-'+fault+'.txt')).open('x') as f:p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
  raw=(OUT/('enrollment-'+fault+'.json')).read_text();d=json.loads(raw)
  passed=p.returncode!=0 and d['status']!='PASS' and 'child_exit_code' not in d and 'SYNTHETIC_PRIVATE' not in raw
  results.append(dict(case=fault,command=cmd,exit=p.returncode,passed=passed,status=d['status'],reason=d.get('reason')))
(OUT/'ENROLLMENT-CLI.json').write_text(json.dumps(results,indent=2));assert all(x['passed'] for x in results);print(results)
