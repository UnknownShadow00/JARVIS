"""Stdlib/synthetic canaries only; no candidate dependency or app import."""
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import socket

expected = json.loads(Path('/input/expected.json').read_text())
result = {'scope': 'stdlib synthetic child boundary probe, not framework integration'}
namespaces = {name: os.readlink('/proc/self/ns/' + name) for name in expected['parent_namespaces']}
assert all(namespaces[name] != parent for name, parent in expected['parent_namespaces'].items()), 'namespace isolation not established'
result['child_namespaces'] = namespaces
status = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
assert int(status['CapEff'].strip(), 16) == 0, 'effective capability retained'
assert status['NoNewPrivs'].strip() == '1', 'no_new_privs not established'
result['cap_eff'] = status['CapEff'].strip()
result['no_new_privs'] = status['NoNewPrivs'].strip()
readable = Path('/input/readonly-canary.txt').read_bytes()
assert hashlib.sha256(readable).hexdigest() == expected['readable_canary_sha256']
try:
    Path('/input/readonly-canary.txt').open('wb')
except OSError as error:
    assert error.errno in {errno.EROFS, errno.EACCES, errno.EPERM}
    result['readonly_input_write_denied_errno'] = error.errno
else:
    raise AssertionError('readonly input writable')
try:
    Path(expected['outside_canary_path']).read_bytes()
except OSError as error:
    assert error.errno in {errno.ENOENT, errno.EACCES, errno.EPERM}
    result['outside_synthetic_read_denied_errno'] = error.errno
else:
    raise AssertionError('outside synthetic file visible')
Path('/work/write-canary.txt').write_text('synthetic writable fixture only\n')
assert os.path.realpath('/tmp') == '/work/tmp', 'tmp escapes new private fixture'
Path('/tmp/tmp-canary.txt').write_text('synthetic child tmp only\n')
result['write_paths'] = ['/work/write-canary.txt', '/work/tmp/tmp-canary.txt']
fds = {}
for name in os.listdir('/proc/self/fd'):
    try:
        fds[name] = os.readlink('/proc/self/fd/' + name)
    except FileNotFoundError:
        pass
assert set(fds) <= {'0', '1', '2'}, 'unexpected inherited handle'
assert not any(expected['outside_canary_path'] in value for value in fds.values())
result['inherited_fd_targets'] = fds
for label, kind, value in [('address_space', resource.RLIMIT_AS, 1073741824),
                           ('file_size', resource.RLIMIT_FSIZE, 1048576),
                           ('open_files', resource.RLIMIT_NOFILE, 64),
                           ('core', resource.RLIMIT_CORE, 0)]:
    actual = resource.getrlimit(kind)
    assert actual == (value, value), (label, actual)
    result[label + '_limit'] = list(actual)
assert resource.getrlimit(resource.RLIMIT_CPU) == (5, 6)
result['cpu_limit'] = [5, 6]
result['network_canaries'] = []
for family, address in [(socket.AF_INET, ('192.0.2.1', 9)), (socket.AF_INET6, ('2001:db8::1', 9))]:
    try:
        with socket.socket(family, socket.SOCK_STREAM) as connection:
            connection.settimeout(0.25)
            connection.connect(address)
    except OSError as error:
        assert error.errno in {errno.ENETUNREACH, errno.EHOSTUNREACH, errno.EAFNOSUPPORT, errno.EPERM, errno.EACCES}
        result['network_canaries'].append({'family': int(family), 'errno': error.errno})
    else:
        raise AssertionError('external network canary connected')
result['status'] = 'SYNTHETIC_BOUNDARIES_PASSED'
print(json.dumps(result, sort_keys=True))
