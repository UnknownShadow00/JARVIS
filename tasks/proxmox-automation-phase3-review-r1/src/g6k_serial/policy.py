"""Immutable target and catalog; operator grants only narrow that catalog."""
import hashlib
import re
import time

from .protocol import ACTIONS, DISK, DISK_SERIAL, TARGET, TOKEN_ID, exact_dict, hexid, integer, need, target

GRANT_KEYS = ('v', 'enabled', *TARGET, 'grant_id', 'operator_reference', 'expires_at',
              'machine_id', 'release', 'worker_uid', 'worker_gid', 'caller_uid', 'caller_gid', 'broker_uid', 'broker_gid',
              'actions', 'ca_sha256')
WORKER_KEYS = ('v', 'enabled', *TARGET, 'grant_id', 'expires_at', 'machine_id',
               'release', 'worker_uid', 'worker_gid', 'caller_uid')


def config(data, *, worker=False, now=None):
    exact_dict(data, WORKER_KEYS if worker else GRANT_KEYS)
    need(type(data['v']) is int and data['v'] == 1 and data['enabled'] is True, 'DISABLED')
    target(data)
    for key in ('grant_id', 'machine_id'):
        hexid(data[key])
    hexid(data['release'], 64)
    for key in ('worker_uid', 'worker_gid', 'caller_uid'):
        integer(data[key], 1)
    integer(data['expires_at'], 1, 2**53 - 1)
    need((time.time() if now is None else now) < data['expires_at'], 'GRANT_EXPIRED')
    if not worker:
        integer(data['broker_uid'], 1)
        integer(data['broker_gid'], 1)
        integer(data['caller_gid'], 1)
        need(data['broker_uid'] != data['caller_uid'], 'ROLE_UID')
        need(type(data['actions']) is list and 0 < len(data['actions']) <= len(ACTIONS) and
             all(type(a) is str and a in ACTIONS for a in data['actions']) and
             len(set(data['actions'])) == len(data['actions']), 'CATALOG')
        need(type(data['operator_reference']) is str and re.fullmatch(
            '[A-Za-z0-9][A-Za-z0-9._-]{0,95}', data['operator_reference']), 'OPERATOR_REFERENCE')
        hexid(data['ca_sha256'], 64)
    return data


def vm_state(snapshot):
    exact_dict(snapshot, ('config', 'status', 'pending', 'permissions'))
    c, s = snapshot['config'], snapshot['status']
    need(type(c) is dict and type(s) is dict, 'PVE_SCHEMA')
    need(c.get('smbios1') == 'uuid=' + TARGET['vm_uuid'], 'VM_UUID')
    need(c.get('serial0') == 'socket' and c.get('boot') == 'order=scsi0', 'VM_CHANNEL')
    need(str(c.get('agent', '0')) in ('0', 'enabled=0'), 'QGA_ENABLED')
    need(s.get('status') == 'running' and s.get('qmpstatus') == 'running', 'VM_STATE')
    integer(s.get('uptime'), 0, 2**53 - 1)
    need('lock' not in c, 'VM_LOCK')
    need(c.get('ide2', 'none,media=cdrom') == 'none,media=cdrom', 'MEDIA')
    disk = c.get('scsi0')
    need(type(disk) is str, 'DISK')
    parts = disk.split(',')
    need(len(parts) == 4 and parts[0] == DISK and set(parts[1:]) == {
        'cache=none', 'serial=' + DISK_SERIAL, 'size=64G'}, 'DISK')
    for key in c:
        need(key not in ('args', 'hookscript', 'ivshmem', 'cicustom', 'cipassword', 'sshkeys'), 'VM_EXTERNAL_INPUT')
        if re.fullmatch('(net|hostpci|usb|virtiofs|unused|sata|virtio|scsi|ide|serial|efidisk|tpmstate)\\d+', key):
            need(key in ('scsi0', 'ide2', 'serial0'), 'VM_EXTRA_DEVICE')
    need(type(snapshot['pending']) is list, 'PENDING_SCHEMA')
    for item in snapshot['pending']:
        need(type(item) is dict and not ('pending' in item or item.get('delete')), 'VM_PENDING')
    perms = snapshot['permissions']
    need(type(perms) is dict, 'PERMISSION_SCHEMA')
    # Values are propagation flags, not allow/deny flags. Zero is still a grant.
    active = {path: set(grants) for path, grants in perms.items() if type(grants) is dict and grants}
    need(active == {'/vms/164': {'VM.Audit', 'VM.Console'}}, 'PERMISSION_SCOPE')
    need(all(type(v) is dict for v in perms.values()), 'PERMISSION_SCHEMA')
    digest = c.get('digest')
    need(type(digest) is str and re.fullmatch('[0-9a-f]{40,64}', digest), 'CONFIG_DIGEST')
    return digest, s['uptime']


def token(data):
    exact_dict(data, ('id', 'secret'))
    need(data['id'] == TOKEN_ID and type(data['secret']) is str and
         re.fullmatch('[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data['secret']), 'CREDENTIAL_SCHEMA')
    return data
