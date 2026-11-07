from pathlib import Path
import tempfile,shutil,subprocess,json
ROOT=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-reliability-hardening-r2')
OUT=Path(__file__).resolve().parent
CASES={
 'collection-skip-repeat':("import pytest\npytest.skip('AUDIT_SYNTHETIC_SECRET_SKIP',allow_module_level=True)\n",True),
 'collection-error':("raise ImportError('AUDIT_SYNTHETIC_SECRET_IMPORT')\n",True),
 'collection-exit':("import pytest\npytest.exit('AUDIT_SYNTHETIC_SECRET_EXIT',returncode=0)\n",True),
 'adversarial-leaks':('''import pytest
@pytest.mark.parametrize('kind',[RuntimeError,ImportError,OSError,type('AUDIT_SYNTHETIC_SECRET_TYPE',(Exception,),{})],ids=['AUDIT_SYNTHETIC_SECRET_ID'+str(i) for i in range(4)])
def test_payload(kind):
    raise kind("No module named 'AUDIT_SYNTHETIC_SECRET_TOKEN' password=synthetic token=synthetic payload=synthetic")
''',False),
 'independent-scheduler':((OUT/'supplemental_scheduler.py').read_text(),False),
}
results=[]
for name,(body,r2) in CASES.items():
 with tempfile.TemporaryDirectory(prefix='jarvis-audit-r2-') as tmp:
  p=Path(tmp)
  for folder in ('app','tests','scripts'):shutil.copytree(ROOT/folder,p/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for f in ('config.yaml.example','pytest.ini'):shutil.copy2(ROOT/f,p/f)
  (p/'tests'/('test_scheduler_hardening_r2.py' if r2 else 'test_reliability_gauntlet.py')).write_text(body)
  cmd=['python3','-B',str(p/'scripts/reliability_gauntlet.py'),'--output',str(OUT/(name+'.json'))]
  if r2:cmd+=['--r2']
  with (OUT/(name+'.log')).open('x') as log:proc=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT)
  raw=(OUT/(name+'.json')).read_text();d=json.loads(raw)
  results.append(dict(case=name,exit=proc.returncode,status=d['status'],counts=d.get('counts'),secret_leaked='AUDIT_SYNTHETIC_SECRET' in raw))
(OUT/'supplemental-summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
