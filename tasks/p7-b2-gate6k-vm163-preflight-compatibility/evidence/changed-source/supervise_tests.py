"""Ephemeral test supervisor: only signal a verified direct disposable child via pidfd.

The sandbox still denies every signal syscall. This broker supports two canonical
writer-crash tests without granting the candidate a signal capability over JARVIS.
"""
import json,os,select,signal,subprocess,sys
from pathlib import Path
stage=Path(__file__).parent;label=sys.argv[1]
request_r,request_w=os.pipe();answer_r,answer_w=os.pipe()
env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','PYTHONPATH','PYTHONDONTWRITEBYTECODE','PYTEST_DISABLE_PLUGIN_AUTOLOAD','P7_OFFLINE_STAGE','TMPDIR','JARVIS_API_TOKEN')}
env.update(P7_TEST_REQUEST_FD=str(request_w),P7_TEST_ANSWER_FD=str(answer_r))
env['PYTHONPATH']=str(stage/'guard')+':'+str(stage/'repo')+':'+str(stage)
child=subprocess.Popen([sys.executable,str(stage/'run_tests.py'),*sys.argv[1:]],env=env,pass_fds=(request_w,answer_r))
os.close(request_w);os.close(answer_r);records=[];buffer=b''
try:
    while child.poll() is None:
        if not select.select([request_r],[],[],0.1)[0]:continue
        chunk=os.read(request_r,512)
        if not chunk:continue
        buffer+=chunk
        if len(buffer)>1024:raise RuntimeError('BROKER_PROTOCOL_SIZE')
        if b'\n' not in buffer:continue
        line,buffer=buffer.split(b'\n',1);result='REFUSED';pid=None;fd=None
        try:
            request=json.loads(line)
            if type(request) is not dict or set(request)!={'pid','signal'}:raise ValueError()
            pid=request['pid'];sig=request['signal']
            if type(pid) is not int or pid<=1 or sig not in (9,15):raise ValueError()
            fd=os.pidfd_open(pid) # Bind identity before inspecting; prevent PID-reuse signalling.
            status=dict(x.split(':',1) for x in (Path('/proc')/str(pid)/'status').read_text().splitlines() if ':' in x)
            if int(status['PPid'])!=child.pid or not all(int(x)==os.getuid() for x in status['Uid'].split()):raise ValueError()
            cwd=Path(os.readlink(Path('/proc')/str(pid)/'cwd')).resolve()
            if stage not in cwd.parents:raise ValueError()
            args=(Path('/proc')/str(pid)/'cmdline').read_bytes().split(b'\0')
            if args[0]!=os.fsencode(sys.executable) or args[1]!=b'-c':raise ValueError()
            # Never preserve the inline fixture program or request content in broker evidence.
            signal.pidfd_send_signal(fd,sig);result='DISPOSABLE_CHILD_SIGNALED'
        except (ValueError,OSError,KeyError,IndexError):pass
        finally:
            if fd is not None:os.close(fd)
        records.append({'target_pid':pid,'result':result,'verified_parent':child.pid})
        os.write(answer_w,(result+'\n').encode())
    rc=child.wait()
finally:
    os.close(request_r);os.close(answer_w)
    (stage/(label+'-broker.json')).write_text(json.dumps(records,indent=2)+'\n')
sys.exit(rc)
