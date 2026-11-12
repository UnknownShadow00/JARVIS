"""Complete qualified offline gate. No installs, providers or host pytest fallback.

Both direct-script and -m invocation use this same acceptance implementation.
Inventory-only discovery is explicitly labelled and never constitutes PASS.
"""
import argparse
import concurrent.futures
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
DEPS = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages')
MODES = ('safety', 'coverage', 'reconciliation', 'r3', 'r2', 'new', 'existing')
PUBLIC = ('conftest.py', 'pytest.ini', 'config.yaml.example', 'docker-compose.yml',
          'frontend/pwa/app.js', 'frontend/hologram/app.js', 'frontend/electron/preload.js',
          '.github/workflows/tests.yml')
SCRIPTS = ('gauntlet_protocol.py', 'reliability_gauntlet.py', 'reliability_gate_checks.py',
           'required_test_inventory.py', 'required_tests.json', 'test_enrollment.py',
           'test_enrollment.json', 'coverage_modules.json', 'propose_required_inventory.py',
           'sensor_node.py', 'offline_acceptance.py', 'offline_contracts.py',
           'offline_environment.json', 'historical_packet_inventory.json', 'required_nodes_6341648.json')
HELPERS = ('tasks/jarvis-v2-baseline-coverage-remediation-r2/check_gate_contracts.py',
           'tasks/jarvis-v2-baseline-coverage-remediation-r2/check_adversaries.py',
           'tasks/jarvis-v2-final-integration-rehearsal-r2/replay_audit_attacks.py')


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        print(json.dumps(dict(status='BLOCKED', reason='invalid_offline_acceptance_arguments')))
        raise SystemExit(2)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root, name):
    parts = Path(name).parts
    if not parts or Path(name).is_absolute() or '..' in parts:
        raise ValueError('unsafe_public_source_path')
    path = root
    for part in parts:
        path = path/part
        if path.is_symlink():
            raise ValueError('unsafe_public_source_path')
    return path


def public_hashes(root):
    explicit = [safe_path(root, p) for p in PUBLIC] + [safe_path(root, 'scripts/'+p) for p in SCRIPTS] + [safe_path(root, p) for p in HELPERS]
    if any(not p.is_file() for p in explicit) or any(not (root/p).is_dir() for p in ('app', 'tests', 'evals')):
        raise ValueError('missing_public_source')
    entries = [p for folder in ('app', 'tests', 'evals') for p in (root/folder, *(root/folder).rglob('*')) if '__pycache__' not in p.parts]
    entries += explicit
    if any(p.is_symlink() for p in entries):
        raise ValueError('unsafe_public_source_path')
    return {str(p.relative_to(root)): sha(p) for p in sorted(set(entries)) if p.is_file()}


def required_nodes(root):
    from required_test_inventory import load_inventory
    body = json.loads((root/'scripts/required_tests.json').read_text())
    positive = {name for name in body['suites'] if name != 'probe' and not name.startswith('case:')}
    if positive != set(MODES):
        raise ValueError('unreviewed_positive_suite')
    nodes = []
    for mode in MODES:
        loaded = load_inventory(root/'scripts/required_tests.json', root, mode)
        if len(loaded['identities']) != len(body['suites'][mode]['nodeids']):
            raise ValueError('required_identity_mapping_mismatch')
        nodes.extend(body['suites'][mode]['nodeids'])
    if len(nodes) != len(set(nodes)):
        raise ValueError('duplicate_required_identity')
    return sorted(nodes)


def check_environment():
    policy = json.loads((ROOT/'scripts/offline_environment.json').read_text())
    current = {d.metadata['Name']: d.version for d in importlib.metadata.distributions(path=[str(DEPS)])}
    if (platform.python_version() != policy['python'] or current != policy['packages']
            or subprocess.check_output(['/usr/bin/bwrap', '--version'], text=True).strip() != policy['bwrap']):
        raise ValueError('unqualified_offline_environment')
    return dict(python=platform.python_version(), packages=current, bwrap=policy['bwrap'])


def check_ci_inventory(root):
    expected = json.loads((root/'scripts/offline_environment.json').read_text())['workflow_paths']
    paths = list(safe_path(root, '.github/workflows').iterdir())
    if any(p.is_symlink() or not p.is_file() for p in paths) or {str(p.relative_to(root)) for p in paths} != set(expected):
        raise ValueError('unreviewed_ci_entrypoint')


def packet_hashes(root):
    policy = json.loads((root/'scripts/historical_packet_inventory.json').read_text())
    folders = [safe_path(root, name) for name in policy['folders']]
    entries = [p for folder in folders for p in (folder, *folder.rglob('*'))]
    if any(p.is_symlink() for p in entries):
        raise ValueError('unsafe_historical_packet_path')
    actual = {str(p.relative_to(root)) for p in entries if p.is_file() and '__pycache__' not in p.parts}
    if actual != set(policy['files']):
        raise ValueError('historical_packet_set_mismatch')
    for name, digest in policy['files'].items():
        path = safe_path(root, name)
        if not any(path.is_relative_to(folder) for folder in folders) or sha(path) != digest:
            raise ValueError('historical_packet_integrity_mismatch')
    return policy['files']


def complete_suite(body, required):
    from gauntlet_protocol import case_identifiers
    identities = set(case_identifiers(required).values())
    scenarios = body.get('scenarios', [])
    observed = [s['id'] for s in scenarios]
    session = body.get('session', {})
    return (body.get('status') == 'PASS' and body.get('gate_exit_code') == body.get('child_exit_code') == 0
            and len(observed) == len(set(observed)) == len(identities) and set(observed) == identities
            and body.get('required_missing') == body.get('unexpected_collected') == 0
            and body.get('executed') == len(identities)
            and body.get('collection') == dict(skipped=0, deselected=0)
            and all(session.get(k) is True for k in ('started', 'collected', 'finished'))
            and all(session.get(k) is False for k in ('interrupted', 'internal_error', 'collection_error', 'unexpected_report'))
            and session.get('pytest_exit_code') == 0 and session.get('collected_count') == len(identities)
            and body.get('counts') == dict(PASS=len(identities), FAIL=0, ERROR=0, SKIP=0, INCOMPLETE=0)
            and all(s['complete'] and not s['timed_out'] and [p['phase'] for p in s['phases']] == ['setup', 'call', 'teardown']
                    and all(p['outcome'] == 'passed' for p in s['phases']) for s in scenarios))


def acceptance(out):
    before = public_hashes(ROOT)
    nodes = required_nodes(ROOT)
    environment = check_environment()
    check_ci_inventory(ROOT)
    historical = packet_hashes(ROOT)
    git = lambda *a: subprocess.check_output(['git', *a], cwd=ROOT, text=True).strip()
    tracked = set(subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0'))
    if not set(before) <= tracked or git('status', '--porcelain', '--untracked-files=no'):
        raise ValueError('clean_committed_checkout_required')
    snapshot = Path(tempfile.mkdtemp(prefix='jarvis-canonical-safety-acceptance-'))/'source'
    snapshot.mkdir()
    for name in before:
        dst = snapshot/name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT/name, dst)
        dst.chmod(0o444)
    for path in sorted((p for p in snapshot.rglob('*') if p.is_dir()), key=lambda p: len(p.parts), reverse=True):
        path.chmod(0o555)
    snapshot.chmod(0o555)
    if public_hashes(snapshot) != before:
        raise ValueError('snapshot_copy_mismatch')
    with (out/'SOURCE.json').open('x') as stream:
        json.dump(dict(source_commit=git('rev-parse', 'HEAD'), git_tree=git('rev-parse', 'HEAD^{tree}'), source_sha256=before,
                       source_snapshot=str(snapshot), environment=environment, inventory_sha256=sha(ROOT/'scripts/required_tests.json')), stream, indent=2)
    jobs = {}
    for mode in MODES:
        flag = [] if mode == 'new' else ['--'+mode]
        jobs[mode] = [str(snapshot/'scripts/reliability_gauntlet.py'), *flag, '--output', str(out/(mode+'.json'))]
        if mode != 'existing':
            jobs[mode+'-seed42'] = [str(snapshot/'scripts/reliability_gauntlet.py'), *flag, '--seed', '42', '--output', str(out/(mode+'-seed42.json'))]
    jobs['negative14'] = [str(snapshot/'scripts/reliability_gate_checks.py'), '--output-dir', str(out/'negative14')]
    for kind in ('gate22', 'adversaries11', 'attacks12'):
        jobs[kind] = [str(ROOT/'scripts/offline_contracts.py'), kind, '--source-root', str(snapshot), '--output-dir', str(out/kind)]

    def run(pair):
        name, args = pair
        command = [sys.executable, '-B', *args]
        with (out/(name+'.log')).open('x') as stream:
            try:
                process = subprocess.run(command, cwd=snapshot, stdout=stream, stderr=subprocess.STDOUT, timeout=600)
                code = process.returncode
            except subprocess.TimeoutExpired:
                stream.write('offline_acceptance_job_timeout\n')
                code = 124
        return dict(name=name, command=command, exit=code)

    runs = list(concurrent.futures.ThreadPoolExecutor(max_workers=3).map(run, jobs.items()))
    with (out/'RUNS.json').open('x') as stream:
        json.dump(runs, stream, indent=2)
    manifest = json.loads((ROOT/'scripts/required_tests.json').read_text())
    suites, identities, repeats, valid = [], [], 0, all(r['exit'] == 0 for r in runs)
    for mode in MODES:
        for suffix in ('', '-seed42') if mode != 'existing' else ('',):
            body = json.loads((out/(mode+suffix+'.json')).read_text())
            valid &= complete_suite(body, manifest['suites'][mode]['nodeids'])
            if suffix:
                repeats += body['counts']['PASS']
            else:
                identities.extend(s['id'] for s in body['scenarios'])
                suites.append(dict(mode=mode, counts=body['counts'], required_missing=body['required_missing'], unexpected=body['unexpected_collected'], executed=body['executed'], gate_exit=body['gate_exit_code'], child_exit=body['child_exit_code']))
    for kind, count, key in (('gate22', 22, 'contract_pass'), ('adversaries11', 11, 'passed')):
        rows = json.loads((out/kind/'SUMMARY.json').read_text())
        valid &= len(rows) == count and all(r[key] for r in rows)
    rows = json.loads((out/'negative14/SUMMARY.json').read_text())['checks']
    valid &= len(rows) == 14 and all(r['status'] == 'PASS' and r['gate_exit'] != 0 and r['gate_status'] != 'PASS' for r in rows)
    rows = json.loads((out/'attacks12/SUMMARY.json').read_text())
    valid &= len(rows) == 12 and all(r['exit'] != 0 and r['status'] != 'PASS' and not r['secret_leaked'] for r in rows)
    after, snapshot_after = public_hashes(ROOT), public_hashes(snapshot)
    historical_after = packet_hashes(ROOT)
    check_ci_inventory(ROOT)
    valid &= before == after == snapshot_after and historical == historical_after and environment == check_environment()
    valid &= len(identities) == len(set(identities)) == len(nodes)
    return dict(status='PASS' if valid else 'FAIL', qualification='QUALIFIED_OFFLINE_ONLY', source_commit=git('rev-parse', 'HEAD'), git_tree=git('rev-parse', 'HEAD^{tree}'),
                source_snapshot=str(snapshot), source_sha256=before, source_after_sha256=after, snapshot_after_sha256=snapshot_after,
                content_tree_sha256=hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(), historical_sha256=historical,
                historical_integrity=True, environment=environment, inventory_sha256=sha(ROOT/'scripts/required_tests.json'), module_policy_sha256=sha(ROOT/'scripts/test_enrollment.json'),
                distinct_positive=len(set(identities)), repeat_executions=repeats, suites=suites, runs=runs, independent_custody=False)


def main():
    parser = SafeParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--output-dir', type=Path)
    group.add_argument('--list-required', action='store_true')
    args = parser.parse_args()
    if args.list_required:
        try:
            public_hashes(ROOT)
            print(json.dumps(dict(status='INVENTORY_ONLY_NOT_ACCEPTANCE', nodeids=required_nodes(ROOT))))
            return 0
        except Exception:
            print(json.dumps(dict(status='BLOCKED', reason='invalid_inventory_or_source')))
            return 2
    os.umask(0o077)
    out = args.output_dir.resolve()
    if out == ROOT or ROOT in out.parents and not out.is_relative_to(ROOT/'tasks/jarvis-v2-canonical-integration-safety-r2'):
        parser.error('acceptance output must be outside source or inside the new isolated task packet')
    try:
        out.mkdir(parents=True, mode=0o700, exist_ok=False)
    except OSError:
        print(json.dumps(dict(status='BLOCKED', reason='acceptance_output_unavailable')))
        return 2
    try:
        report = acceptance(out)
    except Exception:
        # No raw exception/class/message, private paths or payloads in JSON.
        report = dict(status='BLOCKED', reason='offline_acceptance_preflight_or_evidence_failure', qualification='QUALIFIED_OFFLINE_ONLY')
    with (out/'RESULT.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    (out/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(out))+'\n' for p in sorted(out.rglob('*')) if p.is_file() and p != out/'SHA256SUMS'))
    print(json.dumps({k: report[k] for k in ('status', 'distinct_positive', 'repeat_executions', 'reason') if k in report}))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
