#!/usr/bin/python3
"""Nonsecret PRE-probe checks only. Never imports or executes the auth utility."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

R = Path('/home/jarvis/JARVIS')
G = Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate4-v2-supervised-startup')
B = Path('/home/jarvis/.hermes-poc/backups/p7-b2/9315a199492449709dfd6bd51b2666a5')


def require(condition):
    if not condition:
        raise ValueError('PREFLIGHT_REFUSED')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    require(len(sys.argv) == 1)
    def guard(event, args):
        if event.startswith('socket.'):
            raise RuntimeError('NETWORK_FORBIDDEN')
        if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
            path = Path(os.fsdecode(args[0])).absolute()
            if Path('/home/jarvis/.config/jarvis') in path.parents:
                raise RuntimeError('CREDENTIAL_OPEN_FORBIDDEN')
            if (args[2] or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
                raise RuntimeError('WRITE_FORBIDDEN')
    sys.addaudithook(guard)
    expected = {'ActiveState': 'active', 'SubState': 'running', 'MainPID': '594042',
                'InvocationID': '103e420f4f334237a96654048a3edaf4', 'NRestarts': '0',
                'Restart': 'no', 'UMask': '0077', 'UnitFileState': 'disabled',
                'NeedDaemonReload': 'no', 'WorkingDirectory': str(R),
                'FragmentPath': '/home/jarvis/.config/systemd/user/jarvis.service',
                'DropInPaths': '/home/jarvis/.config/systemd/user/jarvis.service.d/p7-b2.conf'}
    result = subprocess.run(['systemctl', '--user', 'show', 'jarvis.service',
                             *[v for k in expected for v in ('-p', k)]],
                            capture_output=True, text=True, timeout=5, check=True)
    require(dict(line.split('=', 1) for line in result.stdout.splitlines()) == expected)
    require(sha(Path(expected['FragmentPath'])) ==
            '134e60634b7fb9fae7848f3423e6bb20e89458075fdb06cf602269050219639d')
    require(sha(Path(expected['DropInPaths'])) ==
            '0a126c10d05d446bb1da0635a042a44fe00a7ee8aa4cda5cd008959bfaea3244')
    head = subprocess.run(['git', '-C', str(R), 'rev-parse', 'HEAD'],
                          capture_output=True, text=True, timeout=5, check=True).stdout.strip()
    require(head == 'bd53dbc799fb9284a21fae8cce3f5d9539e31141')
    require(sha(R / 'config.yaml') == '00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c')
    inventory = G / 'installed-source-sha256.json'
    require(sha(inventory) == 'c2be606074bed90a0e22fa198cf64d704bb51b78e7f486e6c82bdb246752e6c7')
    for name, digest in json.loads(inventory.read_text()).items():
        require(name.startswith('app/') and '..' not in Path(name).parts)
        require(sha(R / name) == digest)
    dbpath = R / 'data/p7-b2-pilot-controller-v1/controller.sqlite3'
    with sqlite3.connect(dbpath.as_uri() + '?mode=ro', uri=True, timeout=2) as db:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        require(db.execute('PRAGMA quick_check').fetchall() == [('ok',)])
        require(db.execute('PRAGMA user_version').fetchone() == (3,))
        require(db.execute('SELECT id,status,input_complete FROM epochs').fetchall() ==
                [('606a991a06b74fd79ed72b308417cc3f', 'OPEN', 1)])
        resource = json.dumps(('ollama', 'http://192.168.0.200:11434',
                               'hermes-candidate-granite41-30b-q3km-64k'))
        require(db.execute('SELECT purpose,resource,profile,accepted_limit FROM pilot_context').fetchall() ==
                [('PILOT', resource, 'jarvis.p7.ollama.granite41.b1r2.v1', 4)])
        for table in ('attempts', 'attempt_events', 'submissions', 'receipt_joins',
                      'resource_resolutions', 'collector_facts', 'receipt_resolutions',
                      'pilot_events', 'pilot_refusals'):
            require(db.execute('SELECT count(*) FROM ' + table).fetchone() == (0,))
    require(not (R / 'data/p7-shadow-evidence-v1').exists())
    require(sha(B / 'manifest.json') == 'e6847c5043b28da9c6e7a3f1d18869bcfe5529c2fcc3867fe53fa00474527f64')
    manifest = json.loads((B / 'manifest.json').read_text())
    for name, digest in manifest['files'].items():
        require(Path(name).name == name and sha(B / name) == digest)
    for live, backup in [('state.json', 'state.json'), ('scope.json', 'scope.json')]:
        require(sha(R / 'data/model-ownership-v1' / live) == manifest['files'][backup])
    require(sha(R / 'data/model-ownership-v1.managed') == manifest['files']['ownership.managed'])
    require(json.loads((R / 'data/model-ownership-v1/state.json').read_text()) ==
            {'version': 1, 'current': None, 'last': None})
    print('PREFLIGHT=PASS PID=594042 INVOCATION=UNCHANGED RESTARTS=0')
    print('ADMISSION=CLOSED_SOURCE_BOUND EPOCH=606a991a06b74fd79ed72b308417cc3f')
    print('AUTH_ABORT_RECORDS=0 ATTEMPTS=0 SUBMISSIONS=0 D04=0 D06=IDLE BACKUP=PASS')
    print('STAGE=PRE_PROBE_ONLY HUMAN_AUTH=NOT_PROVEN')


if __name__ == '__main__':
    try:
        run()
    except BaseException:
        print('PREFLIGHT=REFUSED DO_NOT_RUN_AUTH_UTILITY')
        raise SystemExit(1) from None
