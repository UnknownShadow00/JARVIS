"""Actual offline CLI adversaries in public disposable copies. Never changes inventory IDs.

Instrumented source hashes are explicitly repinned ONLY in fixture copies so
collection/execution checks (rather than source pin checks) receive the faults.
Acceptance never performs this operation. Before uses exact committed R2 runner.
"""
from pathlib import Path
import tempfile,shutil,subprocess,json,hashlib,argparse
ROOT=Path(__file__).resolve().parents[2]
parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,required=True);parser.add_argument('--baseline-r2',action='store_true');args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=False)
CASES={
'astra':('module',"import pytest\npytest.skip('SYNTHETIC_PRIVATE_MODULE',allow_module_level=True)\n"),
'omitted_module':('hook',"items[:]=[i for i in items if 'test_scheduler_hardening_r2.py' not in i.nodeid]"),
'omitted_parameter':('hook',"items[:]=[i for i in items if not ('test_inflight_cleanup' in i.name and '[cancel]' in i.nodeid)]"),
'collection_importorskip':('module',"import pytest\npytest.importorskip('SYNTHETIC_PRIVATE_MISSING_PACKAGE')\n"),
'ignore_pattern':('ignore',''),
'marker':('marker',''),
'duplicate':('hook','items.append(items[0])'),
'substitution':('hook',"items[0]._nodeid='tests/test_scheduler_hardening_r2.py::test_SYNTHETIC_PRIVATE_REPLACEMENT'"),
'exit0_missing':('hook','items.pop()'),
'empty':('hook','items.clear()'),
'interrupt':('module',"import pytest\ndef test_interrupted():\n    pytest.exit('SYNTHETIC_PRIVATE_INTERRUPT',returncode=0)\n"),
'xfail':('hook',"items[0].add_marker(__import__('pytest').mark.xfail(reason='SYNTHETIC_PRIVATE_XFAIL',run=False))"),
'xpass':('hook',"items[0].add_marker(__import__('pytest').mark.xfail(reason='SYNTHETIC_PRIVATE_XPASS'))"),
'no_collection_complete':('finish',''),
'no_execution_result':('protocol',''),
'missing_terminal':('terminal',''),
'partial_terminal':('partial',''),
'invalid_manifest':('invalid',''),
'duplicate_manifest':('dupe_manifest',''),
'full':('full',''),
'source_changed':('source',''),
'reduced_manifest':('reduced',''),
}
results=[]
selected = [(name,CASES[name]) for name in ('astra','omitted_module','omitted_parameter','marker','substitution','exit0_missing','xpass')] if args.baseline_r2 else [('before-astra',CASES['astra']),*((n,v) for n,v in CASES.items() if n!='ignore_pattern')]
for name,(kind,body) in selected:
 with tempfile.TemporaryDirectory(prefix='jarvis-r3-cli-') as tmp:
  root=Path(tmp)
  for folder in ('app','tests','scripts'):shutil.copytree(ROOT/folder,root/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for f in ('config.yaml.example','pytest.ini'):shutil.copy2(ROOT/f,root/f)
  runner=root/'scripts/reliability_gauntlet.py'
  if name=='before-astra' or args.baseline_r2:
   for file in ('reliability_gauntlet.py','gauntlet_protocol.py'):
    (root/'scripts'/file).write_bytes(subprocess.check_output(['git','show','b199ace:scripts/'+file],cwd=ROOT))
  if kind=='source':(root/'tests/test_scheduler_hardening_r2.py').write_text('def test_replacement(): pass\n')
  if kind=='module':(root/'tests/test_scheduler_hardening_r2.py').write_text(body)
  if kind=='hook':
   with (root/'tests/conftest.py').open('a') as f:f.write('\ndef pytest_collection_modifyitems(items):\n    '+body+'\n')
  if kind=='marker':
   with (root/'tests/conftest.py').open('a') as f:f.write('\ndef pytest_collection_modifyitems(items):\n    items[0].add_marker(__import__("pytest").mark.r3exclude)\n')
   runner.write_text(runner.read_text().replace('*selection,',"'-m', 'not r3exclude', *selection,"))
  if kind=='ignore':
   # Directory traversal lets pytest's real ignore rule remove a required file.
   for f in list((root/'tests').rglob('test*.py')) + list((root/'tests').rglob('*_test.py')):
    if f.name not in ('test_scheduler_hardening_r2.py','test_gauntlet_protocol_r2.py'):f.unlink()
   for directory in (root/'tests').iterdir():
    if directory.is_dir():shutil.rmtree(directory)
   runner.write_text(runner.read_text().replace("files = ['test_scheduler_hardening_r2.py', 'test_gauntlet_protocol_r2.py']","files = ['.']").replace('*selection,',"'--ignore=/source/tests/test_scheduler_hardening_r2.py', *selection,"))
  if kind in ('terminal','partial'):
   with (root/'tests/conftest.py').open('a') as f:f.write('\ndef pytest_sessionfinish(session,exitstatus):\n    import os\n'+('    os.write(1,b\'{"protocol":\')\n' if kind=='partial' else '')+'    os._exit(0)\n')
  if kind=='finish':runner.write_text(runner.read_text().replace("state['collected'] = True","state['collected'] = False"))
  if kind=='protocol':runner.write_text(runner.read_text().replace("outcomes[identity]['phases'].append", "return\n            outcomes[identity]['phases'].append"))
  path=root/'scripts/required_tests.json';manifest=json.loads(path.read_text())
  for suite in manifest['suites'].values():
   for f in suite['sources']:
    if kind!='source' and (root/f).is_file():suite['sources'][f]=hashlib.sha256((root/f).read_bytes()).hexdigest()
  if kind=='reduced':manifest['suites']['r2']['nodeids']=manifest['suites']['r2']['nodeids'][14:]
  if kind=='invalid':manifest['version']=99
  if kind=='dupe_manifest':manifest['suites']['r2']['nodeids']*=2
  path.write_text(json.dumps(manifest))
  # Authorize fixture metadata only; never performed by the gate itself.
  loader=root/'scripts/required_test_inventory.py'
  import re
  if kind not in ('invalid','dupe_manifest','reduced'):
   loader.write_text(re.sub(r'INVENTORY_SHA256 = "[^"]*"', 'INVENTORY_SHA256 = "'+hashlib.sha256(path.read_bytes()).hexdigest()+'"',loader.read_text()))
  # Fixture-only policy source rebinding; production acceptance never does this.
  policy=root/'scripts/test_enrollment.json'
  coverage=json.loads(policy.read_text())
  coverage['modules']={n:e for n,e in coverage['modules'].items() if (root/n).is_file()}
  for n,e in coverage['modules'].items():e['sha256']=hashlib.sha256((root/n).read_bytes()).hexdigest()
  policy.write_text(json.dumps(coverage))
  checker=root/'scripts/test_enrollment.py'
  checker.write_text(re.sub(r"ENROLLMENT_SHA256 = '[^']+'", "ENROLLMENT_SHA256 = '"+hashlib.sha256(policy.read_bytes()).hexdigest()+"'",checker.read_text()))
  output=args.output_dir/(name+'.json')
  with (args.output_dir/(name+'.txt')).open('x') as f:proc=subprocess.run(['python3','-B',str(runner),'--r2','--output',str(output)],stdout=f,stderr=subprocess.STDOUT,timeout=125)
  raw=output.read_text();d=json.loads(raw)
  correct=proc.returncode==0 and d['counts']['PASS']==31 if name=='before-astra' else proc.returncode==0 and d['counts']['PASS']==45 if name=='full' else proc.returncode!=0 and d['status']!='PASS'
  if name=='ignore_pattern':correct=correct and d.get('required_missing')==14 and d.get('child_exit_code')==0 and d['counts']['PASS']==31
  if args.baseline_r2:correct=proc.returncode==0 and d['status']=='PASS'
  correct=correct and 'SYNTHETIC_PRIVATE' not in raw
  results.append(dict(case=name,contract_pass=correct,exit=proc.returncode,status=d['status'],counts=d.get('counts'),missing=d.get('required_missing'),reason=d.get('reason'),child_exit=d.get('child_exit_code')))
(args.output_dir/'SUMMARY.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
raise SystemExit(0 if all(x['contract_pass'] for x in results) else 1)
