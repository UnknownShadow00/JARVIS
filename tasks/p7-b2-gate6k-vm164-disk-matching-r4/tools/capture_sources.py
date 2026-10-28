"""Extract exact public matching source, r3 config and retained late guard."""
import ast
import datetime
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import R3, R3_SHA, SNAP_SHA, TASK, extract_iso_file, require_hash, snap_source


def main():
    require_hash(R3, R3_SHA)
    directory = TASK / 'evidence/pinned-source'
    directory.mkdir(mode=0o700)
    rows = []
    for label, path in (
        ('filesystem-model.py', 'lib/python3.12/site-packages/subiquity/models/filesystem.py'),
        ('filesystem-controller.py', 'lib/python3.12/site-packages/subiquity/server/controllers/filesystem.py'),
    ):
        data = snap_source(path)
        with (directory / label).open('xb') as out:
            out.write(data)
        rows.append({'snap_path': path, 'retained_path': 'evidence/pinned-source/' + label,
                     'sha256': hashlib.sha256(data).hexdigest()})
    for name, path in (('autoinstall-r3.yaml', '/autoinstall.yaml'),
                       ('g6k-firstboot-guard.py', '/g6k-firstboot-guard.py'),
                       ('md5sum-r3.txt', '/md5sum.txt')):
        data = extract_iso_file(R3, path)
        with (TASK / 'evidence' / name).open('xb') as out:
            out.write(data)
        rows.append({'iso_path': path, 'retained_path': 'evidence/' + name,
                     'sha256': hashlib.sha256(data).hexdigest()})
    observation = {
        'recorded_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'source': 'USER_REPORTED_ACTUAL_VM164_INSTALLER_CONSOLE; NOT_AGENT_REMOTE_OBSERVATION',
        'observed_utc': None,
        'error': "Failed to find matching device for {'serial': 'g6k164-12821f6b54a2'}",
        'vm_uuid': 'faeb1db8-0df9-482d-b3e4-f6ccc1602193',
        'disk_path': '/dev/sda', 'bytes': 68_719_476_736, 'model': 'QEMU HARDDISK',
        'lsblk_serial': 'g6k164-12821f6b54a2',
        'ID_SERIAL': '0QEMU_QEMU_HARDDISK_drive-scsi0',
        'ID_SERIAL_SHORT': 'drive-scsi0', 'ID_PATH': 'pci-0000:09:01.0-scsi-0:0:0:0',
        'wipefs_no_act': 'NO_SIGNATURES_REPORTED', 'installation': 'NOT_COMPLETED',
        'raw_installer_logs_retained_by_agent': False,
        'preservation': 'No VM access/lifecycle or virtual disk operation by this task; external retention before retry still required',
    }
    (TASK / 'evidence/operator-failure-observation.json').write_text(json.dumps(observation, indent=2) + '\n')
    (TASK / 'evidence/input-source-record.json').write_text(json.dumps(
        {'r3_sha256': R3_SHA, 'subiquity_snap_sha256': SNAP_SHA, 'files': rows}, indent=2) + '\n')
    print(json.dumps({'status': 'PINNED_LOCAL_INPUTS_CAPTURED', 'source_files': len(rows)}))


if __name__ == '__main__':
    main()
