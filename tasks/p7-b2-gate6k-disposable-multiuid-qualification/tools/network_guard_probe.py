"""Disposable child only: exercise unprivileged per-process restrictions."""
import subprocess,sys,json
from pathlib import Path
candidate=Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2/disposable')
script=f'''import sys,os,json,socket,ctypes
sys.path.insert(0,{str(candidate)!r})
from qualify_multi_uid import network_guard
uid=os.getuid();network_guard();checks={{}}
for family in (socket.AF_INET,socket.AF_INET6,socket.AF_PACKET):
 try:
  value=socket.socket(family,socket.SOCK_STREAM);value.close();checks[str(family)]=False
 except PermissionError:checks[str(family)]=True
left,right=socket.socketpair(socket.AF_UNIX);left.close();right.close()
libc=ctypes.CDLL(None)
result=dict(uid=uid,unchanged_uid=os.getuid()==uid,no_new_privs=libc.prctl(39,0,0,0,0)==1,blocked_families=checks,unix_pair=True)
print(json.dumps(result));sys.exit(0 if all(checks.values()) and result['no_new_privs'] and result['unchanged_uid'] else 1)
'''
result=subprocess.run([sys.executable,'-B','-c',script],capture_output=True,text=True,timeout=10,check=True)
path=Path(__file__).resolve().parent.parent/'evidence/kernel-runner-probe.json'
path.write_text(result.stdout);print(result.stdout)
