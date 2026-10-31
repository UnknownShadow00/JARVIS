"""Linux x86_64 worker-only irreversible seccomp guard, after Python startup.

The worker needs inherited serial FDs, files and SQLite, never a new process,
socket or identity. Unsupported platforms/kernels refuse; no fallback path.
"""
import ctypes
import os

from .protocol import need


def undumpable():
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = (ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
    libc.prctl.restype = ctypes.c_int
    need(libc.prctl(4, 0, 0, 0, 0) == 0, 'PROCESS_DUMP_PROTECTION')


def install_worker_guard():
    need(os.geteuid() != 0 and os.uname().machine == 'x86_64', 'WORKER_GUARD_PLATFORM')
    undumpable()

    class Filter(ctypes.Structure):
        _fields_ = [('code', ctypes.c_ushort), ('jt', ctypes.c_ubyte),
                    ('jf', ctypes.c_ubyte), ('k', ctypes.c_uint32)]

    class Program(ctypes.Structure):
        _fields_ = [('length', ctypes.c_ushort), ('filters', ctypes.POINTER(Filter))]

    deny = 0x00050000 | 1  # SECCOMP_RET_ERRNO | EPERM
    instructions = [Filter(0x20, 0, 0, 4), Filter(0x15, 1, 0, 0xc000003e),
                    Filter(0x06, 0, 0, 0x80000000), Filter(0x20, 0, 0, 0),
                    Filter(0x35, 0, 1, 0x40000000), Filter(0x06, 0, 0, deny)]
    # x86_64 syscall numbers. Reject x32 above before applying this table.
    forbidden = (41, 42, 43, 44, 45, 46, 47, 49, 50, 53, 56, 57, 58, 59,
                 101, 105, 106, 113, 114, 116, 117, 119, 122, 123, 155,
                 165, 166, 169, 246, 248, 250, 272, 288, 298, 304, 308, 310,
                 311, 313, 321, 322, 323, 425, 426, 427, 435, 438, 442)
    for number in forbidden:
        instructions.extend((Filter(0x15, 0, 1, number), Filter(0x06, 0, 0, deny)))
    instructions.append(Filter(0x06, 0, 0, 0x7fff0000))
    array = (Filter * len(instructions))(*instructions)
    program = Program(len(instructions), array)
    libc = ctypes.CDLL(None, use_errno=True)
    libc.prctl.argtypes = (ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
    libc.prctl.restype = ctypes.c_int
    need(libc.prctl(38, 1, 0, 0, 0) == 0, 'NO_NEW_PRIVILEGES')
    need(libc.prctl(22, 2, ctypes.addressof(program), 0, 0) == 0, 'WORKER_SECCOMP')
