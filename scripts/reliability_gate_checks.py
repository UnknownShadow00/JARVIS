#!/usr/bin/env python3
"""Exercise actual offline CLI failure modes; does not import application code."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

CASES = ('early_setup','early_call','early_teardown','final_exit','skip','crash','interrupt',
         'leak','parameter_secret','empty','worker_crash','partial_output','mismatched_count','session_exit')
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output-dir',type=Path,required=True,help='new directory for immutable reports')
args=parser.parse_args()
args.output_dir.mkdir(parents=True,exist_ok=False)
runner=Path(__file__).with_name('reliability_gauntlet.py')
results=[]
for case in CASES:
    report_path=args.output_dir/(case+'.json')
    with (args.output_dir/(case+'.txt')).open('x') as log:
        process=subprocess.run([sys.executable,str(runner),'--probe-case',case,'--output',str(report_path)],stdout=log,stderr=subprocess.STDOUT,timeout=125)
    raw=report_path.read_text()
    report=json.loads(raw)
    passed=process.returncode!=0 and report['status']!='PASS' and 'SYNTHETIC_PRIVATE' not in raw
    if case in {'early_setup','early_call','early_teardown','final_exit'}:
        passed = passed and report['counts']['INCOMPLETE']>=1
    if case=='session_exit':passed=passed and not report['session']['finished']
    if case=='empty':passed=passed and report['collected']==0
    if case=='worker_crash':passed=passed and report['child_exit_code']!=0
    if case=='partial_output':passed=passed and report['reason']=='malformed_completion_evidence'
    if case=='mismatched_count':passed=passed and report['reason']=='mismatched_test_count'
    results.append(dict(case=case,status='PASS' if passed else 'FAIL',gate_exit=process.returncode,
                        gate_status=report['status'],counts=report.get('counts'),reason=report.get('reason')))
with (args.output_dir/'SUMMARY.json').open('x') as output:
    json.dump(dict(checks=results,passed=sum(r['status']=='PASS' for r in results),failed=sum(r['status']!='PASS' for r in results)),output,indent=2)
for result in results:print(result['status'],result['case'])
raise SystemExit(0 if all(r['status']=='PASS' for r in results) else 1)
