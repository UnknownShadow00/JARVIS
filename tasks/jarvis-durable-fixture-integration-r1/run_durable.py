#!/usr/bin/env python3
"""One low-resource durable-store fixture run; owned bounded output files, no pipes."""
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import shutil
import signal
import stat
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
PRIOR = ROOT / 'tasks/jarvis-fixture-integration-r1'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CPU, (120, 121))
    resource.setrlimit(resource.RLIMIT_FSIZE, (67108864, 67108864))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    sys.dont_write_bytecode = True
    os.chmod(PACKET, 0o700)
    started = datetime.now(UTC).isoformat()
    available = {line.split(':', 1)[0]: line.split(':', 1)[1].strip() for line in Path('/proc/meminfo').read_text().splitlines() if line.startswith(('MemAvailable:', 'SwapFree:'))}
    load = os.getloadavg()
    disk = shutil.disk_usage(ROOT)
    assert int(available['MemAvailable'].split()[0]) >= 3 * 1024**2 and disk.free >= 3 * 1024**3
    assert load[0] < os.cpu_count(), 'defer fixture workload under current contention'
    own_overlap = subprocess.run(['pgrep', '-af', '^python3 -B tasks/jarvis-fixture-integration-r1/run_(preflight|integration).py$'], capture_output=True, text=True).stdout
    assert not own_overlap, 'previous JARVIS fixture runner still active'
    resource_record = {'at_utc': started, 'cpu_count': os.cpu_count(), 'load_average': load, 'memory': available, 'disk_free': disk.free,
                       'prior_runner_matches': own_overlap, 'worktrees': subprocess.check_output(['git', 'worktree', 'list', '--porcelain'], cwd=ROOT, text=True),
                       'limit': 'public aggregate resources and own runner/worktree only; other project coordination stays with parent'}
    (PACKET / 'RESOURCE-CHECK.json').write_text(json.dumps(resource_record, indent=2) + '\n')
    assert sha(PRIOR / 'SHA256SUMS') == '8ebf51763947ca18a9cff2be2308fe9e764a26aa9c6000b02510ecf2b8e31761'
    assert sha(PRIOR / 'MATERIALIZED-SHA256SUMS') == '6701baa39697b9e250429f8b77938fa3032ac747b1d9798fdee0196e11937a7d'
    for line in (PRIOR / 'MATERIALIZED-SHA256SUMS').read_text().splitlines():
        expected, name = line.split('  ', 1)
        path = PRIOR / name
        assert not path.is_symlink() and sha(path) == expected, name
    assert sha('/usr/bin/bwrap') == '523da3e7399044be5163aee6f57a77a6bef7454376e28f0a0627920bae1b76b6'
    assert sha('/usr/bin/python3.14') == '52e0a13e60a981d8c4b6478be2ba5176f69da07948a056bf49cf6f077e30cb41'
    previous = json.loads((PRIOR / 'SOURCE-ENVIRONMENT-AND-LIMITS.json').read_text())
    guard_hash = previous['fixture_and_runner_sha256']['integration_child.py']
    assert sha(PRIOR / 'integration_child.py') == guard_hash
    work = PACKET / 'work'
    work.mkdir(mode=0o700)
    inputs, output = work / 'input', work / 'output'
    inputs.mkdir(mode=0o700)
    output.mkdir(mode=0o700)
    (output / 'tmp').mkdir(mode=0o700)
    outside = work / 'outside-canary.txt'
    outside.write_text('NEW SYNTHETIC OUTSIDE CANARY ONLY\n')
    readonly = b'NEW DURABLE SYNTHETIC READONLY INPUT\n'
    (inputs / 'readonly-canary.txt').write_bytes(readonly)
    (inputs / 'guard_source.py').write_bytes((PRIOR / 'integration_child.py').read_bytes())
    sources = {name: previous['current_source_sha256'][name] for name in ['app/agent/task_queue.py', 'app/agent/scheduler.py', 'app/server.py']}
    for name, digest in sources.items():
        assert sha(ROOT / name) == digest, name
        target = inputs / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / name).read_bytes())
    for name in ['durable_tests.py', 'durable_child.py']:(inputs / name).write_bytes((PACKET / name).read_bytes())
    stdout_path, stderr_path = PACKET / 'durable.stdout.txt', PACKET / 'durable.stderr.txt'
    expected = {'outside_canary_path': str(outside), 'readable_canary_sha256': hashlib.sha256(readonly).hexdigest(),
                'parent_namespaces': {name: os.readlink('/proc/self/ns/' + name) for name in ['user', 'mnt', 'pid', 'net', 'ipc', 'uts']},
                'guard_source_sha256': guard_hash, 'source_sha256': sources, 'versions': previous['installed_versions_inside_child']}
    (inputs / 'expected.json').write_text(json.dumps(expected, indent=2) + '\n')
    target = PRIOR / 'work/integration-output/site-packages'
    argv = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
            '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'TZ', 'UTC',
            '--cap-drop', 'ALL', '--dir', '/usr', '--ro-bind', '/usr/bin', '/usr/bin', '--ro-bind', '/usr/lib', '/usr/lib',
            '--dir', '/usr/share', '--ro-bind', '/usr/share/zoneinfo', '/usr/share/zoneinfo',
            '--ro-bind', '/lib', '/lib', '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--dir', '/run',
            '--ro-bind', str(inputs), '/input', '--ro-bind', str(target), '/deps', '--bind', str(output), '/work',
            '--symlink', '/work/tmp', '/tmp', '--chdir', '/work', '--remount-ro', '/',
            '--', '/usr/bin/python3', '-I', '-B', '-S', '/input/durable_child.py']
    descriptor = os.open(outside, os.O_RDONLY)
    os.set_inheritable(descriptor, True)
    safety_stop = None
    peak_files = peak_bytes = 0
    timer = time.monotonic()
    try:
        with stdout_path.open('x') as stdout, stderr_path.open('x') as stderr:
            process = subprocess.Popen(argv, cwd=ROOT, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, stdin=subprocess.DEVNULL,
                                       stdout=stdout, stderr=stderr, close_fds=True, start_new_session=True, preexec_fn=limits)
            while process.poll() is None:
                files = [path for path in work.rglob('*') if path.is_file()]
                sizes = []
                for path in files:
                    try:sizes.append(path.stat().st_size)
                    except FileNotFoundError:pass  # Application atomic temp publication in synthetic state only.
                peak_files, peak_bytes = max(peak_files, len(files)), max(peak_bytes, sum(sizes))
                if len(files) > 20000 or sum(sizes) > 256 * 1024**2 or time.monotonic() - timer > 180:
                    safety_stop = 'controlled-workload safety threshold; STOP_NO_FALLBACK'
                    os.killpg(process.pid, signal.SIGKILL)
                    break
                time.sleep(0.05)
            process.wait(timeout=5)
    finally:os.close(descriptor)
    child = json.loads((output / 'RESULT.json').read_text()) if (output / 'RESULT.json').exists() else None
    for name, digest in sources.items():assert sha(ROOT / name) == digest, name
    files = [path for path in work.rglob('*') if path.is_file()]
    total = sum(path.stat().st_size for path in files)
    assert len(files) <= 100000 and total <= 2 * 1024**3
    result = {'started_at': started, 'finished_at': datetime.now(UTC).isoformat(), 'elapsed_child_seconds': time.monotonic() - timer,
              'argv': argv, 'env': {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'}, 'close_fds': True, 'outside_synthetic_fd_deliberately_inheritable': descriptor,
              'resource_limits': {'AS': 1073741824, 'CPU': [120, 121], 'FSIZE': 67108864, 'NOFILE': 64, 'CORE': 0},
              'wall_stop_seconds': 180, 'top_level_payload_children': 1, 'max_concurrent_payloads': 1,
              'peak_observed_work_files': peak_files, 'peak_observed_work_bytes': peak_bytes,
              'work_tree_final_files': len(files), 'work_tree_final_bytes': total,
              'dependency_reuse': {'path': str(target), 'mount': 'read-only /deps', 'materialized_manifest_sha256': '6701baa39697b9e250429f8b77938fa3032ac747b1d9798fdee0196e11937a7d', 'files_hash_checked': 1022, 'installer_invoked': False},
              'source_sha256': sources, 'exitcode': process.returncode, 'safety_stop': safety_stop, 'child': child,
              'stdout_file': stdout_path.name, 'stderr_file': stderr_path.name,
              'status': 'PASS_DURABLE_FIXTURE_INTEROPERABILITY' if process.returncode == 0 and child and child['status'] == 'DURABLE_FIXTURE_INTEROPERABILITY_PASSED' else 'STOPPED_NO_FALLBACK'}
    with (PACKET / 'RUN.json').open('x') as handle:json.dump(result, handle, indent=2);handle.write('\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS_DURABLE_FIXTURE_INTEROPERABILITY' else 2


if __name__ == '__main__':raise SystemExit(main())
