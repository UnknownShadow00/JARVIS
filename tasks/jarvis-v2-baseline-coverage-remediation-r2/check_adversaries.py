"""Actual offline CLI adversaries. Mutations and explicit rebinding are fixture-only."""
from pathlib import Path
import shutil,tempfile,subprocess,json,hashlib,re,sys
ROOT=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else Path(__file__).resolve().parents[2];OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=False)
results=[]
for fault in ('added','deleted','changed','policy_tamper','manifest_tamper','module_omission','parameter_omission','substitution','unexpected_exclusion','excluded_selection','regeneration_trap'):
 with tempfile.TemporaryDirectory(prefix='jarvis-coverage-adversary-') as tmp:
  r=Path(tmp)
  for folder in ('app','tests','scripts','evals'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for f in ('pytest.ini','config.yaml.example','docker-compose.yml','frontend/pwa/app.js','frontend/hologram/app.js','frontend/electron/preload.js'):
   (r/f).parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/f,r/f)
  policy=r/'scripts/test_enrollment.json';manifest=r/'scripts/required_tests.json';p=json.loads(policy.read_text());m=json.loads(manifest.read_text())
  if fault=='added':(r/'tests/test_not_reviewed.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_IMPORT')\n")
  if fault=='deleted':(r/'tests/test_dictation.py').unlink()
  if fault=='changed':(r/'tests/test_dictation.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_IMPORT')\n")
  if fault=='policy_tamper':policy.write_text('{}')
  if fault=='manifest_tamper':manifest.write_text('{}')
  if fault in ('module_omission','parameter_omission','substitution'):
   hook={'module_omission':"items[:]=[i for i in items if 'test_dictation.py' not in i.nodeid]",'parameter_omission':"items.remove(next(i for i in items if '[' in i.nodeid))",'substitution':"items[0]._nodeid='tests/test_dictation.py::test_SYNTHETIC_PRIVATE_REPLACEMENT'"}[fault]
   with (r/'tests/conftest.py').open('a') as f:f.write('\ndef pytest_collection_modifyitems(items):\n    '+hook+'\n')
   n='tests/conftest.py';h=hashlib.sha256((r/n).read_bytes()).hexdigest();p['modules'][n]['sha256']=h
   for suite in m['suites'].values():suite['sources'][n]=h
   policy.write_text(json.dumps(p));manifest.write_text(json.dumps(m))
   loader=r/'scripts/required_test_inventory.py';loader.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+hashlib.sha256(manifest.read_bytes()).hexdigest()+'"',loader.read_text()))
  if fault=='unexpected_exclusion':
   p['modules']['tests/test_dictation.py']['disposition']='excluded_offline_scope';policy.write_text(json.dumps(p))
  if fault=='excluded_selection':
   (r/'scripts/coverage_modules.json').write_text('["boot_test.py"]')
   (r/'tests/boot_test.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_NEVER_IMPORT')\n")
   p['modules']['tests/boot_test.py']['sha256']=hashlib.sha256((r/'tests/boot_test.py').read_bytes()).hexdigest();policy.write_text(json.dumps(p))
  if fault in ('module_omission','parameter_omission','substitution','unexpected_exclusion','excluded_selection'):
   loader=r/'scripts/test_enrollment.py';loader.write_text(re.sub(r"ENROLLMENT_SHA256 = '[^']+'", "ENROLLMENT_SHA256 = '"+hashlib.sha256(policy.read_bytes()).hexdigest()+"'",loader.read_text()))
  if fault=='regeneration_trap':(r/'scripts/propose_required_inventory.py').write_text("raise RuntimeError('SYNTHETIC_PRIVATE_REGENERATION_FORBIDDEN')\n")
  command=['python3','-B',str(r/'scripts/reliability_gauntlet.py'),'--coverage','--output',str(OUT/(fault+'.json'))]
  with (OUT/(fault+'.log')).open('x') as log:proc=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,timeout=125)
  raw=(OUT/(fault+'.json')).read_text();d=json.loads(raw)
  passed=(proc.returncode==0 and d['counts']['PASS']==217) if fault=='regeneration_trap' else proc.returncode!=0 and d['status']!='PASS'
  passed=passed and 'SYNTHETIC_PRIVATE' not in raw
  if fault=='module_omission':passed=passed and d.get('required_missing')==6 and d.get('child_exit_code')==0
  if fault=='parameter_omission':passed=passed and d.get('required_missing')==1 and d.get('child_exit_code')==0
  if fault=='substitution':passed=passed and d.get('required_missing')==1 and d.get('unexpected_collected')==1 and d.get('child_exit_code')==0
  if fault in ('added','deleted','changed','policy_tamper','manifest_tamper','unexpected_exclusion','excluded_selection'):passed=passed and 'child_exit_code' not in d
  results.append(dict(case=fault,passed=passed,command=command,exit=proc.returncode,child_exit=d.get('child_exit_code'),status=d['status'],counts=d.get('counts'),missing=d.get('required_missing'),unexpected=d.get('unexpected_collected'),reason=d.get('reason')))
(OUT/'SUMMARY.json').write_text(json.dumps(results,indent=2));print([(x['case'],x['passed']) for x in results]);raise SystemExit(0 if all(x['passed'] for x in results) else 1)
