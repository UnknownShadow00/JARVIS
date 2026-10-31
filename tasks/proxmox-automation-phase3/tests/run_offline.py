#!/usr/bin/env python3
"""Run from any cwd with -I -B. Refuse all IP networking and real credential opens."""
import io
import json
import os
from pathlib import Path
import socket
import sys
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src'), str(ROOT / 'tests')]
COUNTS = {'ip_connects_blocked': 0, 'real_credential_opens_blocked': 0,
          'unix_connects': 0, 'unix_socket_objects': 0}


def audit(event, args):
    if event == 'socket.connect':
        address = args[1]
        if isinstance(address, tuple):
            COUNTS['ip_connects_blocked'] += 1
            raise PermissionError('OFFLINE_TEST_NO_IP_CONNECTIONS')
        COUNTS['unix_connects'] += 1
    elif event == 'socket.__new__':
        if args[1] == socket.AF_UNIX:
            COUNTS['unix_socket_objects'] += 1
    elif event == 'socket.getaddrinfo':
        raise PermissionError('OFFLINE_TEST_NO_DNS')
    elif event == 'open' and isinstance(args[0], (str, bytes)):
        path = os.fsdecode(args[0])
        if '/.config/g6k-proxmox/' in path or path in (
                '/var/lib/g6k-serial-host/token.json', '/etc/shadow', '/root/.ssh/id_rsa'):
            COUNTS['real_credential_opens_blocked'] += 1
            raise PermissionError('OFFLINE_TEST_NO_REAL_CREDENTIALS')


class Result(unittest.TextTestResult):
    subtests = 0
    def addSubTest(self, test, subtest, err):
        self.subtests += 1
        super().addSubTest(test, subtest, err)


def main():
    sys.addaudithook(audit)
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(stream=stream, verbosity=2, resultclass=Result).run(suite)
    evidence = ROOT / 'evidence'
    text = stream.getvalue()
    (evidence / 'offline-tests.txt').write_text(text)
    summary = {'at_utc': datetime.now(timezone.utc).isoformat(), 'python': sys.version.split()[0],
               'methods': result.testsRun, 'subtests': result.subtests, 'failures': len(result.failures),
               'errors': len(result.errors), 'skipped': len(result.skipped), 'successful': result.wasSuccessful(),
               'guard_counts': COUNTS, 'live_pve_calls': 0, 'live_guest_calls': 0,
               'actual_cross_uid_isolation_tested': False,
               'limits': ['Synthetic remote state and same-UID IPC fixture are not live isolation evidence',
                          'Nexus child seccomp tests do not qualify the Ubuntu guest or Gate 6K',
                          'Audit hook applies to the runner; explicit child programs only run bounded SQLite/seccomp fixtures']}
    (evidence / 'offline-tests.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(text)
    print(json.dumps(summary, sort_keys=True))
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__ == '__main__':
    raise SystemExit(main())
