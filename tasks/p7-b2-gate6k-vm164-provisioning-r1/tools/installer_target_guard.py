"""Before-first-boot guard for NEW VM164 only. No credential file reads or cleanup."""
import json
import os
from pathlib import Path
import stat
import subprocess

UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'g6k164-12821f6b54a2'


def run(argv):
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=30).stdout.strip()


def main():
    if os.geteuid() != 0 or Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower() != UUID:
        raise RuntimeError('WRONG_VM')
    if {p.name for p in Path('/sys/class/net').iterdir()} != {'lo'}:
        raise RuntimeError('NIC_PRESENT')
    devices = json.loads(run(['lsblk', '-J', '-b', '-d', '-o', 'NAME,TYPE,SIZE,SERIAL']))['blockdevices']
    disks = [r for r in devices if r['type'] == 'disk']
    if len(disks) != 1 or disks[0]['name'] != 'sda' or disks[0]['serial'] != SERIAL or int(disks[0]['size']) != 64 * 1024 ** 3:
        raise RuntimeError('WRONG_DEDICATED_DISK')
    target = Path('/target')
    mount = json.loads(run(['findmnt', '-J', '-M', str(target), '-o', 'TARGET,SOURCE,FSTYPE']))['filesystems']
    if len(mount) != 1 or mount[0]['fstype'] != 'ext4' or not mount[0]['source'].startswith('/dev/sda'):
        raise RuntimeError('PRIVATE_EXT4_TARGET_REQUIRED')
    if run(['lsblk', '-n', '-o', 'PKNAME', mount[0]['source']]) != 'sda':
        raise RuntimeError('TARGET_PARENT_DISK')
    for relative in ('root/.ssh', 'home/jarvis/.ssh', 'etc/g6k-disposable-approved.json', 'var/lib/g6j-disposable'):
        path = target / relative
        if path.exists() or path.is_symlink():
            raise RuntimeError('UNEXPECTED_TARGET_PATH_' + relative.replace('/', '_'))
    sentinel = (target / 'etc/cloud/cloud-init.disabled').lstat()
    if not stat.S_ISREG(sentinel.st_mode) or sentinel.st_uid != 0 or sentinel.st_gid != 0 or sentinel.st_size or sentinel.st_nlink != 1 or stat.S_IMODE(sentinel.st_mode) != 0o644:
        raise RuntimeError('CLOUD_DISABLE_SENTINEL')
    # The installer may generate public seed inputs. Do not read, chmod or remove them.
    # Any subsequent failed unchanged r1 scan stops readiness; this is not that scan.
    names = ('g6j-operator', 'g6j-service', 'g6j-agent')
    prefix = ['curtin', 'in-target', '--target=/target', '--']
    for name in names:
        result = subprocess.run(prefix + ['getent', 'passwd', name], capture_output=True, timeout=30)
        if result.returncode != 2:
            raise RuntimeError('EXISTING_OR_UNINSPECTABLE_ROLE')
    for name in names:
        run(prefix + ['useradd', '--system', '--user-group', '--no-create-home', '--groups', '',
                      '--shell', '/usr/sbin/nologin', name])
    run(prefix + ['systemd-machine-id-setup'])
    machine_id = (target / 'etc/machine-id').read_text().strip()
    if len(machine_id) != 32 or any(c not in '0123456789abcdef' for c in machine_id):
        raise RuntimeError('MACHINE_ID')
    roles = [run(prefix + ['getent', 'passwd', name]).split(':') for name in names]
    if len({int(r[2]) for r in roles} | {0}) != 4 or len({int(r[3]) for r in roles} | {0}) != 4:
        raise RuntimeError('ROLE_IDENTITIES_NOT_DISTINCT')
    report = {'scope': 'INSTALLER_TARGET_PRE_FIRST_BOOT_ONLY', 'vm_uuid': UUID, 'disk_serial': SERIAL,
              'machine_id': machine_id, 'root_mount': mount[0],
              'roles': [{'name': r[0], 'uid': int(r[2]), 'gid': int(r[3]), 'shell': r[6]} for r in roles],
              'ssh_paths': 'ABSENT_AT_CHECK', 'cloud_init_disabled': True,
              'guest_boot_validation': 'NOT_RUN', 'qualification': 'NOT_RUN'}
    destination = target / 'var/log/g6k-install-origin.json'
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'w') as out:
        json.dump(report, out, indent=2)
        out.write('\n')
    print('INSTALLER_TARGET_GUARD_COMPLETE; GUEST_PREFLIGHT_AND_BOOT_REVIEW_REQUIRED')


if __name__ == '__main__':
    main()
