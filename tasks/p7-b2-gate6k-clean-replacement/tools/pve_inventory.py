"""Run only at the trusted PVE root console. GET operations only; no VM mutation."""
import datetime
import json
import os
from pathlib import Path
import socket
import subprocess

PROTECTED = {50, 101, 162, 163, 200}


def get(path, *arguments):
    result = subprocess.run(['pvesh', 'get', path, *arguments, '--output-format', 'json'],
                            capture_output=True, text=True, check=True, timeout=30)
    return json.loads(result.stdout)


def pick(value, keys):
    return {key: value[key] for key in keys if key in value}


def candidate_id(resources):
    used = {int(row['vmid']) for row in resources if 'vmid' in row}
    return next(i for i in range(164, 1000000) if i not in used | PROTECTED)


def main():
    if os.geteuid() != 0 or socket.gethostname().split('.')[0] != 'pve':
        raise SystemExit('REFUSE: requires independently verified pve root console')
    addresses = subprocess.run(['ip', '-j', '-4', 'address', 'show'], capture_output=True,
                               text=True, check=True, timeout=10)
    if not any(a.get('local') == '192.168.0.50' for link in json.loads(addresses.stdout)
               for a in link.get('addr_info', [])):
        raise SystemExit('REFUSE: expected management address absent')
    resources = get('/cluster/resources', '--type', 'vm')
    candidate = candidate_id(resources)
    if int(get('/cluster/nextid', '--vmid', str(candidate))) != candidate:
        raise SystemExit('REFUSE: candidate availability not confirmed')
    status = get('/nodes/pve/status')
    storage = get('/nodes/pve/storage')
    meminfo = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree'):
            meminfo[key + '_bytes'] = int(value.split()[0]) * 1024
    print(json.dumps({
        'observed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'node': 'pve', 'management_address': '192.168.0.50', 'effective_uid': 0,
        'scope': 'GET_ONLY; NO_GUEST_ACCESS; NO_MUTATIONS',
        'vms': [pick(row, ('vmid', 'node', 'type', 'status', 'maxmem', 'maxcpu', 'maxdisk')) for row in resources],
        'candidate_vmid_available_at_observation_only': candidate,
        'node_memory': pick(status.get('memory', {}), ('total', 'used', 'free')),
        'node_cpu': pick(status.get('cpuinfo', {}), ('cpus', 'cores', 'sockets')),
        'node_load': status.get('loadavg'), 'meminfo': meminfo,
        'storage': [pick(row, ('storage', 'type', 'active', 'enabled', 'shared', 'content',
                              'total', 'used', 'avail')) for row in storage],
        'creation': 'NOT_RUN', 'qualification': 'NOT_RUN',
    }, indent=2))


if __name__ == '__main__':
    main()
