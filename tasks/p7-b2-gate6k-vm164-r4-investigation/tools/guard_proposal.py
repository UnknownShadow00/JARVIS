"""Pure admission predicates for review; NOT an installer or a live collector.

No device access, subprocesses, write authorization, markers or override mode.
The sysfs/mount/loop-origin records are synthetic contract inputs. A production
collector and pre-boot write barrier remain unimplemented and unqualified.
"""
import re

VM_UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
HARDWARE_SERIAL = 'g6k164-12821f6b54a2'
DISK_BYTES = 68_719_476_736
DISK_PATH = '/dev/sda'
IDENTITIES = {
    'ID_SERIAL': '0QEMU_QEMU_HARDDISK_drive-scsi0',
    'ID_SERIAL_SHORT': 'drive-scsi0',
    'ID_PATH': 'pci-0000:09:01.0-scsi-0:0:0:0',
}


def require(ok, code):
    if not ok:
        raise RuntimeError(code)


def block_flag(value):
    require(type(value) in (bool, int) and value in (0, 1), 'UNKNOWN_BLOCK_FLAG')
    return bool(value)


def records(snapshot):
    require(type(snapshot) is dict, 'SNAPSHOT_TYPE')
    roots = snapshot.get('blockdevices')
    require(type(roots) is list and bool(roots), 'BLOCK_INVENTORY_TYPE')
    result = []
    names = set()
    def visit(rows, parent, depth):
        require(depth <= 8, 'TOPOLOGY_DEPTH')
        for row in rows:
            require(type(row) is dict and len(result) < 256, 'BLOCK_RECORD_OR_LIMIT')
            path = row.get('name')
            require(type(path) is str and re.fullmatch(r'/dev/[A-Za-z0-9_.-]+', path)
                    and path[5:] not in ('.', '..'), 'DEVICE_PATH')
            require(path not in names, 'DUPLICATE_PATH')
            names.add(path)
            result.append((row, parent))
            children = row.get('children', [])
            require(type(children) is list, 'CHILDREN_TYPE')
            visit(children, path, depth + 1)
    visit(roots, None, 0)
    return result


def validate_identity(snapshot):
    require(type(snapshot) is dict, 'SNAPSHOT_TYPE')
    require(type(snapshot.get('euid')) is int and snapshot['euid'] == 0, 'ROOT_REQUIRED')
    uuid = snapshot.get('uuid')
    require(type(uuid) is str and uuid.strip().lower() == VM_UUID, 'WRONG_VM_UUID')
    require(snapshot.get('interfaces') == ['lo'], 'NETWORK_INTERFACE_PRESENT')
    rows = records(snapshot)
    paths = {row['name'] for row, _ in rows}
    udev, sysfs = snapshot.get('udev'), snapshot.get('sysfs')
    require(type(udev) is dict and set(udev) == paths, 'INCOMPLETE_UDEV')
    require(type(sysfs) is dict and set(sysfs) == paths, 'INCOMPLETE_SYSFS')
    bypath = {row['name']: row for row, _ in rows}
    devnums = set()
    partitions = []
    nonpartitions = []
    for row, parent in rows:
        path = row['name']
        props, kernel = udev[path], sysfs[path]
        require(type(props) is dict and props.get('DEVNAME') == path, 'UDEV_DISAGREEMENT')
        require(type(kernel) is dict, 'SYSFS_RECORD')
        dev = row.get('dev')
        require(type(dev) is str and re.fullmatch(r'[0-9]+:[0-9]+', dev)
                and kernel.get('dev') == dev, 'DEVNUM_DISAGREEMENT')
        require(dev not in devnums, 'DUPLICATE_DEVNUM')
        devnums.add(dev)
        require(kernel.get('holders') == [] and kernel.get('slaves') == [], 'UNSAFE_STORAGE_GRAPH')
        require(type(row.get('mountpoints')) is list, 'UNKNOWN_MOUNTS')
        block_flag(row.get('ro')); block_flag(row.get('rm'))
        kind = row.get('type')
        require(kind in ('disk', 'part', 'rom', 'loop'), 'UNSAFE_DEVICE_TYPE')
        require(kernel.get('kind') == kind, 'KERNEL_KIND_DISAGREEMENT')
        if kind == 'part':
            require(props.get('DEVTYPE') == 'partition', 'PARTITION_DEVTYPE')
            require(parent is not None and parent == row.get('pkname') == kernel.get('parent')
                    and bypath[parent].get('type') == 'disk', 'PARTITION_PARENT')
            require(type(kernel.get('partition')) is int and kernel['partition'] > 0,
                    'PARTITION_NUMBER')
            require(not row.get('children'), 'PARTITION_DEPENDENTS')
            partitions.append(path)
        else:
            require(parent is None and row.get('pkname') is None
                    and 'parent' in kernel and kernel['parent'] is None
                    and 'partition' in kernel and kernel['partition'] is None,
                    'WHOLE_DEVICE_TOPOLOGY')
            require(props.get('DEVTYPE') == 'disk', 'WHOLE_DEVICE_DEVTYPE')
            nonpartitions.append(path)
            if kind in ('rom', 'loop'):
                require(block_flag(row['ro']) and not row.get('children'), 'WRITABLE_MEDIA')
                if kind == 'loop':
                    require(kernel.get('backing_origin') == 'verified-install-media-or-ram',
                            'UNSAFE_LOOP_BACKING')
    # Count every whole-disk candidate BEFORE matching a preferred path/serial.
    # Any unsupported type was refused above, never filtered away silently.
    disks = [r for r, _ in rows if r['type'] == 'disk']
    require(len(disks) == 1 and disks[0]['name'] == DISK_PATH,
            'EXACTLY_ONE_EXPECTED_DISK_REQUIRED')
    disk = disks[0]
    require(disk.get('serial') == HARDWARE_SERIAL, 'WRONG_HARDWARE_SERIAL')
    require(type(disk.get('size')) is int and disk['size'] == DISK_BYTES, 'WRONG_SIZE')
    require(type(disk.get('model')) is str and disk['model'].strip() == 'QEMU HARDDISK',
            'WRONG_MODEL')
    require(not block_flag(disk['ro']) and not block_flag(disk['rm']), 'TARGET_NOT_FIXED_WRITABLE')
    for key, expected in IDENTITIES.items():
        require(udev[DISK_PATH].get(key) == expected, 'WRONG_UDEV_' + key)
        # Partition identity inheritance is legal only after parent proof.
        owners = [path for path in nonpartitions if udev[path].get(key) == expected]
        require(owners == [DISK_PATH], 'IDENTITY_NOT_UNIQUE_' + key)
    for key in ('mounts', 'swaps'):
        usage = snapshot.get(key)
        require(type(usage) is list and all(type(x) is str and re.fullmatch(r'[0-9]+:[0-9]+', x)
                                          for x in usage), 'INCOMPLETE_USAGE_' + key)
        target_devs = {bypath[p]['dev'] for p in [DISK_PATH] + partitions}
        require(not (target_devs & set(usage)), 'TARGET_IN_USE_' + key)
    for path in [DISK_PATH] + partitions:
        require(all(m in (None, '') for m in bypath[path]['mountpoints']), 'TARGET_MOUNTED')
    return {'disk': DISK_PATH, 'partitions': partitions,
            'hardware_serial': HARDWARE_SERIAL, 'bytes': DISK_BYTES}


def validate(snapshot):
    identity = validate_identity(snapshot)
    require(not identity['partitions'], 'TARGET_HAS_PARTITIONS')
    disk = next(r for r in snapshot['blockdevices'] if r['name'] == DISK_PATH)
    require('fstype' in disk and 'pttype' in disk and disk['fstype'] in (None, '')
            and disk['pttype'] in (None, ''), 'TARGET_INITIALIZED_OR_UNKNOWN')
    report = snapshot.get('wipefs')
    require(type(report) is dict and report.get('signatures') == []
            and type(report.get('signatures')) is list, 'SIGNATURES_PRESENT_OR_UNKNOWN')
    return {**identity, 'status': 'SYNTHETIC_PREDICATES_ACCEPTED_NOT_WRITE_AUTHORIZATION'}
