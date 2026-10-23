"""Run a local Python module after denying network socket creation in this process.

This is a Nexus same-UID fixture, not a VM or UID qualification. No host policy changes.
"""
import ctypes,errno,os,pathlib,runpy,socket,sys
def deny_network():
    libc=ctypes.CDLL(None,use_errno=True)
    if libc.prctl(38,1,0,0,0):raise RuntimeError('NO_NEW_PRIVS')
    sec=ctypes.CDLL('libseccomp.so.2')
    sec.seccomp_init.argtypes=[ctypes.c_uint32];sec.seccomp_init.restype=ctypes.c_void_p
    sec.seccomp_syscall_resolve_name.argtypes=[ctypes.c_char_p];sec.seccomp_syscall_resolve_name.restype=ctypes.c_int
    sec.seccomp_rule_add.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_int,ctypes.c_uint]
    sec.seccomp_load.argtypes=[ctypes.c_void_p];sec.seccomp_release.argtypes=[ctypes.c_void_p]
    class Compare(ctypes.Structure):_fields_=[('arg',ctypes.c_uint),('op',ctypes.c_int),('a',ctypes.c_uint64),('b',ctypes.c_uint64)]
    ctx=sec.seccomp_init(0x7fff0000)
    if not ctx:raise RuntimeError('SECCOMP_INIT')
    try:
        for syscall in (b'socket',b'socketpair'):
            number=sec.seccomp_syscall_resolve_name(syscall)
            if number<0 or sec.seccomp_rule_add(ctx,0x50000|errno.EPERM,number,1,Compare(0,1,1,0)):raise RuntimeError('SECCOMP_RULE')
        if sec.seccomp_load(ctx):raise RuntimeError('SECCOMP_LOAD')
    finally:sec.seccomp_release(ctx)
    for family in (socket.AF_INET,socket.AF_INET6,socket.AF_PACKET):
        try:s=socket.socket(family,socket.SOCK_DGRAM)
        except PermissionError:continue
        else:s.close();raise RuntimeError('NETWORK_DENIAL_FAILED')
def main():
    # New child has no inherited sockets; fail if caller supplied any non-stdio FD.
    for fd in range(3,1024):
        try:os.close(fd)
        except OSError:pass
    deny_network()
    base=pathlib.Path(__file__).resolve().parents[1]
    if sys.argv[1]=='pip':
        sys.path.insert(0,str(next((base/'artifacts/wheels').glob('pip-*.whl'))))
        sys.argv=['pip','--isolated','--disable-pip-version-check','--no-cache-dir',*sys.argv[2:]]
        runpy.run_module('pip',run_name='__main__')
    elif sys.argv[1]=='sigstore':
        sys.argv=sys.argv[1:];runpy.run_module('sigstore',run_name='__main__')
    else:raise ValueError('unsupported offline operation')
if __name__=='__main__':main()
