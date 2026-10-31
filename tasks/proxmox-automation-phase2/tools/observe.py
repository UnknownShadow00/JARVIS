#!/usr/bin/env python3
"""Reuse the installed observer; emit selected public metadata, never credentials.

No API method other than GET exists here. No guest-agent or console call exists.
Self-permissions queries inspect authorization, not other guests' contents.
Run explicitly; importing this file makes no connection.
"""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import re
import runpy
from datetime import datetime, timezone

CLIENT = Path('/home/nexus/.local/bin/g6k-pve164-readonly')
ALLOWED = frozenset({
    '/api2/json/version',
    '/api2/json/access/permissions',
    '/api2/json/nodes/pve/qemu/164/config',
    '/api2/json/nodes/pve/qemu/164/status/current',
})


def granted_names(grants):
    """PVE values are propagate flags; even a zero-valued entry is a grant."""
    return sorted(grants) if isinstance(grants, dict) else []


def main():
    # The installed client performs its original two GETs and loads the secret
    # internally. Suppress its stdout; never serialize its module namespace.
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        client = runpy.run_path(str(CLIENT))

    calls = []

    def get(path):
        if path not in ALLOWED:
            raise ValueError('ENDPOINT_NOT_ALLOWED')
        conn = client['PVEConnection']('pve', 8006, timeout=10)
        try:
            conn.request('GET', path, headers={
                'Authorization': 'PVEAPIToken=' + client['TOKEN_ID'] + '=' + client['secret'],
            })
            response = conn.getresponse()
            calls.append({'method': 'GET', 'path': path, 'status': response.status})
            # Do not log error bodies, headers, URLs containing tickets or exceptions.
            if response.status != 200:
                response.read(4096)
                return None
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise ValueError('OVERSIZE_RESPONSE')
            return json.loads(raw)['data']
        finally:
            conn.close()

    version = get('/api2/json/version')
    permissions = get('/api2/json/access/permissions')
    config = get('/api2/json/nodes/pve/qemu/164/config')
    status = get('/api2/json/nodes/pve/qemu/164/status/current')
    if not isinstance(config, dict) or not isinstance(status, dict):
        raise ValueError('OBSERVATION_UNAVAILABLE')
    expected_uuid = 'uuid=faeb1db8-0df9-482d-b3e4-f6ccc1602193'
    if config.get('smbios1') != expected_uuid:
        raise ValueError('WRONG_VM_IDENTITY')
    privilege_summary = {}
    unexpected_paths = []
    if isinstance(permissions, dict):
        for path, grants in permissions.items():
            # Only authorization names are retained. No other guest data queried.
            if isinstance(grants, dict):
                # The value is an inheritance/propagation flag, NOT allow/deny.
                # A present privilege with value zero is still granted here.
                active = granted_names(grants)
                if active:
                    if path in ('/', '/vms/164', '/vms/162', '/vms/163', '/nodes/pve'):
                        privilege_summary[path] = active
                    else:
                        unexpected_paths.append(path)
    selected = {k: config[k] for k in (
        'name', 'smbios1', 'scsi0', 'scsihw', 'bios', 'serial0', 'vga', 'agent',
        'boot', 'ide2', 'sata0', 'memory', 'cores', 'onboot', 'lock',
    ) if k in config}
    forbidden = sorted(k for k in config if
        (re.fullmatch(r'(net|hostpci|usb|virtiofs|unused|sata|virtio|efidisk|tpmstate|scsi|ide|serial)\d+', k)
         and k not in ('scsi0', 'ide2', 'serial0'))
        or k in ('args', 'hookscript', 'ivshmem', 'cicustom', 'cipassword', 'sshkeys'))
    result = {
        'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'installed_client_sha256': hashlib.sha256(CLIENT.read_bytes()).hexdigest(),
        'tls_verified': True, 'vmid': 164,
        'version': {k: version[k] for k in ('version', 'release', 'repoid') if k in version}
        if isinstance(version, dict) else None,
        'config': selected,
        'config_keys': sorted(config),
        'status': {k: status[k] for k in ('status', 'qmpstatus', 'uptime', 'agent') if k in status},
        'no_nic': not any(k.startswith('net') and k[3:].isdigit() for k in config),
        'unexpected_isolation_config_keys': forbidden,
        'self_permissions_available': isinstance(permissions, dict),
        'self_permissions_selected': privilege_summary,
        'self_permissions_other_active_paths': sorted(unexpected_paths),
        'api_calls': calls,
        'installed_observer_initial_get_count': 2,
        'guest_calls': 0, 'console_calls': 0, 'mutation_calls': 0,
        'limits': ['No guest boot/login/install attestation',
                   'Self-permissions are not live denied-call tests or a complete ACL audit'],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (Exception, SystemExit):
        print(json.dumps({'result': 'BLOCKED', 'detail': 'OBSERVATION_FAILED_NO_SECRET_DETAIL'}))
        raise SystemExit(1)
