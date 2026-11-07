import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


class HardeningTests(unittest.TestCase):
    def test_real_nonroot_child_kernel_guard_denies_exec_network_identity_and_fork(self):
        source = Path(__file__).resolve().parents[1] / 'src'
        code = '''import ctypes,errno,json,os,socket,sys
sys.path.insert(0,sys.argv[1])
from g6k_serial.hardening import install_worker_guard
install_worker_guard()
libc=ctypes.CDLL(None,use_errno=True)
checks={}
for name,number,args in [('execve',59,(b'/usr/bin/true',0,0)),('socket',41,(2,1,0)),
                         ('setuid',105,(0,)),('fork',57,()),('socketpair',53,(1,1,0,0)),
                         ('execveat',322,(-100,b'/usr/bin/true',0,0,0)),
                         ('io_uring_setup',425,(0,0))]:
 ctypes.set_errno(0)
 result=libc.syscall(number,*args)
 checks[name]=result==-1 and ctypes.get_errno()==errno.EPERM
status=open('/proc/self/status').read()
checks['no_new_privs']='NoNewPrivs:\\t1' in status
checks['seccomp_filter']='Seccomp:\\t2' in status
checks['undumpable']=libc.prctl(3,0,0,0,0)==0
print(json.dumps(checks))
sys.exit(0 if all(checks.values()) else 9)
'''
        result = subprocess.run([sys.executable, '-I', '-B', '-c', code, str(source)],
                                capture_output=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        checks = json.loads(result.stdout)
        self.assertTrue(all(checks.values()), checks)
        self.assertEqual(os.geteuid(), os.getuid())
        # Only the disposable child received seccomp; the test runner still runs.


if __name__ == '__main__':
    unittest.main()
