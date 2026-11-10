"""Diagnostic only: current development app + narrow reliability delta,
against reviewed R3 offline tests. NOT final candidate acceptance.
No source conflict is resolved; current divergent app files are preserved.
"""
from pathlib import Path
import subprocess,json,tempfile,shutil,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[2]
REVIEW=ROOT.parent/'JARVIS-v2-reliability-hardening-r3'
OUT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='jarvis-rehearsal-blocker-') as tmp:
 r=Path(tmp)
 shutil.copytree(ROOT/'app',r/'app',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for name in ('app/agent/storage_paths.py','app/cli.py','app/comms/ue5_bridge.py','app/config.py','app/server.py'):
  (r/name).write_bytes(subprocess.check_output(['git','show','b738a473d27471f35df60d31ccd93047bf9d1a6e:'+name],cwd=ROOT))
 for folder in ('tests','scripts'):shutil.copytree(REVIEW/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for f in ('pytest.ini','config.yaml.example'):shutil.copy2(ROOT/f,r/f)
 # Only the four specifically reviewed application paths; no baseline-only file
 # is replaced. This is a disposable compatibility experiment, not integration.
 for f in ('authority.py','scheduler.py','scheduler_backend.py','simulation.py'):
  shutil.copy2(REVIEW/'app/agent'/f,r/'app/agent'/f)
 manifest=r/'scripts/required_tests.json';d=json.loads(manifest.read_text())
 for suite in d['suites'].values():
  for name in suite['sources']:suite['sources'][name]=hashlib.sha256((r/name).read_bytes()).hexdigest()
 manifest.write_text(json.dumps(d))
 loader=r/'scripts/required_test_inventory.py';loader.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]+"','INVENTORY_SHA256 = "'+hashlib.sha256(manifest.read_bytes()).hexdigest()+'"',loader.read_text()))
 def hashes():return {str(p.relative_to(r)):hashlib.sha256(p.read_bytes()).hexdigest() for p in r.rglob('*') if p.is_file()}
 before=hashes();command=['python3','-B',str(r/'scripts/reliability_gauntlet.py'),'--existing','--output',str(OUT/'compatibility-existing.json')]
 with (OUT/'compatibility-existing.txt').open('x') as f:process=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
 after=hashes();result=json.loads((OUT/'compatibility-existing.json').read_text())
 (OUT/'compatibility-provenance.json').write_text(json.dumps(dict(qualification='DIAGNOSTIC_ONLY_NOT_CANDIDATE_ACCEPTANCE',command=command,exit=process.returncode,source_unchanged=before==after,source_sha256=before,result_counts=result.get('counts')),indent=2))
 print(result.get('counts'),process.returncode)
