#!/bin/bash
(
set -eu
umask 077
python3 -I -B - <<'G6K_REVIEWED_PY'
"""PVE root-console read-only sampler. Never starts, stops or changes a VM."""
import datetime
import json
import os
from pathlib import Path
import socket
import subprocess
import time

GUEST = 6000 * 1024 ** 2
OVERHEAD = 1024 ** 3
RESERVE = 8 * 1024 ** 3
REQUIRED = GUEST + OVERHEAD + RESERVE


def kv(path):
    return {k.rstrip(':'): int(v.split()[0]) for k, v in
            (line.split(maxsplit=1) for line in Path(path).read_text().splitlines())}


def pressure(path):
    return {line.split()[0]: {k: float(v) for k, v in
            (item.split('=') for item in line.split()[1:])}
            for line in Path(path).read_text().splitlines()}


def assess(samples):
    first, last = samples[0], samples[-1]
    reasons = []
    if min(s['memory_bytes']['MemAvailable'] for s in samples) < REQUIRED:
        reasons.append('AVAILABLE_BELOW_GUEST_PLUS_1GIB_OVERHEAD_PLUS_8GIB_RESERVE')
    if len({s.get('boot_id') for s in samples}) != 1:
        reasons.append('HOST_BOOT_CHANGED_DURING_SAMPLE')
    if any(last['vmstat'][key] != first['vmstat'][key] for key in ('pswpin', 'pswpout', 'oom_kill')):
        reasons.append('SWAP_ACTIVITY_OR_OOM_DURING_SAMPLE')
    for metric in ('some', 'full'):
        if last['memory_psi'][metric]['total'] != first['memory_psi'][metric]['total']:
            reasons.append('MEMORY_PSI_STALLS_DURING_SAMPLE_' + metric.upper())
    return {'screen': 'NO_GO_START' if reasons else 'SCREEN_ONLY_PASSED_NOT_START_AUTHORIZATION',
            'reasons': reasons, 'required_available_bytes': REQUIRED,
            'policy': 'Conservative task-specific screen, not a Linux/Proxmox guarantee',
            'start': 'NOT_RUN; representative workload/commitments and operator review still required'}


def main():
    if os.geteuid() != 0 or socket.gethostname().split('.')[0] != 'pve':
        raise SystemExit('REFUSE_WRONG_CONSOLE')
    links = json.loads(subprocess.check_output(['ip', '-j', '-4', 'address', 'show']))
    if not any(a.get('local') == '192.168.0.50' for link in links for a in link.get('addr_info', [])):
        raise SystemExit('REFUSE_WRONG_ADDRESS')
    samples = []
    for index in range(7):
        if index:
            time.sleep(5)
        mem = kv('/proc/meminfo')
        vm = kv('/proc/vmstat')
        samples.append({'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'memory_bytes': {k: mem[k] * 1024 for k in ('MemTotal', 'MemAvailable', 'SwapTotal', 'SwapFree')},
            'vmstat': {k: vm[k] for k in ('pswpin', 'pswpout', 'oom_kill', 'pgmajfault')},
            'memory_psi': pressure('/proc/pressure/memory'), 'io_psi': pressure('/proc/pressure/io')})
    def get(path, *args):
        return json.loads(subprocess.check_output(['pvesh', 'get', path, *args, '--output-format', 'json']))
    resources = get('/cluster/resources', '--type', 'vm')
    running = [{k: r[k] for k in ('vmid', 'type', 'node', 'status', 'mem', 'maxmem') if k in r}
               for r in resources if r.get('node') == 'pve' and r.get('status') == 'running']
    config = get('/storage/downloads')
    print(json.dumps({'scope': 'READ_ONLY_30_SECOND_SAMPLE_NO_ALLOCATION',
                      'samples': samples, 'assessment': assess(samples), 'running_allocations': running,
                      'downloads_backend': {k: config[k] for k in ('type', 'path', 'shared', 'content', 'disable') if k in config},
                      'vmid164_still_available': get('/cluster/nextid', '--vmid', '164')}, indent=2))


if __name__ == '__main__':
    main()

G6K_REVIEWED_PY
)
