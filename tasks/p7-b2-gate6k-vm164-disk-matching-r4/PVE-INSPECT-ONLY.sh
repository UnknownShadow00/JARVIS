#!/bin/bash
# FUTURE OPERATOR PROCEDURE ONLY; not authorized by current ISO-engineering GO.
(
set -eu
umask 077
python3 -I -B - --mode inspect <<'G6K_R4_CONSOLE_PY'
"""FUTURE OPERATOR HANDOFF ONLY. Default read-only; never powers off/starts a VM.

Current user authorization covers ISO engineering only. Do not execute on PVE
until separately authorized after failed-installer evidence retention.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
import time

UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'g6k164-12821f6b54a2'
OLD_ISO = 'local:iso/ubuntu-26.04.1-g6k-vm164-r3.iso,media=cdrom'
NEW_VOLUME = 'local:iso/ubuntu-26.04.1-g6k-vm164-r4.iso'
NEW_SHA = '050875e2f3ffd5a7711bb2f520bce98404416d2117faedf2ba608831e2a416f3'
MEMORY_BUDGET = (6000 + 1024 + 8192) * 1024 ** 2


def require(value, message):
    if not value:
        raise RuntimeError(message)


def run(argv):
    return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=120).stdout


def get(path):
    return json.loads(run(['pvesh', 'get', path, '--output-format', 'json']))


def validate_config(config):
    require(config.get('smbios1') == 'uuid=' + UUID, 'WRONG_VM_UUID')
    for key, value in (('cores', 4), ('sockets', 1), ('memory', 6000), ('balloon', 0), ('onboot', 0)):
        require(int(config.get(key, -1)) == value, 'HARDWARE_' + key)
    require(config.get('bios') == 'seabios' and config.get('scsihw') == 'virtio-scsi-single'
            and config.get('machine') == 'q35', 'HARDWARE_TOPOLOGY_CHANGED')
    require(str(config.get('agent', '0')).split(',')[0] in ('0', 'enabled=0'), 'GUEST_AGENT_ENABLED')
    for key in config:
        require(not re.fullmatch(r'(net|hostpci|usb|virtiofs|virtio|sata|unused|efidisk|tpmstate)\d+', key)
                and key not in ('args', 'hookscript', 'ivshmem', 'cicustom', 'cipassword', 'sshkeys'), 'EXTERNAL_INPUT_PRESENT')
        require(not re.fullmatch(r'(ide|scsi)\d+', key) or key in ('ide2', 'scsi0'), 'ADDITIONAL_DISK')
    parts = config.get('scsi0', '').split(',')
    require(bool(re.fullmatch(r'downloads:164/vm-164-disk-[0-9]+\.raw', parts[0])), 'DISK_VOLUME_NOT_REVIEWED_RAW_VM164_VOLUME')
    require('serial=' + SERIAL in parts and 'size=64G' in parts, 'WRONG_DISK_SERIAL_OR_SIZE')
    return parts[0]


def kv(path):
    return {k.rstrip(':'): int(v.split()[0]) for k, v in
            (line.split(maxsplit=1) for line in Path(path).read_text().splitlines())}


def memory_sample():
    pressure = {}
    for line in Path('/proc/pressure/memory').read_text().splitlines():
        values = dict(item.split('=') for item in line.split()[1:])
        pressure[line.split()[0]] = int(values['total'])
    vm = kv('/proc/vmstat')
    return {'available': kv('/proc/meminfo')['MemAvailable'] * 1024,
            'counters': {k: vm[k] for k in ('pswpin', 'pswpout', 'oom_kill')}, 'psi': pressure,
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=('inspect', 'replace-media', 'prestart'), default='inspect')
    mode = parser.parse_args().mode
    require(os.geteuid() == 0 and socket.gethostname().split('.')[0] == 'pve', 'WRONG_ROOT_NODE_CONSOLE')
    links = json.loads(run(['ip', '-j', '-4', 'address', 'show']))
    require(any(a.get('local') == '192.168.0.50' for link in links for a in link.get('addr_info', [])), 'WRONG_NODE_ADDRESS')
    config = get('/nodes/pve/qemu/164/config')
    volume = validate_config(config)
    status = get('/nodes/pve/qemu/164/status/current')['status']
    disk = Path(run(['pvesm', 'path', volume]).strip())
    st = disk.lstat()
    require(stat.S_ISREG(st.st_mode) and st.st_uid == 0 and st.st_nlink == 1
            and st.st_size == 68_719_476_736 and not st.st_mode & 0o022, 'RAW_DISK_FILE_IDENTITY')
    iso = Path(run(['pvesm', 'path', NEW_VOLUME]).strip())
    ist = iso.lstat()
    require(stat.S_ISREG(ist.st_mode) and ist.st_uid == 0 and ist.st_nlink == 1 and not ist.st_mode & 0o022,
            'R4_ISO_NOT_PROTECTED_REGULAR_FILE')
    with iso.open('rb') as stream:
        require(hashlib.file_digest(stream, 'sha256').hexdigest() == NEW_SHA, 'R4_ISO_HASH_MISMATCH')
    public = {'vmid': 164, 'uuid': UUID, 'volume': volume, 'disk_path': str(disk), 'inode': st.st_ino,
              'device': st.st_dev, 'logical_bytes': st.st_size, 'status': status,
              'media': config.get('ide2'), 'r4_sha256': NEW_SHA, 'mode': mode}
    print(json.dumps(public, indent=2), flush=True)
    if mode == 'inspect':
        print('READ_ONLY_INSPECTION_ONLY; NO_LIFECYCLE_OR_DISK_WRITE')
        return
    require(status == 'stopped', 'VM_MUST_BE_STOPPED_AFTER_APPROVED_EVIDENCE_PRESERVATION; NO_AUTO_STOP')
    signatures = json.loads(run(['wipefs', '--json', '--no-act', str(disk)]))
    require(type(signatures) is dict and signatures.get('signatures') == [], 'DISK_INITIALIZED_OR_UNINSPECTABLE_PRESERVE_AND_STOP')
    if mode == 'replace-media':
        require(config.get('ide2') == OLD_ISO, 'EXPECTED_RETAINED_R3_MEDIA_NOT_ATTACHED')
        require(get('/nodes/pve/qemu/164/status/current')['status'] == 'stopped', 'VM_STATUS_CHANGED')
        run(['qm', 'set', '164', '--digest', config['digest'], '--ide2', NEW_VOLUME + ',media=cdrom',
             '--boot', 'order=ide2;scsi0'])
        after = get('/nodes/pve/qemu/164/config')
        validate_config(after)
        require(after.get('ide2') == NEW_VOLUME + ',media=cdrom' and after.get('boot') == 'order=ide2;scsi0', 'POST_MEDIA_BINDING')
        require(get('/nodes/pve/qemu/164/status/current')['status'] == 'stopped', 'VM_UNEXPECTEDLY_RUNNING')
        print('R4_MEDIA_ATTACHED_VM164_STOPPED; NO_DISK_WRITE_OR_START')
        return
    require(config.get('ide2') == NEW_VOLUME + ',media=cdrom' and config.get('boot') == 'order=ide2;scsi0', 'R4_BOOT_BINDING_MISSING')
    first = memory_sample()
    samples = [first]
    for _ in range(6):
        time.sleep(5)
        samples.append(memory_sample())
    require(min(s['available'] for s in samples) >= MEMORY_BUDGET, 'INSUFFICIENT_PHYSICAL_MEMORY_HEADROOM')
    require(all(s['boot_id'] == first['boot_id'] and s['counters'] == first['counters']
                and s['psi'] == first['psi'] for s in samples), 'SWAP_OOM_PRESSURE_OR_BOOT_CHANGED')
    require(get('/nodes/pve/qemu/164/status/current')['status'] == 'stopped', 'VM_STATUS_CHANGED')
    require(get('/nodes/pve/qemu/164/config')['digest'] == config['digest'], 'CONFIG_CHANGED')
    print('PRESTART_CHECK_ONLY; NO_START_PERFORMED; REPRESENTATIVE_PEAK_AND_EXTERNAL_AUTHORIZATION_REVIEW_STILL_REQUIRED')


if __name__ == '__main__':
    main()

G6K_R4_CONSOLE_PY
)
