from pathlib import Path
import tempfile,shutil,subprocess,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
import sys
name=sys.argv[1]
with tempfile.TemporaryDirectory(prefix='jarvis-coverage-diagnostic-') as tmp:
 r=Path(tmp)
 for folder in ('app','tests','scripts','evals','frontend'):shutil.copytree(ROOT/folder,r/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc','node_modules'))
 for f in ('pytest.ini','config.yaml.example','docker-compose.yml'):shutil.copy2(ROOT/f,r/f)
 runner=r/'scripts/reliability_gauntlet.py';s=runner.read_text()
 s=s.replace("inventory = load_inventory(Path(\"/inventory.json\"), Path(\"/source\"), mode, verify_sources=False)","inventory = load_inventory(Path(\"/inventory.json\"), Path(\"/source\"), 'reconciliation', verify_sources=False)")
 s=s.replace('root, mode)','root, \'reconciliation\')')
 s=s.replace("files = json.loads(Path('/coverage_modules.json').read_text())", "files = ['test_dictation.py']")
 s=s.replace("*selection,", "'-k', 'test_dictation_config_defaults_present', *selection,")
 s=s.replace('    print(json.dumps(report, allow_nan=False))',"    report['audit_names'] = {v:k for k,v in identities.items()}\n    print(json.dumps(report, allow_nan=False))")
 s=s.replace('            normalized = validate(json.loads(raw, parse_constant=invalid_constant), run_id=run_id,',"            body=json.loads(raw, parse_constant=invalid_constant)\n            names=body.pop('audit_names')\n            normalized = validate(body, run_id=run_id,")
 s=s.replace('            report.update(normalized)',"            report.update(normalized)\n            report['audit_names']=names")
 # Disable only fixture-copy module/source integrity to observe incompatibilities;
 # authoritative required identities and final acceptance are not updated here.
 s=s.replace('inventory = load_inventory(root / \"scripts/required_tests.json\", root, \'reconciliation\')', 'inventory = load_inventory(root / \"scripts/required_tests.json\", root, \'reconciliation\', verify_sources=False)')
 runner.write_text(s)
 with (OUT/(name+'.log')).open('x') as log:p=subprocess.run(['python3','-B',str(runner),'--coverage','--output',str(OUT/(name+'.json'))],stdout=log,stderr=subprocess.STDOUT)
 d=json.loads((OUT/(name+'.json')).read_text());print(p.returncode,d.get('counts'),d.get('reason'))
 for s in d.get('scenarios',[]):
  if s['status']!='PASS':print(d['audit_names'][s['id']],s['status'])
