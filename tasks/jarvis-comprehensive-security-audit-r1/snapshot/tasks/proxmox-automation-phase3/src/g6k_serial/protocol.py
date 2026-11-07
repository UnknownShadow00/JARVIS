"""Small ASCII-only, duplicate-rejecting protocol; no executable payloads."""
import json
import re
import time

VMID = 164
UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'serial0'
DISK = 'downloads:164/vm-164-disk-0.raw'
DISK_SERIAL = 'g6k164-12821f6b54a2'
TOKEN_ID = 'g6k-bridge164@pve!serial'
ACTIONS = ('identity', 'kernel', 'isolation-summary')
TARGET = {'vmid': VMID, 'vm_uuid': UUID, 'serial': SERIAL}
REQUEST_BYTES = 1024
FRAME_BYTES = 16384
WALL_SECONDS = 5


class Refusal(Exception):
    """Constant codes only. Never attach untrusted values or nested exceptions."""


def need(condition, code='INVALID'):
    if not condition:
        raise Refusal(code)


def exact_dict(value, keys):
    need(type(value) is dict and set(value) == set(keys), 'SCHEMA')


def integer(value, low=0, high=2**31 - 1):
    need(type(value) is int and low <= value <= high, 'INTEGER')
    return value


def hexid(value, size=32):
    need(type(value) is str and re.fullmatch('[0-9a-f]{' + str(size) + '}', value), 'HEX_ID')
    return value


def bootid(value):
    need(type(value) is str and re.fullmatch(
        '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', value), 'BOOT_ID')
    return value


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'DUPLICATE_KEY')
        result[key] = value
    return result


def document(raw, limit=FRAME_BYTES):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'FRAME_SIZE')
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(Refusal('JSON_CONSTANT')))
    except (ValueError, RecursionError):
        raise Refusal('JSON') from None
    need(type(value) is dict, 'SCHEMA')
    return value


def decode(raw, limit=FRAME_BYTES):
    need(type(raw) is bytes and all(32 <= b < 127 for b in raw), 'FRAME_ENCODING')
    return document(raw, limit)


def encode(value, limit=FRAME_BYTES):
    raw = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
    need(len(raw) <= limit, 'FRAME_SIZE')
    return raw + b'\n'


def target(value):
    need(type(value.get('vmid')) is int and value['vmid'] == VMID and
         value.get('vm_uuid') == UUID and value.get('serial') == SERIAL, 'TARGET')


def public_request(raw):
    data = decode(raw, REQUEST_BYTES)
    exact_dict(data, ('v', 'vmid', 'vm_uuid', 'serial', 'action', 'request_id'))
    need(type(data['v']) is int and data['v'] == 1, 'VERSION')
    target(data)
    need(type(data['action']) is str and data['action'] in ACTIONS, 'ACTION')
    hexid(data['request_id'])
    return data


def public_metadata(value):
    exact_dict(value, (*TARGET, 'machine_id', 'boot_id', 'release', 'worker_uid'))
    target(value)
    hexid(value['machine_id'])
    bootid(value['boot_id'])
    hexid(value['release'], 64)
    integer(value['worker_uid'], 1)
    return value


def ready(value, grant):
    exact_dict(value, ('v', 'type', 'metadata', 'session'))
    need(type(value['v']) is int and value['v'] == 1 and value['type'] == 'ready', 'PROTOCOL')
    meta = public_metadata(value['metadata'])
    need(meta['machine_id'] == grant['machine_id'] and meta['release'] == grant['release'] and
         meta['worker_uid'] == grant['worker_uid'], 'GUEST_IDENTITY')
    hexid(value['session'])
    return value


def binding(request, advertisement, grant, caller_uid, challenge):
    return {**advertisement['metadata'], 'session': advertisement['session'],
            'request_id': request['request_id'], 'caller_uid': caller_uid,
            'grant_id': grant['grant_id'], 'challenge': challenge}


def validate_binding(value):
    exact_dict(value, (*TARGET, 'machine_id', 'boot_id', 'release', 'worker_uid',
                       'session', 'request_id', 'caller_uid', 'grant_id', 'challenge'))
    public_metadata({k: value[k] for k in (*TARGET, 'machine_id', 'boot_id', 'release', 'worker_uid')})
    integer(value['caller_uid'], 1)
    for key in ('session', 'request_id', 'grant_id', 'challenge'):
        hexid(value[key])


def validate_report(action, report, metadata):
    if action == 'identity':
        public_metadata(report)
        need(report == metadata, 'REPORT_IDENTITY')
    elif action == 'kernel':
        exact_dict(report, ('kernel_release',))
        value = report['kernel_release']
        need(type(value) is str and re.fullmatch('[A-Za-z0-9][A-Za-z0-9._+~-]{0,127}', value), 'KERNEL_REPORT')
    elif action == 'isolation-summary':
        exact_dict(report, ('loopback_only', 'interface_count', 'mount_count',
                            'shared_mount_count', 'external_fs_count', 'scope'))
        need(report['loopback_only'] is True and report['interface_count'] == 1 and
             type(report['interface_count']) is int, 'NETWORK_REPORT')
        for key in ('mount_count', 'shared_mount_count', 'external_fs_count'):
            integer(report[key], 0, 4096)
        need(report['scope'] == 'worker-mount-namespace' and report['external_fs_count'] == 0,
             'MOUNT_REPORT')
        need(report['shared_mount_count'] <= report['mount_count'], 'MOUNT_REPORT')
    else:
        raise Refusal('ACTION')
    return report


def response(value, context, action):
    exact_dict(value, ('v', 'type', 'binding', 'action', 'report'))
    need(type(value['v']) is int and value['v'] == 1 and value['type'] == 'report', 'PROTOCOL')
    validate_binding(value['binding'])
    need(value['binding'] == context and value['action'] == action, 'RESPONSE_BINDING')
    meta = {k: context[k] for k in (*TARGET, 'machine_id', 'boot_id', 'release', 'worker_uid')}
    return validate_report(action, value['report'], meta)


class Deadline:
    def __init__(self, seconds=WALL_SECONDS):
        self.end = time.monotonic() + seconds

    def remaining(self):
        remaining = self.end - time.monotonic()
        need(remaining > 0, 'TIMEOUT')
        return remaining


class Lines:
    """Bound both accumulated input and each line, across transport fragments."""
    def __init__(self, recv, limit=FRAME_BYTES, budget=65536):
        self.recv = recv
        self.limit = limit
        self.budget = budget
        self.buffer = b''

    def raw_line(self, deadline):
        while b'\n' not in self.buffer:
            need(len(self.buffer) <= self.limit, 'FRAME_SIZE')
            chunk = self.recv(deadline)
            need(type(chunk) is bytes and 0 < len(chunk) <= self.budget, 'CHANNEL')
            self.budget -= len(chunk)
            self.buffer += chunk
        raw, self.buffer = self.buffer.split(b'\n', 1)
        need(0 < len(raw) <= self.limit and len(self.buffer) <= self.budget + self.limit, 'FRAME_SIZE')
        return raw

    def line(self, deadline):
        return decode(self.raw_line(deadline), self.limit)
