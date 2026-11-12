"""Fresh late-execution/configuration and evidence attacks on disposable copies only."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

os.umask(0o077)
OUT=Path(__file__).resolve().parent
ROOT=Path(json.loads((OUT/'acceptance/RESULT.json').read_text())['source_snapshot'])
DEST=OUT/'additional-probes'
DEST.mkdir(mode=0o700,exist_ok=False)
hooks={
 'late_runloop_omit':"def pytest_runtestloop(session):\n    session.items.pop()\n",
 'late_skip':"def pytest_collection_finish(session):\n    session.items[0].add_marker(__import__('pytest').mark.skip(reason='PRIVATE_INTEGRATION_AUDIT'))\n",
 'late_xfail':"def pytest_collection_finish(session):\n    session.items[0].add_marker(__import__('pytest').mark.xfail(reason='PRIVATE_INTEGRATION_AUDIT',run=False))\n",
 'clean_early_exit':"def pytest_collection_finish(session):\n    __import__('pytest').exit('PRIVATE_INTEGRATION_AUDIT',returncode=0)\n",
}
rows=[]
for name in (*hooks,'config_keyword_filter','environment_control'):
 with tempfile.TemporaryDirectory(prefix='jarvis-integration-audit-probe-') as temporary:
  root=Path(temporary)
  for folder in ('app','tests','scripts','evals'):
   shutil.copytree(ROOT/folder,root/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for path in ('pytest.ini','config.yaml.example','docker-compose.yml','frontend/pwa/app.js','frontend/hologram/app.js','frontend/electron/preload.js'):
   (root/path).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/path,root/path)
  for p in root.rglob('*'):p.chmod(0o700 if p.is_dir() else 0o600)
  changed=[]
  if name in hooks:
   with (root/'tests/conftest.py').open('a') as stream:stream.write('\n'+hooks[name])
   changed=['tests/conftest.py']
  if name=='config_keyword_filter':
   p=root/'pytest.ini';p.write_text(p.read_text().replace('addopts = ','addopts = -k "not dictation" '));changed=['pytest.ini']
  if changed:
   # Explicitly authorize fixture source metadata, never alter expected identities.
   manifest=root/'scripts/required_tests.json';m=json.loads(manifest.read_text())
   policy=root/'scripts/test_enrollment.json';p=json.loads(policy.read_text())
   for path in changed:
    digest=hashlib.sha256((root/path).read_bytes()).hexdigest()
    if path in p['modules']:p['modules'][path]['sha256']=digest
    for suite in m['suites'].values():
     if path in suite['sources']:suite['sources'][path]=digest
   manifest.write_text(json.dumps(m));policy.write_text(json.dumps(p))
   loader=root/'scripts/required_test_inventory.py';loader.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+hashlib.sha256(manifest.read_bytes()).hexdigest()+'"',loader.read_text()))
   loader=root/'scripts/test_enrollment.py';loader.write_text(re.sub(r"ENROLLMENT_SHA256 = '[^']+'","ENROLLMENT_SHA256 = '"+hashlib.sha256(policy.read_bytes()).hexdigest()+"'",loader.read_text()))
  env=dict(os.environ)
  if name=='environment_control':env.update(PYTEST_ADDOPTS='--collect-only -k PRIVATE_INTEGRATION_AUDIT',PYTEST_PLUGINS='PRIVATE_INTEGRATION_AUDIT_PLUGIN')
  command=[sys.executable,'-B',str(root/'scripts/reliability_gauntlet.py'),'--coverage','--output',str(DEST/(name+'.json'))]
  with (DEST/(name+'.log')).open('x') as stream:process=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env=env,timeout=125)
  raw=(DEST/(name+'.json')).read_text();body=json.loads(raw)
  if name=='environment_control':
   passed=process.returncode==0 and body['status']=='PASS' and body['executed']==body['required_count']==217
  else:
   passed=process.returncode!=0 and body['status']!='PASS' and body.get('child_exit_code')==0
  if name=='late_runloop_omit':passed &= body['required_missing']==0 and body['counts']['INCOMPLETE']==1 and body['counts']['PASS']==216
  passed &= 'PRIVATE_INTEGRATION_AUDIT' not in raw
  rows.append(dict(case=name,passed=passed,command=command,exit=process.returncode,child_exit=body.get('child_exit_code'),status=body['status'],counts=body.get('counts'),missing=body.get('required_missing'),reason=body.get('reason')))

# Tampered report copies are rejected using original pinned bytes/phase requirements.
report=OUT/'acceptance/coverage.json';original=report.read_bytes();pinned=hashlib.sha256(original).hexdigest()
tampering=[]
for name in ('wrong_count','missing_phase','locally_resealed'):
 body=json.loads(original)
 if name=='wrong_count':body['counts']['PASS']=218
 else:body['scenarios'][0]['phases'].pop()
 path=DEST/(name+'.json');path.write_text(json.dumps(body));actual=hashlib.sha256(path.read_bytes()).hexdigest()
 if name=='locally_resealed':(DEST/'replacement-SHA256SUMS').write_text(actual+'  '+path.name+'\n')
 changed=actual!=pinned
 phases_ok=all([p['phase'] for p in s['phases']]==['setup','call','teardown'] for s in body['scenarios'])
 passed=changed and (body['counts']['PASS']!=len(body['scenarios']) or not phases_ok)
 tampering.append(dict(case=name,passed=passed,original_sha256=pinned,tampered_sha256=actual,original_pin_rejects=changed,locally_resealed=name=='locally_resealed'))
(DEST/'SUMMARY.json').write_text(json.dumps({'cli':rows,'tampering':tampering},indent=2))
print([(r['case'],r['passed']) for r in rows+tampering])
raise SystemExit(0 if all(r['passed'] for r in rows+tampering) else 1)
