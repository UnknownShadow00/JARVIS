#!/usr/bin/env python3
"""Human-only read-only metadata report; does not run/provision qualification.

Run only on the independently identified disposable VM, after reviewed source
installation. No regular credential/cache file is opened, hashed or exported.
A BLOCKED result is never a passed security test. This report grants no authority.
"""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import json,os,pwd
from environment_probe import inspect_environment_paths
from safety_preflight import validate_environment

def report():
    try:
        account=pwd.getpwnam('jarvis')
        uid=account.pw_uid if account.pw_dir=='/home/jarvis' else None
    except KeyError:uid=None
    result=inspect_environment_paths(preparation_uid=uid)
    try:
        validate_environment(hostname=os.uname().nodename,
            interfaces=[p.name for p in Path('/sys/class/net').iterdir()],
            mountinfo=Path('/proc/self/mountinfo').read_text(),credential_paths=[],boot_source='/dev/sda2')
        result['vm163_mount_policy']='MATCHES_PROPOSED_BOOT_SOURCE; OPERATOR_APPROVAL_REQUIRED'
    except (RuntimeError,OSError) as e:
        result['vm163_mount_policy']=str(e) if isinstance(e,RuntimeError) else 'MOUNT_INSPECTION_UNAVAILABLE'
    result['required_artifact_root_present']=Path('/opt/g6k-offline').is_dir()
    result['approval_marker_present']=Path('/etc/g6k-disposable-approved.json').is_file()
    result['fixture_path_absent']=not (Path('/var/lib/g6j-disposable').exists() or Path('/var/lib/g6j-disposable').is_symlink())
    result['status']='INFORMATION_ONLY; QUALIFICATION_NOT_RUN'
    return result

if __name__=='__main__':
    print(json.dumps(report(),sort_keys=True,indent=2))
