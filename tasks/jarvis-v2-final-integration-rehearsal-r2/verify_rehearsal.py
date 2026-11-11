"""Read-only verification of exact-source rehearsal evidence; never updates authority.

Run from any directory. Optional output must be a NEW file outside prior evidence.
Trusted local interpreter, Git objects, dependencies and custody remain prerequisites.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys

SOURCE = 'da67d936566d330fad02fa8f23f8e1be2d4b80ad'
INVENTORY = 'bc7359fc23710f82d780943e15c10a45d4df53380884c84c92699c3bc6139f15'
POLICY = '287ab432aa03ac8750a6c58257627077c097e80f98794eaf25c058d6acbdcd1f'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEPS = Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages')
MODES = dict(coverage=217, reconciliation=66, r3=19, r2=45, original=32, existing=507)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def identities(nodes):
    counters, result = {}, {}
    for node in nodes:
        base = node.split('[', 1)[0]
        n = counters.get(base, 0)
        counters[base] = n + 1
        ident = hashlib.sha256((base + '#' + str(n)).encode()).hexdigest()
        assert ident not in result
        result[ident] = node
    return result


def verify():
    a = HERE / 'acceptance'
    result = json.loads((a / 'RESULT.json').read_text())
    assert result['status'] == 'PASS' and result['source_commit'] == SOURCE
    assert result['git_tree'] == git('rev-parse', SOURCE + '^{tree}')
    expected = result['source_sha256']
    assert len(expected) == 266
    snapshot = Path(result['source_snapshot'])
    assert expected == result['source_after_sha256'] == result['snapshot_after_sha256']
    for name, value in expected.items():
        assert digest(ROOT / name) == digest(snapshot / name) == value
        assert hashlib.sha256(subprocess.check_output(['git', 'show', SOURCE + ':' + name], cwd=ROOT)).hexdigest() == value
        assert not (snapshot / name).stat().st_mode & 0o222
    assert not snapshot.stat().st_mode & 0o222
    assert all(not p.stat().st_mode & 0o222 for p in snapshot.rglob('*') if p.is_dir())
    assert digest(ROOT / 'scripts/required_tests.json') == INVENTORY
    assert digest(ROOT / 'scripts/test_enrollment.json') == POLICY
    inventory = json.loads((ROOT / 'scripts/required_tests.json').read_text())
    policy = json.loads((ROOT / 'scripts/test_enrollment.json').read_text())['modules']
    actual = {str(p.relative_to(ROOT)) for p in (ROOT / 'tests').rglob('*.py') if '__pycache__' not in p.parts}
    assert actual == set(policy)
    dispositions = dict(collections.Counter(e['disposition'] for e in policy.values()))
    assert dispositions == dict(required=67, support=17, negative_fixture=2, excluded_offline_scope=39, excluded_live_or_hardware=11)
    for name, entry in policy.items():
        assert entry['reason'] and digest(ROOT / name) == entry['sha256']
    nodeids, passed_ids, suite_results = set(), set(), []
    completed = {}
    for name, count in MODES.items():
        mode = 'new' if name == 'original' else name
        suite = inventory['suites'][mode]
        assert suite['nodeids'] == sorted(set(suite['nodeids']))
        assert len(suite['nodeids']) == count
        assert not nodeids.intersection(suite['nodeids'])
        nodeids.update(suite['nodeids'])
        for path, sha in suite['sources'].items():
            assert digest(ROOT / path) == sha
        required = identities(suite['nodeids'])
        for suffix in ('', '-seed42') if name != 'existing' else ('',):
            body = json.loads((a / (name + suffix + '.json')).read_text())
            seen = [s['id'] for s in body['scenarios']]
            assert len(seen) == len(set(seen)) == count and set(seen) == set(required)
            assert body['status'] == 'PASS' and body['gate_exit_code'] == body['child_exit_code'] == 0
            assert body['required_count'] == body['collected'] == body['executed'] == count
            assert body['required_missing'] == body['unexpected_collected'] == 0
            assert body['collection'] == dict(skipped=0, deselected=0)
            assert body['counts'] == dict(PASS=count, FAIL=0, ERROR=0, SKIP=0, INCOMPLETE=0)
            assert body['seed'] == (42 if suffix else 16401)
            session = body['session']
            assert all(session[k] for k in ('started', 'collected', 'finished'))
            assert not any(session[k] for k in ('interrupted', 'internal_error', 'collection_error', 'unexpected_report'))
            assert session['pytest_exit_code'] == 0 and session['collected_count'] == count
            for s in body['scenarios']:
                assert s['complete'] and not s['timed_out'] and s['status'] == 'PASS'
                assert [p['phase'] for p in s['phases']] == ['setup', 'call', 'teardown']
                assert all(p['outcome'] == 'passed' for p in s['phases'])
            if not suffix:
                assert not passed_ids.intersection(seen)
                passed_ids.update(seen)
                completed[name] = [{'nodeid': required[s['id']], 'evidence_id': s['id'], 'status': s['status']} for s in body['scenarios']]
                suite_results.append(dict(suite=name, counts=body['counts'], gate_exit=0, child_exit=0, missing=0, unexpected=0))
    assert len(nodeids) == len(passed_ids) == result['distinct_positive'] == 886
    assert {n.split('::')[0] for n in nodeids} == {n for n, e in policy.items() if e['disposition'] == 'required'}
    assert result['repeat_executions'] == 379
    assert len(result['runs']) == 14 and all(r['exit'] == 0 for r in result['runs'])
    contracts = {}
    for name, n, key in [('gate22', 22, 'contract_pass'), ('adversaries11', 11, 'passed')]:
        rows = json.loads((a / name / 'SUMMARY.json').read_text())
        assert len(rows) == n and all(r[key] for r in rows)
        contracts[name] = n
    rows = json.loads((a / 'negative14/SUMMARY.json').read_text())['checks']
    assert len(rows) == 14 and all(r['status'] == 'PASS' and r['gate_status'] != 'PASS' and r['gate_exit'] != 0 for r in rows)
    contracts['negative14'] = 14
    rows = json.loads((HERE / 'audit-attacks12/SUMMARY.json').read_text())
    assert len(rows) == 12 and all(r['exit'] != 0 and r['status'] != 'PASS' and not r['secret_leaked'] for r in rows)
    assert json.loads((HERE / 'AUDIT-ATTACK-EXECUTION.json').read_text())['exit'] == 0
    contracts['audit_attacks_replayed'] = 12
    verified_hashes = 0
    for line in (a / 'SHA256SUMS').read_text().splitlines():
        sha, name = line.split('  ', 1)
        assert digest(a / name) == sha
        verified_hashes += 1
    before = json.loads((a / 'gate22/before-astra.json').read_text())
    after = json.loads((a / 'gate22/astra.json').read_text())
    assert before['status'] == 'PASS' and before['gate_exit_code'] == 0 and before['executed'] == 31 and before['counts']['SKIP'] == 0
    assert after['status'] == 'FAIL' and after['gate_exit_code'] == 1 and after['child_exit_code'] == 0
    assert after['executed'] == 31 and after['required_count'] == 45 and after['required_missing'] == 14
    mapping = identities(inventory['suites']['r2']['nodeids'])
    missing = sorted(set(mapping) - {s['id'] for s in after['scenarios']})
    assert len(missing) == 14
    assert not git('diff', '--name-only', 'b0c8865a', SOURCE, '--', 'app')
    assert all(p.startswith('tasks/jarvis-v2-final-integration-rehearsal-r2/') for p in git('diff', '--name-only', SOURCE, 'HEAD').splitlines())
    outputs = [p for p in a.rglob('*') if p.is_file()]
    assert a.stat().st_mode & 0o077 == 0 and all(p.stat().st_mode & 0o077 == 0 for p in outputs)
    distributions = sorted([dict(name=d.metadata['Name'], version=d.version) for d in importlib.metadata.distributions(path=[str(DEPS)])], key=lambda d: d['name'].lower())
    versions = {d['name'].lower(): d['version'] for d in distributions}
    assert versions['apscheduler'] == '3.11.3'
    real_scheduler = [n for n in nodeids if n.startswith('tests/test_scheduler_hardening_r2.py::')]
    return dict(status='PASS', source_commit=SOURCE, artifact_head=git('rev-parse', 'HEAD'), source_tree=result['git_tree'], content_tree_sha256=result['content_tree_sha256'], inputs_verified=266, distinct_passes=886, repeat_passes=379, failures=0, errors=0, skips=0, incomplete=0, required_missing=0, suites=suite_results, contracts=contracts, enrollment=dispositions, test_python_files=len(actual), executed=completed, missing_astra_nodeids=[mapping[i] for i in missing], real_scheduler_tests=real_scheduler, required_inventory_sha256=INVENTORY, module_policy_sha256=POLICY, acceptance_hashes_verified=verified_hashes, snapshot=snapshot.as_posix(), readonly_snapshot=True, protected_local_output=True, independent_custody=False, dependencies=distributions, environment=dict(python=sys.version, kernel=platform.release(), platform=platform.platform(), git=git('--version'), bwrap=subprocess.check_output(['/usr/bin/bwrap','--version'], text=True).strip()), qualification='OFFLINE_REHEARSAL_ONLY')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    evidence = verify()
    if args.output:
        with args.output.open('x') as stream:
            json.dump(evidence, stream, indent=2)
            stream.write('\n')
    print(json.dumps({k:v for k,v in evidence.items() if k not in ('executed', 'dependencies', 'missing_astra_nodeids', 'real_scheduler_tests', 'suites')}))
