"""Offline-only green regression and unchanged independent assertions replay."""
import contextlib,importlib.util,io,json,os,socket,subprocess,sys,unittest,types
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')];sys.dont_write_bytecode=True
import packet,results,fixtures,proposals,test_regression,test_design
CANON=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS')
def deny(*a,**k):raise AssertionError('offline process/network/signaling tripwire')
def run(name,module):
 stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module));(ROOT/'evidence'/f'{name}.log').write_text(stream.getvalue())
 return dict(tests=result.testsRun,passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),failed=len(result.failures),errors=len(result.errors),skips=len(result.skipped))
with contextlib.ExitStack() as stack:
 for obj,name in ((subprocess,'Popen'),(os,'system'),(os,'kill'),(os,'killpg'),(socket,'socket'),(socket,'create_connection')):stack.enter_context(patch.object(obj,name,deny))
 spec=importlib.util.spec_from_file_location('audit_replay',CANON/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r1/tests/test_independent.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
 audit.p=types.SimpleNamespace(**vars(packet));audit.p.cleanup_argv=lambda nonce,case,owned,current:packet.cleanup_argv(nonce,case,owned,dict(current));audit.results=results;audit.ident=fixtures.ident;audit.session=fixtures.session;audit.sample=fixtures.sample;audit.ownership=fixtures.ownership
 audit.CAT={'install':proposals.install('/SYNTHETIC/canary.py',fixtures.session(),fixtures.sample()),'read':{'R19-policy-or-manual-read':proposals.protected_read('/SYNTHETIC/policy',1048576,'d'*64),'R20-manual-gzip-read':proposals.protected_read('/SYNTHETIC/man.gz',1048576,'d'*64,True)}}
 original_catalog=json.loads((CANON/'tasks/jarvis-v2-vm164-stage2-operator-preparation-r1/COMMAND-CATALOG.json').read_bytes())
 test_design.CAT=original_catalog
 design_before=run('design-original-red',test_design)
 assert (design_before['passed'],design_before['failed'],design_before['errors'],design_before['skips'])==(0,3,0,0)
 test_design.CAT=__import__('catalog').build()
 design_after=run('design-r2-green',test_design)
 report={'kind':'OFFLINE_SYNTHETIC_ONLY','design_original_expected_red':design_before,'design_r2':design_after,'audit30_r2':run('green-audit30',audit),'regression':run('regression',test_regression)}
 (ROOT/'evidence/R2-TEST-RESULTS.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 if any(r['failed'] or r['errors'] or r['skips'] for k,r in report.items() if isinstance(r,dict) and k!='design_original_expected_red'):sys.exit(1)
