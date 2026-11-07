#!/usr/bin/env python3
"""Use /usr/bin/python3 -I -B /opt/g6k-serial/entry.py <mode>."""
import os
from pathlib import Path
import secrets
import sys

# -I removes environment/user-site/cwd imports. The reviewed installed tree is
# root-controlled; runtime verifies ownership and its complete pinned manifest.
sys.path.insert(0, str(Path(__file__).resolve().parent))


def main():
    from g6k_serial.protocol import ACTIONS, encode, need
    from g6k_serial import runtime
    need(len(sys.argv) >= 2, 'MODE')
    mode = sys.argv[1]
    if mode == 'client':
        need(3 <= len(sys.argv) <= 4 and sys.argv[2] in ACTIONS, 'CLIENT_ARGUMENTS')
        result = runtime.client(sys.argv[2], sys.argv[3] if len(sys.argv) == 4 else secrets.token_hex(16))
        sys.stdout.buffer.write(encode(result))
        return 0 if result['result'] == 'REPORTED' else 2
    need(len(sys.argv) == 2, 'ARGUMENTS')
    if mode == 'host':
        runtime.host()
    elif mode == 'worker':
        runtime.worker()
    elif mode in ('init-host', 'init-worker'):
        runtime.initialize_state(worker=mode == 'init-worker')
    elif mode in ('revoke-host', 'revoke-worker'):
        runtime.revoke(worker=mode == 'revoke-worker')
    elif mode == 'issue-token':
        from g6k_serial.provision import issue
        issue()
    else:
        need(False, 'MODE')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (Exception, KeyboardInterrupt):
        # Never log str(exception), repr(settings) or stack frames with secrets.
        sys.stderr.write('G6K_STOP: operation refused; preserve state for operator review.\n')
        raise SystemExit(2)
