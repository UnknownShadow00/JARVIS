#!/usr/bin/env python3
"""One conditional guarded fixture child after the retained successful prerequisite."""
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
BUNDLE = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1')


def copy_pinned(source, target, digest):
    assert not source.is_symlink()
    target.parent.mkdir(parents=True, exist_ok=True)
    hashed = hashlib.sha256()
    with source.open('rb') as incoming, target.open('xb') as outgoing:
        for chunk in iter(lambda: incoming.read(1024 * 1024), b''):
            hashed.update(chunk)
            outgoing.write(chunk)
    assert hashed.hexdigest() == digest, source


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_CPU, (120, 121))
    resource.setrlimit(resource.RLIMIT_FSIZE, (67108864, 67108864))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    sys.dont_write_bytecode = True
    prereq = json.loads((PACKET / 'PREFLIGHT.json').read_text())
    assert prereq['outcome'] == 'ISOLATION_PREFLIGHT_PASSED_INTEGRATION_NOT_YET_RUN'
    closure_file = ROOT / 'tasks/jarvis-framework-closure-r1/evidence-20261030T231119946730Z.json'
    assert hashlib.sha256(closure_file.read_bytes()).hexdigest() == 'dda702ee87a2a9e0ca6edceb7691eb31ef934bc1b8309595d100af5dac024b3b'
    closure = json.loads(closure_file.read_text())
    work = PACKET / 'work'
    inputs, output = work / 'integration-input', work / 'integration-output'
    inputs.mkdir(mode=0o700)
    output.mkdir(mode=0o700)
    (output / 'tmp').mkdir(mode=0o700)
    budget_bytes = 0
    archive_files = 0
    directories = set()
    largest = 0
    for name, row in closure['selected'].items():
        source = BUNDLE / row['relative_path']
        copy_pinned(source, inputs / 'wheels' / source.name, row['artifact_sha256'])
        with zipfile.ZipFile(source) as archive:
            for entry in archive.infolist():
                budget_bytes += entry.file_size
                largest = max(largest, entry.file_size)
                archive_files += not entry.is_dir()
                directories.update(str(parent) for parent in Path(entry.filename).parents)
                assert not entry.filename.endswith('.pth') and '.data/scripts/' not in entry.filename
    # Conservative controlled-wheel materialization envelope, not a malicious-
    # payload storage quota assertion. Actual new-tree totals are monitored too.
    envelope = {'declared_uncompressed_bytes': budget_bytes, 'archive_regular_entries': archive_files,
                'directory_name_count': len(directories), 'largest_entry_bytes': largest,
                'conservative_workspace_bytes': budget_bytes * 8 + 64 * 1024**2,
                'conservative_file_count': archive_files * 8 + 1000}
    assert envelope['conservative_workspace_bytes'] < 2 * 1024**3
    assert envelope['conservative_file_count'] < 100000
    assert largest < 67108864
    pip_row = prereq['installer']['retained_record']
    copy_pinned(BUNDLE / pip_row['artifact']['path'], inputs / 'bootstrap' / 'pip-26.2.1-py3-none-any.whl', pip_row['artifact']['sha256'])
    lock = ROOT / 'tasks/jarvis-framework-closure-r1/proposed-closure-20261030T231119946730Z.lock'
    copy_pinned(lock, inputs / 'closure.lock', prereq['closure_lock_sha256'])
    source_hashes = {'app/agent/task_queue.py': '50d1a4ebd6132f2593095874b170fa895d09c5bcd9ead9c598312cbf3314fc4c',
                     'app/agent/scheduler.py': '71183f5bf54bc36f96a62abf04a1ca73566805f0eda67cdefba5f4410a726181',
                     'app/server.py': '613a3b08ae074484f0187b0234105c05b85239c45c577eee69a2b0bd8e17052c'}
    for relative, digest in source_hashes.items():
        copy_pinned(ROOT / relative, inputs / 'source' / relative, digest)
    for name in ['fixture_tests.py', 'integration_child.py']:
        (inputs / name).write_bytes((PACKET / name).read_bytes())
    readonly = b'NEW SYNTHETIC READONLY INPUT\n'
    (inputs / 'readonly-canary.txt').write_bytes(readonly)
    outside = work / 'outside-canary.txt'
    expected = {'outside_canary_path': str(outside), 'readable_canary_sha256': hashlib.sha256(readonly).hexdigest(),
                'parent_namespaces': {name: os.readlink('/proc/self/ns/' + name) for name in ['user', 'mnt', 'pid', 'net', 'ipc', 'uts']},
                'source_sha256': source_hashes, 'pip_sha256': pip_row['artifact']['sha256'], 'lock_sha256': prereq['closure_lock_sha256'],
                'selected_versions': {name: row['version'] for name, row in closure['selected'].items()}}
    (inputs / 'expected.json').write_text(json.dumps(expected, indent=2) + '\n')
    descriptor = os.open(outside, os.O_RDONLY)
    os.set_inheritable(descriptor, True)
    # Same existing bwrap mechanism; /usr allowlist narrowed relative to preflight.
    argv = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--clearenv',
            '--setenv', 'PATH', '/usr/bin:/bin', '--setenv', 'LANG', 'C.UTF-8', '--setenv', 'TZ', 'UTC',
            '--cap-drop', 'ALL', '--dir', '/usr', '--ro-bind', '/usr/bin', '/usr/bin',
            '--ro-bind', '/usr/lib', '/usr/lib', '--dir', '/usr/share',
            '--ro-bind', '/usr/share/zoneinfo', '/usr/share/zoneinfo', '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64', '--proc', '/proc', '--dev', '/dev', '--dir', '/run',
            '--ro-bind', str(inputs), '/input', '--bind', str(output), '/work',
            '--symlink', '/work/tmp', '/tmp', '--chdir', '/work', '--remount-ro', '/',
            '--', '/usr/bin/python3', '-I', '-B', '-S', '/input/integration_child.py']
    started, monotonic = datetime.now(UTC).isoformat(), time.monotonic()
    process = subprocess.Popen(argv, cwd=ROOT, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'},
                               stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, close_fds=True, start_new_session=True, preexec_fn=limits)
    # Poll only this new private output tree. Safety stop has margin below the
    # authorized limits; never resize quotas or kill any unrelated process.
    reason = None
    peak_bytes = peak_files = 0
    try:
        while process.poll() is None:
            files = [p for p in output.rglob('*') if p.is_file()]
            sizes = []
            for path in files:
                try:sizes.append(path.stat().st_size)
                except FileNotFoundError:pass  # Installer atomic rename in this fixture only.
            peak_bytes, peak_files = max(peak_bytes, sum(sizes)), max(peak_files, len(files))
            if sum(sizes) > 256 * 1024**2 or len(files) > 20000 or time.monotonic() - monotonic > 180:
                reason = 'fixture safety/time threshold exceeded; STOP_NO_FALLBACK'
                os.killpg(process.pid, signal.SIGKILL)
                break
            time.sleep(0.05)
        stdout, stderr = process.communicate(timeout=5)
    finally:
        os.close(descriptor)
    (PACKET / 'integration.stdout.txt').write_text(stdout)
    (PACKET / 'integration.stderr.txt').write_text(stderr)
    child_result = json.loads((output / 'RESULT.json').read_text()) if (output / 'RESULT.json').is_file() else None
    all_files = [p for p in work.rglob('*') if p.is_file()]
    total_bytes = sum(p.stat().st_size for p in all_files)
    assert len(all_files) <= 100000 and total_bytes <= 2 * 1024**3
    result = {'started_at': started, 'finished_at': datetime.now(UTC).isoformat(), 'elapsed_seconds': time.monotonic() - monotonic,
              'argv': argv, 'close_fds': True, 'environment': {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8'},
              'preexec_limits': {'address_space_bytes': 1073741824, 'cpu_seconds': [120, 121], 'file_bytes': 67108864, 'open_fds': 64, 'core_bytes': 0},
              'wall_safety_stop_seconds': 180, 'precalculated_envelope': envelope,
              'max_active_top_level_fixture_children': 1, 'top_level_test_children_in_unit': 2,
              'output_observed_peak_files': peak_files, 'output_observed_peak_bytes': peak_bytes,
              'complete_work_tree_files': len(all_files), 'complete_work_tree_bytes': total_bytes,
              'exitcode': process.returncode, 'safety_stop': reason, 'child_result': child_result,
              'status': 'PASS_NARROW_FIXTURE_INTEGRATION' if process.returncode == 0 and child_result and child_result['status'] == 'NARROW_FIXTURE_INTEGRATION_PASSED' else 'STOPPED_AT_FAILED_STAGE_NO_FALLBACK'}
    with (PACKET / 'INTEGRATION.json').open('x') as handle:json.dump(result, handle, indent=2);handle.write('\n')
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'PASS_NARROW_FIXTURE_INTEGRATION' else 2


if __name__ == '__main__':
    raise SystemExit(main())
