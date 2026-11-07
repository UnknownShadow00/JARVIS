"""Run actual offline suites; relocate every predecessor fixture to NEW evidence.

A process-wide Popen tripwire blocks any unexpected executable. Test-specific
mocks may simulate calls. No service, guest, Proxmox, network or application runs.
"""
import argparse,hashlib,importlib.machinery,importlib.util,io,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
TASK=Path(__file__).resolve().parents[1]
SOURCES={
 'r2_remediation':TASK/'tests/test_remediation.py',
 'r1_pinned_bootstrap':TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-r1/tools/test_bootstrap.py',
 'r1_offline_validator':TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1/tests/test_state_validator.py',
 'r1_known_hazard_reproductions':TASK.parent/'jarvis-v2-vm164-unattended-offline-readiness-r1/tests/test_pinned_hazards.py',
}
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path,loader=importlib.machinery.SourceFileLoader(name,str(path)))
 m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
class Result(unittest.TextTestResult):
 def __init__(self,*a,**kw):super().__init__(*a,**kw);self.subcases=0
 def addSubTest(self,test,subtest,outcome):self.subcases+=1;super().addSubTest(test,subtest,outcome)
def run(out):
 out.mkdir(mode=0o700);tmp=out/'fixtures';tmp.mkdir();original=tempfile.TemporaryDirectory;summary={}
 def relocated(*a,**kw):kw['dir']=tmp;return original(*a,**kw)
 with patch.object(tempfile,'TemporaryDirectory',side_effect=relocated),patch.object(subprocess,'Popen',side_effect=AssertionError('UNEXPECTED_EXECUTABLE_OFFLINE_TRIPWIRE')):
  for name,path in SOURCES.items():
   module=load(name,path);suite=unittest.defaultTestLoader.loadTestsFromModule(module)
   with (out/(name+'.log')).open('x') as log:
    with patch.object(sys,'stdout',log):r=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=Result).run(suite)
   summary[name]={'tests':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),'subcases_observed_not_added_to_tests':r.subcases,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 d={'status':'PASS_OFFLINE_ONLY' if all(not(r['errors'] or r['failures']) for r in summary.values()) else 'FAIL',
    'suites':summary,'unique_test_methods':sum(r['tests'] for r in summary.values()),
    'failures':sum(r['failures'] for r in summary.values()),'errors':sum(r['errors'] for r in summary.values()),'skips':sum(r['skips'] for r in summary.values()),
    'actual_hardware_or_root_qualification_tests':0,'actions_executed':False,
    'known_hazard_methods_are_reproductions_not_remediation':9,'root_boot_go':False,
    'fixture_writes_relocated_to_new_packet':True}
 with (out/'RESULTS.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps(d,indent=2))
 if d['status']!='PASS_OFFLINE_ONLY':raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);run(p.parse_args().out.resolve())
