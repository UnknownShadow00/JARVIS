"""Run copied-source tests under kernel restrictions plus the reviewed Python audit guard."""
import json,os,sys,time
from pathlib import Path
stage=Path(__file__).parent;repo=stage/'repo';label=sys.argv[1]
os.chdir(repo);sys.path.insert(0,str(repo));sys.dont_write_bytecode=True
from kernel_guard import restrict
policy=restrict(stage,Path(sys.prefix))
# The trusted supervisor is not a general signal proxy: it independently checks
# parent PID, UID, executable and private candidate cwd, then signals a pidfd.
if 'P7_TEST_REQUEST_FD' in os.environ:
 import subprocess,select
 request_fd=int(os.environ['P7_TEST_REQUEST_FD']);answer_fd=int(os.environ['P7_TEST_ANSWER_FD'])
 def fixture_signal(self,sig):
  if self.poll() is not None:return
  os.write(request_fd,(json.dumps({'pid':self.pid,'signal':int(sig)})+'\n').encode())
  if not select.select([answer_fd],[],[],5)[0]:raise RuntimeError('BROKER_TIMEOUT')
  if os.read(answer_fd,128)!=b'DISPOSABLE_CHILD_SIGNALED\n':raise PermissionError('BROKER_REFUSED')
 subprocess.Popen.send_signal=fixture_signal
# The Python audit guard is loaded by sitecustomize before this launcher.
import pytest
start=time.monotonic()
with (stage/(label+'.txt')).open('w') as log:
 oldout,olderr=sys.stdout,sys.stderr;sys.stdout=sys.stderr=log
 try:status=pytest.main([*sys.argv[2:],'-q','--capture=sys','-p','pytest_asyncio.plugin','-p','offline_fixtures','-p','no:cacheprovider','--basetemp',str(stage/('fixtures-'+label))])
 finally:sys.stdout,sys.stderr=oldout,olderr
result={'label':label,'exit':int(status),'seconds':time.monotonic()-start,'kernel_restrictions':policy,'candidate':str(repo)}
(stage/(label+'-result.json')).write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));print((stage/(label+'.txt')).read_text()[-4500:]);sys.exit(status)
