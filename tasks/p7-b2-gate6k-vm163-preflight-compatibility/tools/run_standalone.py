"""Nexus-only unprivileged offline runner. No qualification entrypoint execution."""
import json,os,subprocess,sys
from pathlib import Path
STAGE=Path('/home/nexus/.local/share/jarvis-gate6k-preflight-fix/release-r1')
PYTHON='/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/bin/python'
program='''import sys,pathlib,unittest
p=pathlib.Path(sys.argv[1]);sys.path.insert(0,str(p))
from kernel_guard import restrict
print(restrict(p,pathlib.Path(sys.prefix)),flush=True)
suite=unittest.defaultTestLoader.discover(str(p/'disposable'),pattern='*tests.py')
result=unittest.TextTestRunner(verbosity=2).run(suite)
sys.exit(not result.wasSuccessful())
'''
if os.geteuid()==0 or os.uname().nodename!='nexus-services':raise RuntimeError('NEXUS_UNPRIVILEGED_ONLY')
env={'PATH':'/usr/bin:/bin','HOME':str(STAGE),'TMPDIR':str(STAGE),'PYTHONDONTWRITEBYTECODE':'1'}
log=STAGE.parent/'standalone-recorded.txt'
with log.open('x') as output:
    result=subprocess.run([PYTHON,'-B','-c',program,str(STAGE)],env=env,stdout=output,stderr=subprocess.STDOUT,timeout=120)
print(json.dumps({'exit':result.returncode,'log':str(log)}));sys.exit(result.returncode)
