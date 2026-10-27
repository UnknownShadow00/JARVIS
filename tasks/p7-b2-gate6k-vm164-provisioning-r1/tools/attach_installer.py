"""PVE root console: verify/uploaded r3 ISO and attach only to the recorded STOPPED VM164."""
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess

UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'g6k164-12821f6b54a2'
ISO_VOLUME = 'local:iso/ubuntu-26.04.1-g6k-vm164-r3.iso'
ISO_SHA = '4161509164bcaff08506ad2ffcd52a6782eb34eb4b08d47f1bb8754016a07346'


def run(argv):
    return subprocess.run(argv, check=True, capture_output=True, text=True, timeout=120).stdout


def get(path):
    return json.loads(run(['pvesh', 'get', path, '--output-format', 'json']))


def main():
    if os.geteuid() != 0 or socket.gethostname().split('.')[0] != 'pve':
        raise RuntimeError('WRONG_CONSOLE')
    links = json.loads(run(['ip', '-j', '-4', 'address', 'show']))
    if not any(a.get('local') == '192.168.0.50' for row in links for a in row.get('addr_info', [])):
        raise RuntimeError('WRONG_NODE_ADDRESS')
    record = Path('/root/g6k-vm164-create-r1')
    original = json.loads((record / 'result.json').read_text())
    if not re.fullmatch(r'downloads:164/vm-164-disk-[0-9]+\.raw', original['volume']):
        raise RuntimeError('VOLUME_NOT_OWNED_BY_NEW_VM164')
    config = get('/nodes/pve/qemu/164/config')
    if config.get('smbios1') != 'uuid=' + UUID or config['scsi0'].split(',')[0] != original['volume'] or f'serial={SERIAL}' not in config['scsi0'].split(','):
        raise RuntimeError('WRONG_NEW_VM_OR_DISK')
    if config.get('ide2') != 'none,media=cdrom' or int(config.get('onboot', 1)) != 0 or int(config.get('memory', 0)) != 6000 or int(config.get('balloon', -1)) != 0:
        raise RuntimeError('UNEXPECTED_MEDIA_OR_AUTOSTART')
    if config.get('bios') != 'seabios' or str(config.get('agent', '0')).split(',')[0] not in ('0', 'enabled=0'):
        raise RuntimeError('UNEXPECTED_BOOT_OR_GUEST_AGENT')
    if any(re.fullmatch(r'(net|hostpci|usb|virtiofs|unused|sata|virtio|efidisk|tpmstate)\d+', k) or k in ('args', 'hookscript', 'ivshmem', 'cicustom', 'sshkeys', 'cipassword') for k in config):
        raise RuntimeError('UNEXPECTED_EXTERNAL_INPUT')
    if any(re.fullmatch(r'(ide|scsi)\d+', k) and k not in ('ide2', 'scsi0') for k in config):
        raise RuntimeError('EXTRA_DISK')
    path = Path(run(['pvesm', 'path', original['volume']]).strip())
    st = path.lstat()
    if not stat.S_ISREG(st.st_mode) or st.st_ino != original['inode'] or st.st_dev != original['device'] or st.st_size != 64 * 1024 ** 3:
        raise RuntimeError('DISK_FILE_CHANGED')
    signatures = json.loads(run(['wipefs', '--json', '--no-act', str(path)]))
    if signatures.get('signatures') != []:
        raise RuntimeError('DISK_ALREADY_INITIALIZED_PRESERVE_AND_REVIEW')
    iso = Path(run(['pvesm', 'path', ISO_VOLUME]).strip())
    iso_stat = iso.lstat()
    if not stat.S_ISREG(iso_stat.st_mode) or iso_stat.st_uid != 0 or iso_stat.st_mode & 0o022 or iso_stat.st_nlink != 1:
        raise RuntimeError('ISO_NOT_PROTECTED_REGULAR_FILE')
    with iso.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != ISO_SHA:
            raise RuntimeError('ISO_HASH_MISMATCH')
    if get('/nodes/pve/qemu/164/status/current')['status'] != 'stopped':
        raise RuntimeError('VM_MUST_STAY_STOPPED')
    log = record / 'media-attachment.json'
    fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    # File is reserved before mutation; preserve it on failure. Never retry blindly.
    with os.fdopen(fd, 'w') as out:
        run(['qm', 'set', '164', '--digest', config['digest'], '--ide2', ISO_VOLUME + ',media=cdrom',
             '--boot', 'order=ide2;scsi0'])
        after = get('/nodes/pve/qemu/164/config')
        if after.get('ide2') != ISO_VOLUME + ',media=cdrom' or get('/nodes/pve/qemu/164/status/current')['status'] != 'stopped':
            raise RuntimeError('POST_ATTACH_VALIDATION')
        json.dump({'status': 'INSTALLER_ATTACHED_VM_STOPPED', 'iso_volume': ISO_VOLUME, 'sha256': ISO_SHA,
                   'vm_uuid': UUID, 'serial': SERIAL, 'start': 'NOT_RUN; MEMORY_GATE_REMAINS'}, out, indent=2)
        out.write('\n')
    print('INSTALLER_ATTACHED_TO_VERIFIED_VM164; NO_START_OR_QUALIFICATION')


if __name__ == '__main__':
    main()
