"""Trusted PVE console only. Creates ONLY a new STOPPED VM164; never starts it.

Default is inspect-only. --create-stopped is the explicit allocation action.
No imports from downloaded packages. Preserve partial new allocations on failure.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess

VMID = 164
UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'g6k164-12821f6b54a2'
SIZE = 64 * 1024 ** 3


def run(argv):
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=120).stdout


def get(path, *args):
    return json.loads(run(['pvesh', 'get', path, *args, '--output-format', 'json']))


def check_storage(config, status, available, total):
    if config.get('type') != 'dir' or int(config.get('shared', 0)) or int(config.get('disable', 0)):
        raise RuntimeError('REVIEW_REQUIRED_DOWNLOADS_MUST_BE_ENABLED_LOCAL_DIRECTORY_STORAGE')
    if not int(status.get('active', 0)) or not int(status.get('enabled', 0)) or 'images' not in str(config.get('content', '')).split(','):
        raise RuntimeError('DOWNLOADS_NOT_ACTIVE_IMAGE_STORAGE')
    reserve = max(32 * 1024 ** 3, total // 10)
    if min(int(status.get('avail', 0)), available) < SIZE + reserve:
        raise RuntimeError('INSUFFICIENT_PHYSICAL_FREE_SPACE_PLUS_RESERVE')
    return reserve


def precheck():
    if os.geteuid() != 0 or socket.gethostname().split('.')[0] != 'pve':
        raise RuntimeError('WRONG_ROOT_NODE_CONSOLE')
    links = json.loads(run(['ip', '-j', '-4', 'address', 'show']))
    if not any(a.get('local') == '192.168.0.50' for link in links for a in link.get('addr_info', [])):
        raise RuntimeError('WRONG_MANAGEMENT_ADDRESS')
    resources = get('/cluster/resources', '--type', 'vm')
    if any(int(row.get('vmid', -1)) == VMID for row in resources):
        raise RuntimeError('VMID_ALREADY_IN_USE')
    if any(Path('/etc/pve/nodes').glob('*/qemu-server/164.conf')) or any(Path('/etc/pve/nodes').glob('*/lxc/164.conf')):
        raise RuntimeError('VMID_CONFIG_ALREADY_EXISTS')
    if int(get('/cluster/nextid', '--vmid', str(VMID))) != VMID:
        raise RuntimeError('VMID_NOT_CONFIRMED_FREE')
    node = get('/nodes/pve/status')
    if int(node['cpuinfo']['cpus']) < 4:
        raise RuntimeError('FOUR_HOST_CPUS_NOT_VERIFIED')
    config = get('/storage/downloads')
    status = get('/nodes/pve/storage/downloads/status')
    path = Path(config.get('path', ''))
    if not path.is_absolute() or not path.is_dir():
        raise RuntimeError('DOWNLOADS_PATH')
    mounts = json.loads(run(['findmnt', '-J', '-T', str(path), '-o', 'TARGET,SOURCE,FSTYPE,UUID']))['filesystems']
    if len(mounts) != 1 or mounts[0]['fstype'] not in ('ext4', 'xfs', 'btrfs'):
        raise RuntimeError('BACKEND_REVIEW_REQUIRED_NO_NETWORK_OR_UNREVIEWED_THIN_BACKEND')
    source = mounts[0]['source']
    if not source.startswith('/dev/') or '[' in source:
        raise RuntimeError('BACKING_DEVICE_REVIEW_REQUIRED')
    chain = json.loads(run(['lsblk', '-s', '-J', '-p', '-o', 'NAME,TYPE,TRAN', source]))['blockdevices']
    def inspect_chain(rows):
        for item in rows:
            if item.get('tran') in ('iscsi', 'fcoe') or str(item['name']).startswith(('/dev/nbd', '/dev/rbd')):
                raise RuntimeError('NONLOCAL_BACKING_DEVICE')
            if item.get('type') == 'lvm':
                segments = run(['lvs', '--noheadings', '-o', 'segtype', item['name']]).split()
                if not segments or any(segment not in ('linear', 'striped', 'raid1', 'raid10', 'raid5', 'raid6') for segment in segments):
                    raise RuntimeError('THIN_OR_UNREVIEWED_LVM_BACKEND')
            inspect_chain(item.get('children', []))
    inspect_chain(chain)
    fs = os.statvfs(path)
    reserve = check_storage(config, status, fs.f_bavail * fs.f_frsize, fs.f_blocks * fs.f_frsize)
    if get('/nodes/pve/storage/downloads/content', '--vmid', str(VMID)):
        raise RuntimeError('EXISTING_VM164_VOLUMES_PRESERVE_AND_REVIEW')
    iso = get('/nodes/pve/storage/local/status')
    iso_config = get('/storage/local')
    if not int(iso.get('active', 0)) or not int(iso.get('enabled', 0)) or int(iso_config.get('shared', 0)) or 'iso' not in str(iso_config.get('content', '')).split(',') or int(iso.get('avail', 0)) < 20 * 1024 ** 3:
        raise RuntimeError('LOCAL_ISO_CAPACITY_OR_CONTENT_NOT_VERIFIED')
    mem = {k.rstrip(':'): int(v.split()[0]) * 1024 for k, v in
           (line.split(maxsplit=1) for line in Path('/proc/meminfo').read_text().splitlines())}
    if mem['MemAvailable'] < 2 * 1024 ** 3:
        raise RuntimeError('HOST_TOO_LOW_FOR_MANAGEMENT_PREPARATION')
    return {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'candidate_vmid': VMID, 'planned_uuid': UUID, 'planned_serial': SERIAL,
            'downloads_path': str(path), 'downloads_mount': mounts[0],
            'physical_available_bytes': fs.f_bavail * fs.f_frsize, 'physical_reserve_bytes': reserve,
            'mem_available_bytes': mem['MemAvailable'], 'scope': 'CREATE_STOPPED_ONLY_NO_GUEST_RAM_COMMITTED'}


def create_command():
    return ['qm', 'create', str(VMID), '--name', 'jarvis-g6k-clean-164', '--ostype', 'l26',
            '--bios', 'seabios', '--machine', 'q35', '--cpu', 'host', '--sockets', '1', '--cores', '4',
            '--memory', '6000', '--balloon', '0', '--onboot', '0', '--start', '0', '--agent', '0',
            '--hotplug', '0', '--protection', '1', '--scsihw', 'virtio-scsi-single',
            '--scsi0', f'downloads:64,format=raw,serial={SERIAL},cache=none',
            '--ide2', 'none,media=cdrom', '--serial0', 'socket', '--vga', 'std', '--tablet', '0',
            '--smbios1', f'uuid={UUID}', '--boot', 'order=scsi0']


def validate_hardware(config):
    for key, value in (('cores', 4), ('sockets', 1), ('memory', 6000), ('balloon', 0), ('onboot', 0)):
        if int(config[key]) != value:
            raise RuntimeError('UNEXPECTED_HARDWARE_' + key)
    for key in config:
        if re.fullmatch(r'(net|hostpci|usb|virtiofs|sata|virtio|unused)\d+', key) or key in ('args', 'hookscript', 'cicustom', 'cipassword', 'sshkeys', 'ivshmem', 'efidisk0', 'tpmstate0'):
            raise RuntimeError('UNEXPECTED_DEVICE_OR_EXTERNAL_INPUT')
        if re.fullmatch(r'(scsi|ide)\d+', key) and key not in ('scsi0', 'ide2'):
            raise RuntimeError('EXTRA_DISK_OR_MEDIA')
    if config.get('smbios1') != 'uuid=' + UUID or config.get('ide2') != 'none,media=cdrom':
        raise RuntimeError('IDENTITY_OR_MEDIA')
    if config.get('bios') != 'seabios' or config.get('scsihw') != 'virtio-scsi-single' or config.get('serial0') != 'socket':
        raise RuntimeError('BOOT_OR_CONSOLE_CONFIG')
    if config.get('cpu') != 'host' or config.get('machine') != 'q35' or config.get('boot') != 'order=scsi0' or str(config.get('hotplug')) != '0' or int(config.get('protection', 0)) != 1:
        raise RuntimeError('CPU_MACHINE_BOOT_OR_PROTECTION')
    if str(config.get('agent', '0')).split(',')[0] not in ('0', 'enabled=0'):
        raise RuntimeError('GUEST_AGENT_ENABLED')
    disk = str(config['scsi0'])
    if not disk.startswith('downloads:') or f'serial={SERIAL}' not in disk.split(',') or 'size=64G' not in disk.split(','):
        raise RuntimeError('DISK_IDENTITY_OR_SIZE')
    volume = disk.split(',')[0]
    if not re.fullmatch(r'downloads:164/vm-164-disk-[0-9]+\.raw', volume):
        raise RuntimeError('VOLUME_MUST_BELONG_TO_NEW_VM164')
    return volume


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--create-stopped', action='store_true')
    args = parser.parse_args()
    before = precheck()
    print(json.dumps({'precheck': before, 'proposed_argv': create_command()}, indent=2), flush=True)
    if not args.create_stopped:
        print('INSPECT_ONLY; NOTHING_ALLOCATED')
        return
    record = Path('/root/g6k-vm164-create-r1')
    record.mkdir(mode=0o700)  # Exclusive record; reruns stop rather than retrying allocation.
    (record / 'precheck.json').write_text(json.dumps(before, indent=2) + '\n')
    final = precheck()  # Recheck immediately before the only VM allocation operation.
    (record / 'immediate-precheck.json').write_text(json.dumps(final, indent=2) + '\n')
    try:
        output = run(create_command())
        (record / 'qm-create.txt').write_text(output)
        config = get('/nodes/pve/qemu/164/config')
        (record / 'config.json').write_text(json.dumps(config, indent=2) + '\n')
        volume = validate_hardware(config)
        status = get('/nodes/pve/qemu/164/status/current')
        if status['status'] != 'stopped':
            raise RuntimeError('VM_NOT_STOPPED_DO_NOT_AUTO_SHUT_DOWN')
        path = Path(run(['pvesm', 'path', volume]).strip())
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_nlink != 1 or st.st_uid != 0 or st.st_mode & 0o022 or st.st_size != SIZE:
            raise RuntimeError('DEDICATED_RAW_FILE_VALIDATION')
        info = json.loads(run(['qemu-img', 'info', '-f', 'raw', '--output=json', str(path)]))
        if info.get('format') != 'raw' or info.get('virtual-size') != SIZE or 'backing-filename' in info:
            raise RuntimeError('DISK_FORMAT_OR_BACKING_FILE')
        result = {'status': 'CREATED_STOPPED_GUEST_NOT_INSTALLED', 'volume': volume,
                  'path': str(path), 'inode': st.st_ino, 'device': st.st_dev,
                  'logical_bytes': st.st_size, 'allocated_bytes': st.st_blocks * 512,
                  'vm_uuid': UUID, 'serial': SERIAL, 'network_devices': 0,
                  'ram': '6000 MiB configured, NOT proof of safe runtime capacity',
                  'qualification': 'NOT_RUN', 'boot': 'NOT_AUTHORIZED_BY_THIS_SCRIPT'}
        (record / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps(result, indent=2))
    except Exception as error:
        (record / 'FAILED-PRESERVE.txt').write_text(type(error).__name__ + ': ' + str(error) + '\n')
        raise


if __name__ == '__main__':
    main()
