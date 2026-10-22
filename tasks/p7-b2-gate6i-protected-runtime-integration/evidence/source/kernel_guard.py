"""Per-process Linux restrictions; no system configuration or privilege changes."""
import ctypes,errno,os
from pathlib import Path
def restrict(stage,venv):
 libc=ctypes.CDLL(None,use_errno=True);libc.syscall.restype=ctypes.c_long
 abi=libc.syscall(444,0,0,1)
 if abi<3:raise RuntimeError('LANDLOCK_REQUIRED')
 class Ruleset(ctypes.Structure):_fields_=[('handled_access_fs',ctypes.c_uint64)]
 class Beneath(ctypes.Structure):_pack_=1;_fields_=[('allowed_access',ctypes.c_uint64),('parent_fd',ctypes.c_int)]
 handled=(1<<15)-1;read=(1<<0)|(1<<2)|(1<<3)
 rules=Ruleset(handled);fd=libc.syscall(444,ctypes.byref(rules),ctypes.sizeof(rules),0)
 if fd<0:raise RuntimeError('LANDLOCK_CREATE')
 try:
  # READ_DIR alone allows no-follow directory walks, not file content access.
  for p,access in [(Path('/'),1<<3),(Path(stage),handled),(Path(venv),read),*( (Path(p),read) for p in ['/usr','/lib','/lib64','/bin','/etc','/dev/null','/dev/urandom','/dev/random',f'/proc/{os.getpid()}/stat','/proc/sys/kernel/random/boot_id'])]:
   if not p.exists():continue
   f=os.open(p,os.O_PATH|os.O_CLOEXEC)
   try:
    a=access if p.is_dir() else access&~(1<<3)
    if p==Path('/dev/null'):a=(1<<1)|(1<<2)
    rule=Beneath(a,f)
    if libc.syscall(445,fd,1,ctypes.byref(rule),0)<0:raise RuntimeError('LANDLOCK_RULE')
   finally:os.close(f)
  if libc.prctl(38,1,0,0,0):raise RuntimeError('NO_NEW_PRIVS')
  if libc.syscall(446,fd,0):raise RuntimeError('LANDLOCK_ENFORCE')
 finally:os.close(fd)
 sec=ctypes.CDLL('libseccomp.so.2');sec.seccomp_init.argtypes=[ctypes.c_uint32];sec.seccomp_init.restype=ctypes.c_void_p
 sec.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];sec.seccomp_syscall_resolve_name.restype=ctypes.c_int
 sec.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_int,ctypes.c_uint];sec.seccomp_rule_add.restype=ctypes.c_int
 sec.seccomp_load.argtypes=[ctypes.c_void_p];sec.seccomp_release.argtypes=[ctypes.c_void_p]
 ctx=sec.seccomp_init(0x7fff0000)
 class Compare(ctypes.Structure):_fields_=[('arg',ctypes.c_uint),('op',ctypes.c_int),('a',ctypes.c_uint64),('b',ctypes.c_uint64)]
 try:
  for name in ('ptrace','process_vm_readv','process_vm_writev','kill','tkill','tgkill','pidfd_send_signal','rt_sigqueueinfo','rt_tgsigqueueinfo','mount','umount2','reboot','bpf','io_uring_setup'):
   nr=sec.seccomp_syscall_resolve_name(name.encode())
   if nr>=0 and sec.seccomp_rule_add(ctx,0x50000|errno.EPERM,nr,0):raise RuntimeError('SECCOMP_RULE')
  for family in (1,):
   if sec.seccomp_rule_add(ctx,0x50000|errno.EPERM,sec.seccomp_syscall_resolve_name(b'socket'),1,Compare(0,1,family,0)):raise RuntimeError('SECCOMP_SOCKET')
  if sec.seccomp_load(ctx):raise RuntimeError('SECCOMP_LOAD')
 finally:sec.seccomp_release(ctx)
 return {'landlock_abi':abi,'filesystem':'candidate writable; system/venv read-only; home/production state denied','syscalls':'all non-AF_UNIX sockets, signals, ptrace, process-vm, mount, reboot, bpf/io_uring denied'}
