#!/usr/bin/env python3
"""Offline namespace-isolated release gate. Requires existing local dependencies."""
import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import random
import resource
import subprocess
import sys
import tempfile
import time

from gauntlet_protocol import InvalidEvidence, validate
from required_test_inventory import load_inventory

PROBE_CASES = ('early_setup', 'early_call', 'early_teardown', 'final_exit', 'skip', 'crash', 'interrupt', 'leak', 'parameter_secret', 'empty', 'worker_crash', 'partial_output', 'mismatched_count', 'session_exit')

DEFAULT_DEPS = '/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages'
EXISTING = ['test_execution_pipeline.py', 'test_scheduler.py', 'test_scheduler_reliability.py',
            'test_operator_ledger.py', 'test_recovery_decisions.py', 'test_authority_enrollment.py',
            'test_task_queue_persistence.py', 'test_task_queue_callers.py', 'test_task_queue_store_safety.py',
            'test_agent_stubs.py', 'test_cancel_token.py', 'test_safety_levels.py', 'test_reporter.py',
            'test_audit_disaster.py', 'test_audit_disaster_app.py', 'test_authority_http_security.py',
            'test_operator_app.py', 'test_enrollment_app.py', 'test_storage_ancestry_security.py',
            'test_secure_transport.py', 'test_approval_gates.py', 'test_ready_client.py',
            'test_server_auth.py', 'test_server_integration.py']


def child(seed, mode, scenario_timeout, run_id):
    # Internal entry is not a host-execution fallback.
    if Path(__file__).resolve() != Path('/runner.py') or not Path('/source/app').is_dir() or not Path('/deps').is_dir():
        return 2
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))
    sys.path[:0] = ['/deps', '/source', '/source/tests']
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    import pytest
    inventory = load_inventory(Path("/inventory.json"), Path("/source"), mode, verify_sources=False)
    approved = inventory["identities"]
    collection = dict(skipped=0, deselected=0)
    from gauntlet_protocol import VERSION, case_identifiers, category
    expected, outcomes, timed_out, identities = [], {}, set(), {}
    session = dict(started=False, collected=False, finished=False, interrupted=False,
                   internal_error=False, collection_error=False, unexpected_report=False, pytest_exit_code=3, collected_count=0)
    import signal
    class Results:
        def pytest_sessionstart(self, session):
            state['started'] = True

        @pytest.hookimpl(trylast=True)
        def pytest_collection_modifyitems(self, items):
            identities.update({item.nodeid: approved.get(item.nodeid.removeprefix("/source/"), __import__("hashlib").sha256(("unexpected#" + str(i)).encode()).hexdigest()) for i, item in enumerate(items)})
            random.Random(seed).shuffle(items)
            if mode == 'case:final_exit':
                items.sort(key=lambda item: 'last' in item.name)
            expected.extend(identities[item.nodeid] for item in items)
            outcomes.update((identities[item.nodeid], dict(id=identities[item.nodeid], phases=[], timed_out=False)) for item in items)

        def pytest_collection_finish(self, session):
            state['collected'] = True

        @pytest.hookimpl(hookwrapper=True, tryfirst=True)
        def pytest_sessionfinish(self, session, exitstatus):
            outcome = yield
            state['finished'] = outcome.excinfo is None
            state['interrupted'] = state['interrupted'] or outcome.excinfo is not None
            state['pytest_exit_code'] = int(exitstatus)
            state['collected_count'] = session.testscollected

        def pytest_keyboard_interrupt(self, excinfo):
            state['interrupted'] = True

        def pytest_internalerror(self, excrepr, excinfo):
            state['internal_error'] = True

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_protocol(self, item, nextitem):
            def expired(*args):
                timed_out.add(identities[item.nodeid])
                raise TimeoutError('scenario deadline')
            old = signal.signal(signal.SIGALRM, expired)
            signal.setitimer(signal.ITIMER_REAL, scenario_timeout)
            try:
                yield
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                signal.signal(signal.SIGALRM, old)

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_teardown(self, item, nextitem):
            paths = [item.funcargs.get(name) for name in ('tmp_path', 'tmpdir')]
            yield
            import shutil
            for value in paths:
                if value is not None:
                    path = Path(str(value)).resolve()
                    if path.is_relative_to('/scratch/pytest'):
                        shutil.rmtree(path, ignore_errors=True)

        def pytest_deselected(self, items):
            collection["deselected"] += len(items)

        def pytest_collectreport(self, report):
            if report.skipped:
                collection["skipped"] += 1
            if report.failed:
                state['collection_error'] = True

        @pytest.hookimpl(hookwrapper=True)
        def pytest_runtest_makereport(self, item, call):
            outcome = yield
            report = outcome.get_result()
            report.gauntlet_category = category(call.excinfo.value) if call.excinfo is not None else None

        def pytest_runtest_logreport(self, report):
            if hasattr(report, "wasxfail"):
                state["unexpected_report"] = True
            identity = identities.get(report.nodeid)
            if identity not in outcomes:
                state['unexpected_report'] = True
                return
            outcomes[identity]['phases'].append(dict(phase=report.when, outcome=report.outcome,
                duration_seconds=report.duration, category=getattr(report, 'gauntlet_category', None)))

    state = session
    if mode == 'existing':
        files = EXISTING
    elif mode == 'probe':
        files = ['fixtures/reliability_gate_probe.py']
    elif mode == 'coverage':
        files = json.loads(Path('/coverage_modules.json').read_text())
    elif mode == 'reconciliation':
        files = ['test_release_security.py', 'test_ue5_security.py', 'test_baseline_enrollment.py']
    elif mode == 'r3':
        files = ['test_required_inventory_r3.py']
    elif mode == 'r2':
        files = ['test_scheduler_hardening_r2.py', 'test_gauntlet_protocol_r2.py']
    elif mode.startswith('case:'):
        files = ['fixtures/reliability_completion_probe.py']
    else:
        files = ['test_reliability_gauntlet.py']
    import contextlib
    class DiscardOutput:
        def write(self, value):
            return len(value)
        def flush(self):
            pass
    selection = ['-k', 'test_' + mode.split(':', 1)[1]] if mode.startswith('case:') else []
    with contextlib.redirect_stdout(DiscardOutput()), contextlib.redirect_stderr(DiscardOutput()):
        code = pytest.main(['-p', 'no:terminal', '-p', 'no:cacheprovider', '-p', 'pytest_asyncio.plugin',
                            '--basetemp=/scratch/pytest', '-c', '/source/pytest.ini',
                            *selection, *['/source/tests/' + name for name in files]], plugins=[Results()])
    for identity in timed_out:
        if identity in outcomes:
            outcomes[identity]['timed_out'] = True
    report = dict(protocol=VERSION, run_id=run_id, seed=seed, mode=mode, session=session,
                  collection=collection, expected=expected, scenarios=[outcomes[i] for i in expected], completion='pytest-returned-v2')
    print(json.dumps(report, allow_nan=False))
    return int(code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=16401)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--coverage', action='store_true')
    modes.add_argument('--reconciliation', action='store_true')
    modes.add_argument('--r3', action='store_true', help='R3 required inventory regression suite')
    modes.add_argument('--r2', action='store_true', help='R2 scheduler/protocol regression suite')
    modes.add_argument('--probe-case', choices=PROBE_CASES, help='one intentional completion/redaction failure fixture')
    modes.add_argument('--existing', action='store_true', help='replay selected neighboring offline tests separately')
    modes.add_argument('--probe', action='store_true', help='intentional reporting faults; use --scenario-timeout 1; expects exit 1')
    parser.add_argument('--deps', default=DEFAULT_DEPS, help='existing local site-packages; never installs packages')
    parser.add_argument('--output', type=Path, required=True, help='new JSON report path (exclusive creation)')
    parser.add_argument('--timeout', type=int, default=120)
    parser.add_argument('--scenario-timeout', type=int, default=15)
    args = parser.parse_args()
    if not 1 <= args.timeout <= 600 or not 1 <= args.scenario_timeout <= args.timeout:
        parser.error('timeouts must be positive and bounded by 600 seconds')
    if args.output.exists():
        parser.error('output already exists; choose a fresh report path')
    mode = 'coverage' if args.coverage else 'reconciliation' if args.reconciliation else 'r3' if args.r3 else 'existing' if args.existing else 'probe' if args.probe else 'r2' if args.r2 else 'case:' + args.probe_case if args.probe_case else 'new'
    import uuid
    run_id = uuid.uuid4().hex
    root = Path(__file__).resolve().parents[1]
    deps = Path(args.deps).resolve()
    started = time.monotonic()
    report = dict(qualification='OFFLINE_ENGINEERING_ONLY', seed=args.seed, started_at=datetime.now(UTC).isoformat(),
                  wall_timeout_seconds=args.timeout, network='isolated namespace', host_access=False)
    # Source identity covers every mounted source/test byte; no private config is mounted.
    inputs = [p for folder in ('app', 'tests') for p in (root / folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    inputs += [root / 'scripts/coverage_modules.json', root / 'scripts/test_enrollment.py', root / 'scripts/test_enrollment.json', root / 'scripts/required_test_inventory.py', root / 'scripts/required_tests.json', root / 'scripts/gauntlet_protocol.py', Path(__file__).resolve(), root / 'config.yaml.example', root / 'pytest.ini']
    report['source_sha256'] = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    cmd = ['/usr/bin/bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--cap-drop', 'ALL',
           '--ro-bind', '/usr', '/usr', '--symlink', 'usr/bin', '/bin', '--symlink', 'usr/lib', '/lib',
           '--symlink', 'usr/lib64', '/lib64', '--ro-bind', str(deps), '/deps',
           '--ro-bind', str(root / 'app'), '/source/app', '--ro-bind', str(root / 'tests'), '/source/tests',
           '--ro-bind', str(root / 'config.yaml.example'), '/source/config.yaml',
           '--ro-bind', str(root / 'pytest.ini'), '/source/pytest.ini',
           '--ro-bind', str(root / 'evals'), '/source/evals',
           '--ro-bind', str(root / 'scripts/sensor_node.py'), '/source/scripts/sensor_node.py',
           '--ro-bind', str(root / 'config.yaml.example'), '/source/config.yaml.example',
           '--ro-bind', str(root / 'docker-compose.yml'), '/source/docker-compose.yml',
           '--ro-bind', str(root / 'frontend/pwa/app.js'), '/source/frontend/pwa/app.js',
           '--ro-bind', str(root / 'frontend/hologram/app.js'), '/source/frontend/hologram/app.js',
           '--ro-bind', str(root / 'frontend/electron/preload.js'), '/source/frontend/electron/preload.js',
           '--ro-bind', str(root / 'scripts/coverage_modules.json'), '/coverage_modules.json',
           '--dir', '/input', '--ro-bind', str(root / 'tests/fixtures/baseline_api.py'), '/input/baseline_api.py',
           '--ro-bind', str(root / 'tests/fixtures/ancestor_hypothesis.py'), '/input/ancestor_hypothesis.py',
           '--symlink', '/source', '/input/source', '--symlink', '/source/tests', '/input/tests',
           '--symlink', '/source/tests/synthetic_authority.py', '/input/synthetic_authority.py',
           '--ro-bind', str(Path(__file__).resolve()), '/runner.py',
           '--ro-bind', str(root / 'scripts/gauntlet_protocol.py'), '/gauntlet_protocol.py',
           '--ro-bind', str(root / 'scripts/required_test_inventory.py'), '/required_test_inventory.py',
           '--ro-bind', str(root / 'scripts/test_enrollment.py'), '/test_enrollment.py',
           '--ro-bind', str(root / 'scripts/required_tests.json'), '/inventory.json',
           '--size', '67108864', '--tmpfs', '/scratch', '--dir', '/scratch/home', '--dir', '/scratch/tmp',
           '--dir', '/scratch/work', '--symlink', '/scratch/work', '/work',
           '--proc', '/proc', '--dev', '/dev', '--clearenv', '--setenv', 'PATH', '/usr/bin:/bin',
           '--setenv', 'HOME', '/scratch/home', '--setenv', 'TMPDIR', '/scratch/tmp',
           '--setenv', 'PYTHONDONTWRITEBYTECODE', '1', '--setenv', 'PYTHONPATH', '/deps:/source:/source/tests',
           '--setenv', 'OPENBLAS_NUM_THREADS', '1', '--setenv', 'OMP_NUM_THREADS', '1', '--chdir', '/scratch',
           '/usr/bin/python3.14', '-B', '/runner.py', '--child', str(args.seed), mode, str(args.scenario_timeout), run_id]
    def limits():
        os.umask(0o077)
        for kind, value in [(resource.RLIMIT_CPU, 110), (resource.RLIMIT_AS, 768 * 1024**2),
                            (resource.RLIMIT_NOFILE, 96), (resource.RLIMIT_FSIZE, 4 * 1024**2), (resource.RLIMIT_CORE, 0)]:
            resource.setrlimit(kind, (value, value))
    code = 2
    try:
        inventory = load_inventory(root / "scripts/required_tests.json", root, mode)
        report["required_count"] = len(inventory["identities"])
        report["inventory_sha256"] = inventory["sha256"]
        if not deps.is_dir():
            raise FileNotFoundError()
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            proc = subprocess.run(cmd, stdout=stdout, stderr=stderr, timeout=args.timeout,
                                  env={'PATH': '/usr/bin:/bin'}, preexec_fn=limits)
            report['child_exit_code'] = proc.returncode
            stdout.seek(0)
            raw = stdout.read(2 * 1024**2)
            if not raw:
                raise InvalidEvidence('missing_completion_evidence')
            def invalid_constant(value):
                raise ValueError('invalid_report_number')
            normalized = validate(json.loads(raw, parse_constant=invalid_constant), run_id=run_id,
                                  seed=args.seed, mode=mode, returncode=proc.returncode, required=inventory["identities"].values())
            report.update(normalized)
            code = normalized['gate_exit_code']
    except subprocess.TimeoutExpired:
        report.update(status='TIMEOUT', timed_out=True, collected=None, executed=None, counts=None)
    except InvalidEvidence as exc:
        report.update(status='BLOCKED', reason=exc.code, collected=None, executed=None, counts=None)
    except json.JSONDecodeError:
        report.update(status='BLOCKED', reason='malformed_completion_evidence', collected=None, executed=None, counts=None)
    except (OSError, ValueError, TypeError, KeyError):
        report.update(status='BLOCKED', reason='isolation_dependency_or_report_failure', collected=None, executed=None, counts=None)
    report.update(duration_seconds=time.monotonic() - started, gate_exit_code=code)
    if 'status' not in report:
        report['status'] = 'PASS' if code == 0 else 'FAIL'
    # Existing reports are evidence: never truncate or overwrite them.
    with args.output.open('x') as output:
        json.dump(report, output, indent=2)
        output.write('\n')
    for scenario in report.get('scenarios', []):
        print(f"{scenario['status']} seed={args.seed} {scenario['id']} ({scenario['duration_seconds']:.3f}s)")
    print(json.dumps({k: report[k] for k in ('status', 'duration_seconds', 'gate_exit_code')}))
    return code


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--child':
        raise SystemExit(child(int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), sys.argv[5]))
    raise SystemExit(main())
