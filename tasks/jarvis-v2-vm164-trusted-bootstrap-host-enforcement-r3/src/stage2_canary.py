"""Standalone future Stage2 NON-ROOT/NON-VM clock callback.

No subprocess, network, VM, systemd, private authorization-file or filesystem-write
interface. Host root must separately approve/configure the timer. Callback runs
as a verified EXISTING unprivileged UID; this script rejects UID/eUID0. The only
public copy allowed later is the hash-pinned root-owned path below. Default dry.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import time
PUBLIC_PATH='/opt/jarvis-vm164-r3-stage2/canary.py'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--approved-nonvm-callback',action='store_true')
    p.add_argument('--expected-source-sha256');p.add_argument('--mode',choices=['success','failure'],default='success')
    a=p.parse_args()
    if not a.approved_nonvm_callback:
        print(json.dumps({'status':'DRY_RUN_NON_ROOT_NON_VM_NO_ACTION','root_boot_go':False}));return 0
    if os.getuid()==0 or os.geteuid()==0:raise ValueError('stage2_callback_must_not_be_root')
    path=Path(__file__).absolute()
    if str(path)!=PUBLIC_PATH:raise ValueError('reviewed_public_callback_path_required')
    for item in (Path('/'),*reversed(path.parents[:-1]),path):
        s=item.lstat()
        if stat.S_ISLNK(s.st_mode) or s.st_uid!=0 or s.st_mode&0o022:raise ValueError('root_owned_readonly_callback_required')
    leaf=path.lstat()
    if not stat.S_ISREG(leaf.st_mode) or leaf.st_nlink!=1 or leaf.st_size>16384:raise ValueError('bounded_regular_callback_required')
    raw=path.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=a.expected_source_sha256:raise ValueError('callback_source_pin')
    print(json.dumps({'status':'NON_ROOT_NON_VM_CLOCK_CANARY','uid':os.getuid(),'euid':os.geteuid(),
        'boottime_us':time.clock_gettime_ns(time.CLOCK_BOOTTIME)//1000,
        'monotonic_us':time.clock_gettime_ns(time.CLOCK_MONOTONIC)//1000,
        'host_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
        'vm_operations':False,'root_boot_go':False,'requested_mode':a.mode}),flush=True)
    return 0 if a.mode=='success' else 7
if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,OSError) as exc:
        print(json.dumps({'status':'STAGE2_CALLBACK_REFUSED','reason':str(exc) if isinstance(exc,ValueError)
                          else type(exc).__name__,'vm_operations':False}));raise SystemExit(1)
