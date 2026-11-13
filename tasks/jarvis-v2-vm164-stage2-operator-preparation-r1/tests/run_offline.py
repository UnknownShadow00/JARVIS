"""Run fixture-only tests with process/network tripwires, retain actual results."""
import datetime,hashlib,io,json,os,socket,subprocess,sys,unittest
from pathlib import Path
from unittest.mock import patch
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tests'))
def forbidden(*a,**k):raise AssertionError('OFFLINE: process/network/signaling forbidden')
stream=io.StringIO()
with patch.object(subprocess,'Popen',forbidden),patch.object(os,'system',forbidden),patch.object(os,'kill',forbidden),patch.object(os,'killpg',forbidden),patch.object(socket,'socket',forbidden),patch.object(socket,'create_connection',forbidden):
 suite=unittest.defaultTestLoader.discover(str(root/'tests'),pattern='test_*.py')
 result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
out=root/'evidence'
(out/'offline-tests.log').write_text(stream.getvalue())
record={'kind':'OFFLINE_SYNTHETIC_TEST_RESULTS_NOT_HOST_EVIDENCE','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),
 'status':'PASS' if result.wasSuccessful() and not result.skipped else 'FAIL','host_commands_executed':False,
 'live_qualification':False,'stage2_authorized':False,'expiration_guaranteed':False,
 'source_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for d in ('src','tests') for p in sorted((root/d).glob('*.py'))}}
(out/'OFFLINE-RESULTS.json').write_text(json.dumps(record,indent=2)+'\n')
print(stream.getvalue());print(json.dumps(record,indent=2))
raise SystemExit(0 if record['status']=='PASS' else 1)
