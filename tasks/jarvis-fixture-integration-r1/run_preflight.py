#!/usr/bin/env python3
"""One existing-bubblewrap prerequisite attempt; no fallback or installer execution."""
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
BUNDLE = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 6))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1048576, 1048576))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    sys.dont_write_bytecode = True
    os.chmod(PACKET, 0o700)  # This new task-private directory only.
    started = datetime.now(UTC).isoformat()
    lock = ROOT / 'tasks/jarvis-framework-closure-r1/proposed-closure-20261030T231119946730Z.lock'
    assert sha(lock.read_bytes()) == 'c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8'
    bundle_manifest = (BUNDLE / 'SHA256SUMS').read_bytes()
    assert sha(bundle_manifest) == '1c598e37c69ec2629fed3a3b30652aaf7ec0d2dbfe7906a810fc7036d1b9d390'
    selected_expected = next(line.split('  ', 1)[0] for line in bundle_manifest.decode().splitlines() if line.endswith('  results/selected-artifacts.json'))
    selected_raw = (BUNDLE / 'results/selected-artifacts.json').read_bytes()
    assert sha(selected_raw) == selected_expected
    pip_record = next(row for row in json.loads(selected_raw) if row['name'] == 'pip')
    assert pip_record['artifact']['sha256'] == '71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e'
    pip_wheel = BUNDLE / pip_record['artifact']['path']
    pip_hash = hashlib.sha256()
    with pip_wheel.open('rb') as handle:
        for data in iter(lambda: handle.read(1024 * 1024), b''):
            pip_hash.update(data)
    assert pip_hash.hexdigest() == pip_record['artifact']['sha256']
    bwrap = Path('/usr/bin/bwrap')
    info = bwrap.stat()
    assert info.st_uid == 0 and not info.st_mode & (stat.S_ISUID | stat.S_ISGID | 0o022)
    try:
        capabilities = os.getxattr(bwrap, 'security.capability')
    except OSError as error:
        assert error.errno == 61  # Linux ENODATA, not an ignored metadata error.
        capabilities = b''
    assert not capabilities
    bwrap_bytes = bwrap.read_bytes()
    expected_md5 = next(line.split()[0] for line in Path('/var/lib/dpkg/info/bubblewrap.md5sums').read_text().splitlines() if line.endswith('  usr/bin/bwrap'))
    assert hashlib.md5(bwrap_bytes).hexdigest() == expected_md5
    packages = subprocess.check_output(['/usr/bin/dpkg-query', '-W', '-f=${Package} ${Version} ${Status}\n', 'bubblewrap', 'python3.14', 'python3.14-minimal', 'util-linux'], text=True)
    work = PACKET / 'work'
    work.mkdir(mode=0o700)
    inputs, output = work / 'probe-input', work / 'probe-output'
    inputs.mkdir(mode=0o700)
    output.mkdir(mode=0o700)
    (output / 'tmp').mkdir(mode=0o700)
    outside = work / 'outside-canary.txt'
    outside.write_text('NEW SYNTHETIC OUTSIDE CANARY; NOT A CREDENTIAL\n')
    readonly = b'NEW SYNTHETIC READONLY INPUT\n'
    (inputs / 'readonly-canary.txt').write_bytes(readonly)
    (inputs / 'probe.py').write_bytes((PACKET / 'probe_child.py').read_bytes())
    expected = {'outside_canary_path': str(outside), 'readable_canary_sha256': sha(readonly),
                'parent_namespaces': {name: os.readlink('/proc/self/ns/' + name) for name in ['user', 'mnt', 'pid', 'net', 'ipc', 'uts']}}
    (inputs / 'expected.json').write_text(json.dumps(expected, indent=2) + '\n')
    descriptor = os.open(outside, os.O_RDONLY)
    os.set_inheritable(descriptor, True)  # Deliberate synthetic handle must not reach child.
    argv = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session',
            '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'LANG', 'C.UTF-8',
            '--cap-drop', 'ALL', '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--dir', '/run',
            '--ro-bind', str(inputs), '/input', '--bind', str(output), '/work',
            '--symlink', '/work/tmp', '/tmp', '--chdir', '/work', '--remount-ro', '/',
            '--', '/usr/bin/python3', '-I', '-B', '/input/probe.py']
    record = {'started_at': started, 'scope': 'ONE recognized existing unprivileged bubblewrap/stdlb synthetic prerequisite attempt; no candidate execution',
              'installer': {'recognized': True, 'source': 'retained PyPA pip 26.2.1 public wheel', 'sha256_verified': pip_hash.hexdigest(),
                            'retained_record': pip_record, 'retained_origin_record_sha256': sha(selected_raw),
                            'retained_signature_claim_not_reverified_now': pip_record['verification'], 'executed': False},
              'bwrap': {'package_metadata': packages, 'binary_sha256': sha(bwrap_bytes), 'installed_package_md5_matches': True,
                        'root_owned_not_setuid_or_setgid_or_file_capable': True},
              'runtime': {'version': sys.version, 'executable': sys.executable,
                          'binary_realpath': str(Path(sys.executable).resolve()), 'binary_sha256': sha(Path(sys.executable).read_bytes())},
              'closure_lock_sha256': sha(lock.read_bytes()), 'argv': argv, 'environment': {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'},
              'close_fds': True, 'deliberately_inheritable_synthetic_parent_fd': descriptor,
              'preexec_limits': {'address_space_bytes': 1073741824, 'cpu_seconds': [5, 6], 'file_bytes': 1048576, 'open_fds': 64, 'core_bytes': 0},
              'wall_timeout_seconds': 20, 'expected': expected, 'attempts': 1,
              'no_installer_or_candidate_import_before_boundary_pass': True}
    timer = time.monotonic()
    process = None
    try:
        process = subprocess.Popen(argv, cwd=ROOT, env=record['environment'], stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, close_fds=True,
                                   start_new_session=True, preexec_fn=limits)
        try:
            stdout, stderr = process.communicate(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            record['timeout'] = True
        record.update({'returncode': process.returncode, 'stdout': stdout, 'stderr': stderr})
        if process.returncode == 0:
            value = json.loads(stdout)
            assert value['status'] == 'SYNTHETIC_BOUNDARIES_PASSED'
            record['probe_result'] = value
            record['outcome'] = 'ISOLATION_PREFLIGHT_PASSED_INTEGRATION_NOT_YET_RUN'
        else:
            record['outcome'] = 'BLOCKED_AT_REQUIRED_ISOLATION_OPERATION_STOP_NO_FALLBACK'
    except Exception as error:
        record.update({'outcome': 'BLOCKED_AT_REQUIRED_ISOLATION_OPERATION_STOP_NO_FALLBACK',
                       'error_type': type(error).__name__, 'error': str(error)})
    finally:
        os.close(descriptor)
    record.update({'finished_at': datetime.now(UTC).isoformat(), 'elapsed_seconds': time.monotonic() - timer,
                   'new_tree_file_count': sum(p.is_file() for p in work.rglob('*')),
                   'new_tree_bytes': sum(p.stat().st_size for p in work.rglob('*') if p.is_file()),
                   'probe_output_entries': sorted(str(p.relative_to(output)) for p in output.rglob('*'))})
    target = PACKET / 'PREFLIGHT.json'
    with target.open('x') as handle:
        json.dump(record, handle, indent=2)
        handle.write('\n')
    print(json.dumps(record, indent=2))
    return 0 if record['outcome'] == 'ISOLATION_PREFLIGHT_PASSED_INTEGRATION_NOT_YET_RUN' else 2


if __name__ == '__main__':
    raise SystemExit(main())
