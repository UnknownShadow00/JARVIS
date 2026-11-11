from pathlib import Path
import tempfile,shutil,subprocess,re,json
ROOT=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-baseline-reconciliation-r1');OUT=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='baseline-audit-extra-') as tmp:
 r=Path(tmp)
 for folder in ('app','tests','scripts'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
 for f in ('pytest.ini','config.yaml.example'):shutil.copy2(ROOT/f,r/f)
 (r/'tests/test_independent_ready.py').write_bytes((OUT/'ready_boundary.py').read_bytes())
 import hashlib
 policy=r/'scripts/test_enrollment.json';coverage=json.loads(policy.read_text());coverage['modules']['tests/test_independent_ready.py']=dict(disposition='required',reason='explicit independent diagnostic fixture',sha256=hashlib.sha256((r/'tests/test_independent_ready.py').read_bytes()).hexdigest());policy.write_text(json.dumps(coverage))
 checker=r/'scripts/test_enrollment.py';checker.write_text(re.sub(r"ENROLLMENT_SHA256 = '[^']+'","ENROLLMENT_SHA256 = '"+hashlib.sha256(policy.read_bytes()).hexdigest()+"'",checker.read_text()))
 runner=r/'scripts/reliability_gauntlet.py';s=runner.read_text().replace("files = ['test_release_security.py', 'test_ue5_security.py', 'test_baseline_enrollment.py']", "files = ['test_audit_integration_fixes.py','test_computer_safety.py','test_dictation.py','test_sensor_store.py','test_independent_ready.py']")
 s=s.replace('    print(json.dumps(report, allow_nan=False))', "    report['audit_names'] = {v:k for k,v in identities.items()}\n    print(json.dumps(report, allow_nan=False))")
 s=s.replace('            normalized = validate(json.loads(raw, parse_constant=invalid_constant), run_id=run_id,',"            body=json.loads(raw, parse_constant=invalid_constant)\n            names=body.pop('audit_names')\n            normalized = validate(body, run_id=run_id,")
 s=s.replace('            report.update(normalized)',"            report.update(normalized)\n            report['audit_names']=names")
 runner.write_text(s)
 with (OUT/'extra-ready.log').open('x') as log:p=subprocess.run(['python3','-B',str(runner),'--reconciliation','--output',str(OUT/'extra-ready.json')],stdout=log,stderr=subprocess.STDOUT)
 d=json.loads((OUT/'extra-ready.json').read_text());print('gate exit',p.returncode,'child',d.get('child_exit_code'),d.get('counts'))
 for case in d.get('scenarios',[]):
  if case['status']!='PASS':print(d['audit_names'][case['id']],case['status'])
