from pathlib import Path
import tempfile,shutil,subprocess,json,hashlib,re
ROOT=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-reliability-hardening-r3')
OUT=Path(__file__).resolve().parent
faults={
'late_omission':"def pytest_collection_finish(session):\n    session.items.pop()\n",
'late_substitution':"def pytest_collection_finish(session):\n    session.items[0]._nodeid='tests/test_scheduler_hardening_r2.py::test_AUDIT_PRIVATE'\n",
'keyword':"def pytest_configure(config):\n    config.option.keyword='not test_real_executor_cleanup_failure'\n",
'addition':"def test_AUDIT_PRIVATE_addition():\n    pass\n",
'config_changed':None,
'new_unselected_file':None,
'manifest_shrink':None,
'no_regeneration':None,
}
results=[]
for name,body in faults.items():
 with tempfile.TemporaryDirectory(prefix='r3-independent-') as tmp:
  r=Path(tmp)
  for folder in ('app','tests','scripts'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for f in ('pytest.ini','config.yaml.example'):shutil.copy2(ROOT/f,r/f)
  repin=name in ('late_omission','late_substitution','keyword','addition')
  if body:
   f=r/('tests/test_scheduler_hardening_r2.py' if name=='addition' else 'tests/conftest.py')
   with f.open('a') as stream:stream.write('\n'+body)
  if name=='config_changed':(r/'pytest.ini').write_text('[pytest]\naddopts=-k nonexistent\n')
  if name=='new_unselected_file':(r/'tests/test_new_audit_required.py').write_text('def test_new(): assert False\n')
  if name=='no_regeneration':(r/'scripts/propose_required_inventory.py').write_text("raise RuntimeError('AUDIT_PRIVATE_REGEN')\n")
  m=r/'scripts/required_tests.json';d=json.loads(m.read_text())
  if repin:
   for suite in d['suites'].values():
    for f in suite['sources']:suite['sources'][f]=hashlib.sha256((r/f).read_bytes()).hexdigest()
  if name=='manifest_shrink':d['suites']['r2']['nodeids']=d['suites']['r2']['nodeids'][1:]
  if repin or name=='manifest_shrink':m.write_text(json.dumps(d))
  if repin:
   loader=r/'scripts/required_test_inventory.py';loader.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+hashlib.sha256(m.read_bytes()).hexdigest()+'"',loader.read_text()))
  with (OUT/(name+'.txt')).open('x') as f:p=subprocess.run(['python3','-B',str(r/'scripts/reliability_gauntlet.py'),'--r2','--output',str(OUT/(name+'.json'))],stdout=f,stderr=subprocess.STDOUT)
  raw=(OUT/(name+'.json')).read_text();report=json.loads(raw)
  results.append(dict(case=name,exit=p.returncode,status=report['status'],counts=report.get('counts'),missing=report.get('required_missing'),unexpected=report.get('unexpected_collected'),secret_leak='AUDIT_PRIVATE' in raw))
(OUT/'independent-summary.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
