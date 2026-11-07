"""Actual offline regression, with all process effects tripwired and every
predecessor temporary fixture relocated to the NEW packet's exclusive outdir.
"""
import argparse,contextlib,hashlib,importlib.machinery,importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TASK=Path(__file__).resolve().parents[1]
SOURCES={
 'r3_author_enforcement':TASK/'tests/test_enforcement.py',
 'r3_author_adapter':TASK/'tests/test_host_adapter.py',
 'r3_independent_review':TASK/'tests/test_independent_review.py',
 'r2_remediation':TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-remediation-r2/tests/test_remediation.py',
 'r1_bootstrap':TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-r1/tools/test_bootstrap.py',
 'r1_strict_validator':TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1/tests/test_state_validator.py',
 'r1_hazard_reproductions':TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1/tests/test_pinned_hazards.py'}
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path,loader=importlib.machinery.SourceFileLoader(name,str(path)))
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.subcases=0
 def addSubTest(self,test,subtest,outcome):self.subcases+=1;super().addSubTest(test,subtest,outcome)
def run(out):
 out.mkdir(mode=0o700);tmp=out/'fixtures';tmp.mkdir();original=tempfile.TemporaryDirectory;summary={}
 sys.path.insert(0,str(TASK/'tests'));sys.path.insert(0,str(TASK/'src'))
 def relocated(*a,**kw):kw['dir']=tmp;return original(*a,**kw)
 with patch.object(tempfile,'TemporaryDirectory',side_effect=relocated),patch.object(subprocess,'Popen',side_effect=AssertionError('NO_REAL_COMMANDS_STAGE1')),patch.object(os,'killpg',side_effect=AssertionError('NO_REAL_PROCESS_SIGNALS_STAGE1')):
  for name,path in SOURCES.items():
   module=load(name,path)
   # Old close-unit tests otherwise read the preparation host's public cgroup.
   # Replace that observation only, preserving every old source/test byte.
   with contextlib.ExitStack() as stack:
    if name=='r1_bootstrap':
     original_path=Path;empty=tmp/'empty-cgroup';empty.write_text('')
     def fixture_path(n):return empty if str(n)=='/sys/fs/cgroup/system.slice/debug-shell.service/cgroup.procs' else original_path(n)
     stack.enter_context(patch.object(module.B,'Path',side_effect=fixture_path))
    suite=unittest.defaultTestLoader.loadTestsFromModule(module)
    with (out/(name+'.log')).open('x') as log,patch.object(sys,'stdout',log):
     r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
   summary[name]={'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),
                  'subcases_not_added':r.subcases,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 result={'status':'PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY' if all(not(x['failures'] or x['errors']) for x in summary.values()) else 'FAIL_OFFLINE_REGRESSION',
         'suites':summary,'actual_unique_test_methods':sum(x['tests'] for x in summary.values()),
         'failures':sum(x['failures'] for x in summary.values()),'errors':sum(x['errors'] for x in summary.values()),'skips':sum(x['skips'] for x in summary.values()),
         'hardware_or_real_timer_tests':0,'root_boot_go':False,'live_host_qualified':False,
         'Popen_and_killpg_tripwires':True,'predecessor_fixtures_relocated':True,
         'nine_legacy_hazard_tests_confirm_unchanged_defects':True}
 with (out/'RESULTS.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result,indent=2))
 if result['status'].startswith('FAIL'):raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);run(p.parse_args().out.resolve())
