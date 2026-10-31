"""Non-root inspection-only worker. No subprocess, shell, exec, network or keys."""
import os
from pathlib import Path
import secrets

from .policy import config
from .protocol import (ACTIONS, TARGET, Refusal, Deadline, bootid, decode, encode, exact_dict,
                       hexid, need, public_metadata, validate_binding, validate_report)


def bounded_file(path, maximum):
    with open(path, 'rb', buffering=0) as stream:
        raw = bytearray()
        while len(raw) <= maximum:
            chunk = stream.read(maximum + 1 - len(raw))
            if not chunk:
                break
            raw.extend(chunk)
    need(len(raw) <= maximum, 'INSPECTION_SIZE')
    return bytes(raw)


class Inspector:
    def __init__(self, settings):
        self.settings = settings

    def metadata(self):
        need(os.geteuid() == self.settings['worker_uid'] and os.geteuid() != 0, 'WORKER_UID')
        machine = bounded_file('/etc/machine-id', 64).decode('ascii').strip()
        hexid(machine)
        need(machine == self.settings['machine_id'], 'MACHINE_ID')
        boot = bounded_file('/proc/sys/kernel/random/boot_id', 64).decode('ascii').strip()
        bootid(boot)
        interfaces = os.listdir('/sys/class/net')
        need(interfaces == ['lo'], 'GUEST_NETWORK')
        cmdline = bounded_file('/proc/cmdline', 16384).decode('ascii')
        need(not any(part.startswith('console=ttyS0') or part.startswith('earlycon') or
                     part.startswith('kgdboc=') for part in cmdline.split()), 'KERNEL_SERIAL_CONSOLE')
        return {**TARGET, 'machine_id': machine, 'boot_id': boot,
                'release': self.settings['release'], 'worker_uid': os.geteuid()}

    def inspect(self, action, metadata):
        if action == 'identity':
            return metadata
        if action == 'kernel':
            return {'kernel_release': os.uname().release}
        need(action == 'isolation-summary', 'ACTION')
        lines = bounded_file('/proc/self/mountinfo', 1024 * 1024).splitlines()
        need(0 < len(lines) <= 4096, 'MOUNT_COUNT')
        shared = external = 0
        for line in lines:
            before, separator, after = line.partition(b' - ')
            need(separator and len(before.split()) >= 6 and len(after.split()) >= 3, 'MOUNTINFO')
            shared += any(item.startswith(b'shared:') for item in before.split()[6:])
            external += after.split()[0] in (b'9p', b'virtiofs', b'nfs', b'nfs4', b'cifs', b'smb3', b'fuse.sshfs')
        return {'loopback_only': True, 'interface_count': 1, 'mount_count': len(lines),
                'shared_mount_count': shared, 'external_fs_count': external, 'scope': 'worker-mount-namespace'}


class Worker:
    def __init__(self, settings, ledger, inspector, revalidate=lambda: None):
        self.settings = settings
        self.ledger = ledger
        self.inspector = inspector
        self.revalidate = revalidate
        self.session = None
        self.metadata = None

    def advertisement(self):
        config(self.settings, worker=True)
        self.revalidate()
        self.ledger.available()
        self.metadata = public_metadata(self.inspector.metadata())
        self.session = secrets.token_hex(16)
        return {'v': 1, 'type': 'ready', 'metadata': self.metadata, 'session': self.session}

    def process(self, data):
        exact_dict(data, ('v', 'type', 'binding', 'action'))
        need(type(data['v']) is int and data['v'] == 1 and data['type'] == 'inspect', 'PROTOCOL')
        need(type(data['action']) is str and data['action'] in ACTIONS, 'ACTION')
        context = data['binding']
        validate_binding(context)
        need(self.session is not None, 'NO_SESSION')
        expected = {**self.metadata, 'session': self.session, 'caller_uid': self.settings['caller_uid'],
                    'grant_id': self.settings['grant_id'], 'request_id': context['request_id'],
                    'challenge': context['challenge']}
        need(context == expected, 'WORKER_BINDING')
        # A session is consumed before any action; no retry on a malformed response.
        self.session = None
        with self.ledger.operation():
            config(self.settings, worker=True)
            self.revalidate()
            need(self.inspector.metadata() == self.metadata, 'WORKER_IDENTITY_DRIFT')
            self.ledger.reserve(context['request_id'], data['action'], context['caller_uid'])
            try:
                report = self.inspector.inspect(data['action'], self.metadata)
                validate_report(data['action'], report, self.metadata)
                need(self.inspector.metadata() == self.metadata, 'WORKER_IDENTITY_DRIFT')
                self.revalidate()
                reply = {'v': 1, 'type': 'report', 'binding': context, 'action': data['action'], 'report': report}
                encode(reply)
                self.ledger.finish(context['request_id'], 'REPORTED', report)
                return reply
            except BaseException:
                try:
                    self.ledger.finish(context['request_id'], 'UNKNOWN')
                except Exception:
                    pass  # Durable RESERVED also halts; never clear failed evidence.
                raise Refusal('WORKER_HALTED') from None
