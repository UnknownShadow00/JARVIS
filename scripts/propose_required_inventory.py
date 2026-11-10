#!/usr/bin/env python3
"""Offline maintainer tool: execute known-good suites to propose a NEW inventory.

Never called by acceptance. Output must be new; review its diff before manually
promoting it to scripts/required_tests.json. Uses the frozen R2 collector in a
public-code disposable copy and the existing namespace cage.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import hashlib

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b199acede69962919933d5bca364a587b1a2e8ca'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('choose a new candidate output')
    body=dict(version=1,baseline=BASE,suites={})
    with tempfile.TemporaryDirectory(prefix='jarvis-inventory-proposal-') as tmp:
        root=Path(tmp)
        for folder in ('app','tests','scripts'):
            shutil.copytree(ROOT/folder,root/folder,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
        for f in ('pytest.ini','config.yaml.example'):shutil.copy2(ROOT/f,root/f)
        runner=subprocess.check_output(['git','show',BASE+':scripts/reliability_gauntlet.py'],cwd=ROOT,text=True)
        runner=runner.replace("    elif mode == 'r2':", "    elif mode == 'r3':\n        files = ['test_required_inventory_r3.py']\n    elif mode == 'reconciliation':\n        files = ['test_release_security.py', 'test_ue5_security.py', 'test_baseline_enrollment.py']\n    elif mode == 'r2':")
        runner=runner.replace("    modes.add_argument('--r2'", "    modes.add_argument('--r3', action='store_true')\n    modes.add_argument('--reconciliation', action='store_true')\n    modes.add_argument('--r2'")
        runner=runner.replace("mode = 'existing' if args.existing", "mode = 'reconciliation' if args.reconciliation else 'r3' if args.r3 else 'existing' if args.existing")
        runner=runner.replace('print(json.dumps(report, allow_nan=False))', "report['discovered_nodeids'] = [n.removeprefix('/source/') for n in identities]\n    print(json.dumps(report, allow_nan=False))")
        runner=re.sub(r'normalized = validate\(json.loads\(raw, parse_constant=invalid_constant\), run_id=run_id,\s+seed=args.seed, mode=mode, returncode=proc.returncode\)', "discovered = json.loads(raw, parse_constant=invalid_constant)\n            nodeids = discovered.pop('discovered_nodeids')\n            normalized = validate(discovered, run_id=run_id, seed=args.seed, mode=mode, returncode=proc.returncode)\n            normalized['discovered_nodeids'] = nodeids",runner)
        runner=runner.replace("'--size', '67108864'", "'--ro-bind', str(root / 'scripts/required_test_inventory.py'), '/required_test_inventory.py', '--ro-bind', str(root / 'scripts/test_enrollment.py'), '/test_enrollment.py', '--size', '67108864'")
        runner=runner.replace("'--dir', '/input',", "'--dir', '/input', '--ro-bind', str(root / 'tests/fixtures/baseline_api.py'), '/input/baseline_api.py', '--ro-bind', str(root / 'tests/fixtures/ancestor_hypothesis.py'), '/input/ancestor_hypothesis.py',")
        (root/'scripts/reliability_gauntlet.py').write_text(runner)
        modes={'reconciliation':['--reconciliation'], 'new':[], 'r2':['--r2'],'r3':['--r3'],'existing':['--existing'],'probe':['--probe','--scenario-timeout','1']}
        cases=('early_setup','early_call','early_teardown','final_exit','skip','crash','interrupt','leak','parameter_secret','empty','worker_crash','partial_output','mismatched_count','session_exit')
        # Probe identities are explicit public fixture identities, not harvested
        # from interrupted executions that cannot produce a terminal report.
        for mode,flags in modes.items():
            output=root/(mode+'.json')
            process = subprocess.run(['python3','-B',str(root/'scripts/reliability_gauntlet.py'),*flags,'--output',str(output)],stdout=subprocess.DEVNULL)
            result = json.loads(output.read_text())
            if mode != 'probe' and (process.returncode != 0 or result['counts']['PASS'] != result['collected'] or not result['collected']):
                with args.output.with_suffix('.failure.json').open('x') as failure:
                    json.dump(result,failure,indent=2)
                raise SystemExit('candidate collection did not fully pass')
            nodes=sorted(json.loads(output.read_text())['discovered_nodeids'])
            body['suites'][mode]=dict(nodeids=nodes,sources={})
        for case in cases:
            names=['test_'+case] if case!='final_exit' else ['test_final_exit_control','test_final_exit_last']
            nodes=[] if case=='empty' else ['tests/fixtures/reliability_completion_probe.py::'+n+('[SYNTHETIC_PRIVATE_PROBE]' if case=='parameter_secret' else '') for n in names]
            body['suites']['case:'+case]=dict(nodeids=sorted(nodes),sources={})
        for suite in body['suites'].values():
            paths={n.split('::')[0] for n in suite['nodeids']} | {'pytest.ini', 'config.yaml.example'}
            paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'app').rglob('*.py'))
            paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'tests').rglob('conftest.py'))
            suite['sources']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}
    with args.output.open('x') as f:json.dump(body,f,indent=2);f.write('\n')

if __name__=='__main__':main()
