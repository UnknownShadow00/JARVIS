"""Read-only installer admission for the one virgin VM164 disk. No override modes."""
import json
import os
from pathlib import Path
import subprocess
import sys

VM_UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
HARDWARE_SERIAL = 'g6k164-12821f6b54a2'
DISK_PATH = '/dev/sda'
DISK_BYTES = 68_719_476_736
UDEV_SERIAL = '0QEMU_QEMU_HARDDISK_drive-scsi0'
UDEV_SHORT = 'drive-scsi0'
UDEV_PATH = 'pci-0000:09:01.0-scsi-0:0:0:0'
MATCH = {'path': DISK_PATH, 'serial': UDEV_SERIAL, 'id_path': UDEV_PATH}


def refuse(condition, code):
    if not condition:
        raise RuntimeError(code)


def flag(value):
    refuse(type(value) in (bool, int) and value in (0, 1), 'UNKNOWN_BLOCK_FLAG')
    return bool(value)


def flatten(devices):
    refuse(type(devices) is list, 'BLOCK_INVENTORY_TYPE')
    result = []
    def visit(rows, depth):
        refuse(depth <= 8 and len(result) < 256, 'BLOCK_INVENTORY_LIMIT')
        for row in rows:
            refuse(type(row) is dict, 'BLOCK_RECORD_TYPE')
            result.append(row)
            children = row.get('children', [])
            refuse(type(children) is list, 'BLOCK_CHILDREN_TYPE')
            visit(children, depth + 1)
    visit(devices, 0)
    names = [row.get('name') for row in result]
    refuse(all(type(name) is str and name.startswith('/dev/') and '/' not in name[5:]
               and name[5:] not in ('', '.', '..') for name in names), 'BLOCK_DEVICE_PATH')
    refuse(len(names) == len(set(names)), 'DUPLICATE_BLOCK_PATH')
    return result


def validate_identity(snapshot):
    refuse(snapshot['euid'] == 0, 'ROOT_REQUIRED')
    refuse(snapshot['uuid'].strip().lower() == VM_UUID, 'WRONG_VM_UUID')
    refuse(snapshot['interfaces'] == ['lo'], 'NETWORK_INTERFACE_PRESENT')
    rows = flatten(snapshot['blockdevices'])
    udev = snapshot['udev']
    refuse(type(udev) is dict and set(udev) == {row['name'] for row in rows}, 'INCOMPLETE_UDEV_INVENTORY')
    for path, props in udev.items():
        refuse(type(props) is dict and props.get('DEVNAME') == path, 'UDEV_DEVNAME_DISAGREEMENT')
    # Check uniqueness before selecting a path. A path restriction must not hide
    # a second device claiming the same observed udev identity.
    for key, expected in (('ID_SERIAL', UDEV_SERIAL), ('ID_SERIAL_SHORT', UDEV_SHORT), ('ID_PATH', UDEV_PATH)):
        owners = sorted(path for path, props in udev.items() if props.get(key) == expected)
        refuse(owners == [DISK_PATH], 'UDEV_IDENTITY_NOT_UNIQUE_' + key)
    disks = [row for row in rows if row.get('type') == 'disk']
    refuse(len(disks) == 1 and disks[0].get('name') == DISK_PATH, 'EXACTLY_ONE_EXPECTED_DISK_REQUIRED')
    disk = disks[0]
    refuse(disk.get('serial') == HARDWARE_SERIAL, 'WRONG_QEMU_HARDWARE_SERIAL')
    refuse(type(disk.get('size')) is int and disk['size'] == DISK_BYTES, 'WRONG_DISK_SIZE')
    refuse(type(disk.get('model')) is str and disk['model'].strip() == 'QEMU HARDDISK', 'WRONG_DISK_MODEL')
    refuse(not flag(disk.get('ro')) and not flag(disk.get('rm')), 'TARGET_NOT_FIXED_WRITABLE_DISK')
    refuse(not disk.get('children'), 'TARGET_HAS_PARTITIONS_OR_DEPENDENTS')
    mounts = disk.get('mountpoints')
    refuse(type(mounts) is list and all(m in (None, '') for m in mounts), 'TARGET_MOUNTED_OR_UNINSPECTABLE')
    for row in rows:
        if row is disk:
            continue
        refuse(row.get('type') in ('rom', 'loop') and flag(row.get('ro')), 'EXTRA_INSTALLATION_DEVICE_OR_WRITABLE_MEDIA')
    props = udev[DISK_PATH]
    refuse(props.get('DEVTYPE') == 'disk', 'UDEV_TARGET_NOT_DISK')
    for key, expected in (('ID_SERIAL', UDEV_SERIAL), ('ID_SERIAL_SHORT', UDEV_SHORT), ('ID_PATH', UDEV_PATH)):
        refuse(props.get(key) == expected, 'WRONG_UDEV_' + key)
    return {'disk': DISK_PATH, 'hardware_serial': HARDWARE_SERIAL, 'bytes': DISK_BYTES,
            'udev_serial': UDEV_SERIAL, 'udev_short': UDEV_SHORT, 'udev_path': UDEV_PATH,
            'subiquity_match': dict(MATCH)}


def validate_signatures(report):
    refuse(type(report) is dict and type(report.get('signatures')) is list and report['signatures'] == [],
           'DISK_SIGNATURES_PRESENT_OR_UNINSPECTABLE')


def validate(snapshot):
    result = validate_identity(snapshot)
    validate_signatures(snapshot['wipefs'])
    return result


def run(argv):
    return subprocess.run(argv, capture_output=True, text=True, check=True, timeout=30).stdout


def parse_udev(output):
    props = {}
    for line in output.splitlines():
        if not line:
            continue
        key, separator, value = line.partition('=')
        refuse(bool(separator) and bool(key) and key not in props, 'MALFORMED_OR_DUPLICATE_UDEV_PROPERTY')
        props[key] = value
    return props


def main():
    refuse(len(sys.argv) == 1, 'NO_ARGUMENTS_OR_OVERRIDES_ALLOWED')
    refuse(os.geteuid() == 0, 'ROOT_REQUIRED')
    uuid = Path('/sys/class/dmi/id/product_uuid').read_text().strip().lower()
    refuse(uuid == VM_UUID, 'WRONG_VM_UUID')  # Refuse before any device command.
    interfaces = sorted(p.name for p in Path('/sys/class/net').iterdir())
    refuse(interfaces == ['lo'], 'NETWORK_INTERFACE_PRESENT')
    run(['udevadm', 'settle', '--timeout=30'])  # Wait only; never trigger/rewrite devices.
    report = json.loads(run(['lsblk', '--json', '--bytes', '--paths', '--output',
                             'NAME,TYPE,SIZE,SERIAL,MODEL,RO,RM,MOUNTPOINTS']))
    rows = flatten(report['blockdevices'])
    udev = {row['name']: parse_udev(run(['udevadm', 'info', '--query=property', '--name', row['name']]))
            for row in rows}
    snapshot = {'euid': os.geteuid(), 'uuid': uuid, 'interfaces': interfaces,
                'blockdevices': report['blockdevices'], 'udev': udev}
    result = validate_identity(snapshot)  # Bind identity before examining signatures.
    signatures = json.loads(run(['wipefs', '--json', '--no-act', DISK_PATH]))
    validate_signatures(signatures)
    print(json.dumps({'status': 'READ_ONLY_VM164_DISK_GUARD_ACCEPTED', **result,
                      'signatures': [], 'formatting': 'NOT_PERFORMED_BY_GUARD',
                      'qualification': 'NOT_RUN'}, sort_keys=True))


if __name__ == '__main__':
    main()
