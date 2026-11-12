"""Safe invocation/preflight contracts; never executes excluded test modules."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile

os.umask(0o077)
ROOT=Path('/tmp/jarvis-final-safety-r2-independent-vbpwlozy/checkout')
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,mode=0o700,exist_ok=False)
rows=[]
jobs=[('script_inventory',[sys.executable,'-B','scripts/offline_acceptance.py','--list-required'],False),
      ('module_inventory',[sys.executable,'-B','-m','scripts.offline_acceptance','--list-required'],False),
      ('reject_partial',[sys.executable,'-B','scripts/offline_acceptance.py','--coverage','--output-dir',str(OUT/'not-created')],True),
      ('reject_private_marker',[sys.executable,'-B','-m','scripts.offline_acceptance','-k','SYNTHETIC_PRIVATE_SELECTION'],True)]
protected=OUT/'existing';protected.mkdir();marker=protected/'preserved';marker.write_text('synthetic evidence')
before=hashlib.sha256(marker.read_bytes()).hexdigest()
jobs.append(('existing_output',[sys.executable,'-B','scripts/offline_acceptance.py','--output-dir',str(protected)],True))
forbidden=ROOT/'app/.offline-safety-output-must-not-exist'
if forbidden.exists():raise SystemExit('choose unused diagnostic path')
jobs.append(('forbidden_source_output',[sys.executable,'-B','scripts/offline_acceptance.py','--output-dir',str(forbidden)],True))
for name,command,negative in jobs:
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
    (OUT/(name+'.stdout')).write_text(p.stdout);(OUT/(name+'.stderr')).write_text(p.stderr)
    body=json.loads(p.stdout)
    good=(p.returncode!=0 and body['status']!='PASS') if negative else p.returncode==0 and body['status']=='INVENTORY_ONLY_NOT_ACCEPTANCE' and len(body['nodeids'])==922
    # Exact sensitive probe input stays in this reproduction fixture, not JSON.
    safe_command=['<redacted-synthetic-argument>' if 'SYNTHETIC_PRIVATE' in arg else arg for arg in command]
    rows.append(dict(case=name,command=safe_command,command_sha256=hashlib.sha256(json.dumps(command).encode()).hexdigest(),exit=p.returncode,status=body['status'],passed=good and 'SYNTHETIC_PRIVATE' not in p.stdout))
with tempfile.TemporaryDirectory(prefix='jarvis-empty-qualified-bundle-') as empty:
    # In-memory dependency fault only; original source/env is never modified.
    code="import importlib.util,sys;from pathlib import Path;"+"spec=importlib.util.spec_from_file_location('qualified_fault',sys.argv[1]);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.DEPS=Path(sys.argv[2]);sys.argv=[sys.argv[1],'--output-dir',sys.argv[3]];raise SystemExit(m.main())"
    command=[sys.executable,'-B','-c',code,str(ROOT/'scripts/offline_acceptance.py'),empty,str(OUT/'unqualified-output')]
    p=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=30)
    (OUT/'unqualified.stdout').write_text(p.stdout);(OUT/'unqualified.stderr').write_text(p.stderr)
    body=json.loads((OUT/'unqualified-output/RESULT.json').read_text())
    rows.append(dict(case='unqualified_bundle',command=command,exit=p.returncode,status=body['status'],passed=p.returncode!=0 and body['status']=='BLOCKED' and not (OUT/'unqualified-output/RUNS.json').exists()))
assert hashlib.sha256(marker.read_bytes()).hexdigest()==before and not forbidden.exists()
assert json.loads((OUT/'script_inventory.stdout').read_text())==json.loads((OUT/'module_inventory.stdout').read_text())
(OUT/'SUMMARY.json').write_text(json.dumps(rows,indent=2))
print([(r['case'],r['passed']) for r in rows])
raise SystemExit(0 if len(rows)==7 and all(r['passed'] for r in rows) else 1)
