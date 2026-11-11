from pathlib import Path
import tempfile,shutil,subprocess,json,hashlib,re,sys,os
os.umask(0o077)
ROOT=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve();OUT.mkdir(mode=0o700,exist_ok=False)
results=[]
for fault in ('remove_module','import_skip','late_parameter_drop','late_substitution','duplicate','new_module','unapproved_source','corrupt_digest','zero_exit_subset','unapproved_exclusion','private_exception','unsafe_selection'):
 with tempfile.TemporaryDirectory(prefix='jarvis-final-coverage-audit-') as tmp:
  r=Path(tmp)
  for folder in ('app','tests','scripts','evals'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for n in ('pytest.ini','config.yaml.example','docker-compose.yml','frontend/pwa/app.js','frontend/hologram/app.js','frontend/electron/preload.js'):(r/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/n,r/n)
  # Change permissions ONLY in the disposable clone.
  for copied in r.rglob("*"):
   copied.chmod(0o700 if copied.is_dir() else 0o600)
  changed=[]
  if fault=='remove_module':(r/'tests/test_dictation.py').unlink()
  if fault=='import_skip':(r/'tests/test_dictation.py').write_text("import pytest\npytest.skip('SYNTHETIC_AUDIT_PRIVATE',allow_module_level=True)\n");changed=['tests/test_dictation.py']
  if fault=='new_module':(r/'tests/test_new_audit.py').write_text("raise RuntimeError('SYNTHETIC_AUDIT_PRIVATE')\n")
  if fault=='unapproved_source':(r/'tests/test_dictation.py').write_text("raise RuntimeError('SYNTHETIC_AUDIT_PRIVATE')\n")
  if fault in ('late_parameter_drop','late_substitution','duplicate','zero_exit_subset','private_exception'):
   bodies={
    'late_parameter_drop':"def pytest_collection_finish(session):\n    session.items.remove(next(i for i in session.items if '[' in i.nodeid))\n",
    'late_substitution':"def pytest_collection_finish(session):\n    session.items[0]._nodeid='tests/test_dictation.py::test_SYNTHETIC_AUDIT_PRIVATE'\n",
    'duplicate':"def pytest_collection_modifyitems(items):\n    items.append(items[0])\n",
    'zero_exit_subset':"def pytest_collection_modifyitems(items):\n    del items[:3]\n",
    'private_exception':"def pytest_runtest_call(item):\n    if item.name=='test_dictation_config_defaults_require_opt_in':\n        raise RuntimeError(\"No module named 'SYNTHETIC_AUDIT_PRIVATE' token=synthetic payload=synthetic\")\n"}
   with (r/'tests/conftest.py').open('a') as f:f.write('\n'+bodies[fault])
   changed=['tests/conftest.py']
  policy=r/'scripts/test_enrollment.json';manifest=r/'scripts/required_tests.json';p=json.loads(policy.read_text());m=json.loads(manifest.read_text())
  if fault=='unapproved_exclusion':p['modules']['tests/test_dictation.py']['disposition']='excluded_offline_scope';policy.write_text(json.dumps(p))
  if fault=='unsafe_selection':
   (r/'scripts/coverage_modules.json').write_text('["boot_test.py"]')
   (r/'tests/boot_test.py').write_text("raise RuntimeError('SYNTHETIC_AUDIT_PRIVATE_NO_EFFECTS')\n")
   changed=['tests/boot_test.py']
  if changed:
   for n in changed:
    h=hashlib.sha256((r/n).read_bytes()).hexdigest();p['modules'][n]['sha256']=h
    for suite in m['suites'].values():
     if n in suite['sources']:suite['sources'][n]=h
   policy.write_text(json.dumps(p));manifest.write_text(json.dumps(m))
   f=r/'scripts/test_enrollment.py';f.write_text(re.sub(r"ENROLLMENT_SHA256 = '[^']+'","ENROLLMENT_SHA256 = '"+hashlib.sha256(policy.read_bytes()).hexdigest()+"'",f.read_text()))
   f=r/'scripts/required_test_inventory.py';f.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+hashlib.sha256(manifest.read_bytes()).hexdigest()+'"',f.read_text()))
  if fault=='corrupt_digest':
   f=r/'scripts/required_test_inventory.py';f.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+'0'*64+'"',f.read_text()))
  cmd=['python3','-B',str(r/'scripts/reliability_gauntlet.py'),'--coverage','--output',str(OUT/(fault+'.json'))]
  with (OUT/(fault+'.log')).open('x') as f:process=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=125)
  raw=(OUT/(fault+'.json')).read_text();d=json.loads(raw)
  results.append(dict(case=fault,command=cmd,exit=process.returncode,child_exit=d.get('child_exit_code'),status=d['status'],counts=d.get('counts'),missing=d.get('required_missing'),unexpected=d.get('unexpected_collected'),reason=d.get('reason'),secret_leaked='SYNTHETIC_AUDIT_PRIVATE' in raw))
(OUT/'SUMMARY.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2));assert all(x['exit']!=0 and x['status']!='PASS' and not x['secret_leaked'] for x in results)
