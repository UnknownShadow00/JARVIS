"""Offline policy reference, not an installed broker or execution authority.

No sockets, processes, guest access, credential reads or filesystem writes.
Callers supply synthetic records. Production grants require protected storage,
peer credentials, durable reservation, identity and transport qualification.
"""
from dataclasses import dataclass
import json
import re

VM_UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
DISK = 'downloads:164/vm-164-disk-0.raw'
SERIAL = 'g6k164-12821f6b54a2'
MAX_FRAME = 1024
ACTIONS = frozenset(('identity', 'kernel', 'isolation-summary'))
_HEX = re.compile(r'[0-9a-f]{64}')
_MACHINE = re.compile(r'[0-9a-f]{32}')
_REQUEST = re.compile(r'[0-9a-f]{32}')


class Refusal(ValueError):
    """Only constant public error codes; never echo request contents."""


def require(condition, code):
    if not condition:
        raise Refusal(code)


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def decode_request(raw):
    require(type(raw) is bytes and 0 < len(raw) <= MAX_FRAME, 'FRAME_SIZE_OR_TYPE')
    # Frame payload excludes its LF delimiter; terminal control bytes never pass.
    require(all(32 <= b <= 126 for b in raw), 'NON_PRINTABLE_FRAME')
    try:
        data = json.loads(raw.decode('ascii'), object_pairs_hook=_pairs,
                          parse_constant=lambda _: (_ for _ in ()).throw(Refusal('NON_JSON_CONSTANT')))
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise Refusal('INVALID_JSON') from None
    require(type(data) is dict and set(data) == {'v', 'vmid', 'action', 'request_id'}, 'REQUEST_SCHEMA')
    require(type(data['v']) is int and data['v'] == 1, 'VERSION')
    require(type(data['vmid']) is int and data['vmid'] == 164, 'TARGET')
    require(type(data['action']) is str and data['action'] in ACTIONS, 'ACTION')
    require(type(data['request_id']) is str and _REQUEST.fullmatch(data['request_id']), 'REQUEST_ID')
    return data


@dataclass(frozen=True)
class StandingGrant:
    """Synthetic test input; constructing this is NOT operator approval."""
    operator_reference: str
    expires_at: int
    machine_id: str
    bundle_sha256: str
    actions: frozenset
    caller_uid: int


def validate_vm_config(config, status):
    require(type(config) is dict and type(status) is dict, 'STATE_SCHEMA')
    require(config.get('smbios1') == 'uuid=' + VM_UUID, 'VM_UUID')
    require(status.get('status') == 'running' and status.get('qmpstatus') == 'running', 'VM_STATE')
    require('lock' not in config and not config.get('pending'), 'VM_LOCK_OR_PENDING')
    require(config.get('serial0') == 'socket' and config.get('boot') == 'order=scsi0', 'SERIAL_OR_BOOT')
    require(str(config.get('agent', '0')) in ('0', 'enabled=0'), 'QGA_ENABLED')
    require(config.get('ide2', 'none,media=cdrom') == 'none,media=cdrom', 'ATTACHED_MEDIA')
    for key in config:
        if key in ('args', 'hookscript', 'ivshmem', 'cicustom', 'cipassword', 'sshkeys'):
            raise Refusal('EXTERNAL_INPUT')
        if re.fullmatch(r'(net|hostpci|usb|virtiofs|unused|sata|virtio|efidisk|tpmstate|ide|serial)\d+', key):
            require(key in ('ide2', 'serial0'), 'EXTRA_DEVICE')
        if re.fullmatch(r'scsi\d+', key):
            require(key == 'scsi0', 'EXTRA_DISK')
    disk = config.get('scsi0')
    require(type(disk) is str, 'DISK')
    parts = disk.split(',')
    require(parts[0] == DISK and len(parts) == 4 and set(parts[1:]) == {
        'cache=none', 'serial=' + SERIAL, 'size=64G'}, 'DISK')


def plan(raw, grant, *, peer_uid, now, config, status, guest, consumed_ids):
    request = decode_request(raw)
    require(type(grant) is StandingGrant, 'NO_STANDING_GRANT')
    require(type(now) is int and type(grant.expires_at) is int and now < grant.expires_at, 'EXPIRED_GRANT')
    require(type(grant.operator_reference) is str and bool(grant.operator_reference.strip()), 'OPERATOR_REFERENCE')
    require(type(grant.caller_uid) is int and grant.caller_uid > 0 and
            type(peer_uid) is int and peer_uid == grant.caller_uid, 'PEER_UID')
    require(type(grant.machine_id) is str and _MACHINE.fullmatch(grant.machine_id), 'MACHINE_BINDING')
    require(type(grant.bundle_sha256) is str and _HEX.fullmatch(grant.bundle_sha256), 'BUNDLE_BINDING')
    require(type(grant.actions) is frozenset and grant.actions <= ACTIONS and
            request['action'] in grant.actions, 'GRANT_ACTION')
    require(type(consumed_ids) is frozenset and request['request_id'] not in consumed_ids, 'REPLAY')
    validate_vm_config(config, status)
    require(type(guest) is dict and set(guest) == {
        'vm_uuid', 'machine_id', 'bundle_sha256', 'boot_id', 'interfaces',
        'euid', 'role_separation_verified'}, 'GUEST_SCHEMA')
    require(guest['vm_uuid'] == VM_UUID and guest['machine_id'] == grant.machine_id and
            guest['bundle_sha256'] == grant.bundle_sha256, 'GUEST_BINDING')
    require(type(guest['euid']) is int and guest['euid'] > 0 and
            guest['role_separation_verified'] is True, 'GUEST_PRIVILEGE')
    require(guest['interfaces'] == ['lo'], 'GUEST_NETWORK')
    require(type(guest['boot_id']) is str and re.fullmatch(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', guest['boot_id']), 'BOOT_BINDING')
    return {'result': 'VALID_PLAN_ONLY', 'transport_enabled': False, 'executed': False,
            'vmid': 164, 'action': request['action'], 'request_id': request['request_id']}
