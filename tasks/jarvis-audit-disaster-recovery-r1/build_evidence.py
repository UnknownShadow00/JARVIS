#!/usr/bin/env python3
"""Assemble source-bound development evidence; never import application code."""
from pathlib import Path
from datetime import UTC, datetime
import difflib
import hashlib
import json
import shutil

PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(name, value):
    (PACKET / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def main():
    baseline = json.loads((PACKET / 'BASELINE.json').read_text())
    runs = []
    for directory in sorted((PACKET / 'runs').iterdir()):
        result = json.loads((directory / 'RUN.json').read_text())
        runs.append((directory, result))
    def latest(status):
        return next((d, r) for d, r in reversed(runs)
                    if r['status'] == 'PASS' and r['child']['status'] == status)
    core, c = latest('CORE_PASS')
    app, a = latest('FULL_EXISTING_APP_OFFLINE_LIFESPAN_PASS')
    bench, b = latest('BENCHMARK_PASS')
    assert c['child']['tests'] == dict(collected=254, failed=0, skipped=0, exitstatus=0)
    assert a['child']['regressions'] == dict(collected=54, failed=0, skipped=0, exitstatus=0)
    assert len(a['child']['cases']) == 11 and len(a['child']['native_execution']) == 3
    assert c['source_sha256'] == a['source_sha256'] == b['source_sha256']
    assert len(c['source_sha256']) == 97
    for name, expected in c['source_sha256'].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in baseline['prior_seals'].items():
        assert sha(ROOT / 'tasks' / name / 'SHA256SUMS') == expected, name
    log = (ROOT / 'tasks/loop-log.md').read_bytes()
    assert hashlib.sha256(log[:baseline['log_prefix_bytes']]).hexdigest() == baseline['log_prefix_sha256']
    changed = [name for name, old in baseline['source_sha256'].items() if sha(ROOT / name) != old]
    added = ['app/agent/checkpoint_epochs.py', 'app/agent/archive_restore.py',
             'app/agent/audit_attestations.py', 'app/agent/ledger_schema.py',
             'tests/test_audit_disaster.py', 'tests/audit_process_actor.py',
             'tests/test_audit_disaster_app.py', 'docs/audit_disaster_recovery.md']
    files = sorted(changed + added)
    patch = []
    for name in files:
        destination = PACKET / 'source' / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, destination)
        old = (PACKET / 'before' / name).read_text() if name in changed else ''
        patch.extend(difflib.unified_diff(old.splitlines(True), (ROOT / name).read_text().splitlines(True),
                                       fromfile='before/' + name if name in changed else '/dev/null', tofile='after/' + name))
    (PACKET / 'SOURCE.patch').write_text(''.join(patch))
    write('CHANGES.json', {'baseline': 'BASELINE.json', 'modified': sorted(changed), 'added': sorted(added),
                           'scope': 'Against captured actual starting files, preserving earlier uncommitted sprint changes; not against git HEAD.'})
    all_sources = dict(c['source_sha256'])
    for name in files:
        all_sources[name] = sha(ROOT / name)
    for name in ['run_checks.py', 'child.py', 'focused_child.py', 'full_app_child.py',
                 'benchmark_child.py', 'benchmark_workload.py', 'build_evidence.py']:
        all_sources[str((PACKET / name).relative_to(ROOT))] = sha(PACKET / name)
    for source in (PACKET / 'tests').rglob('*.py'):
        all_sources[str(source.relative_to(ROOT))] = sha(source)
    for source in sorted((core / 'input/tests').glob('*.py')):
        actual = ROOT / 'tests' / source.name
        if actual.is_file():
            assert sha(source) == sha(actual)
            all_sources[str(actual.relative_to(ROOT))] = sha(actual)
    for source in sorted((app / 'input/regressions').glob('*.py')):
        actual = ROOT / 'tests' / source.name
        if actual.is_file():
            assert sha(source) == sha(actual)
            all_sources[str(actual.relative_to(ROOT))] = sha(actual)
    write('SOURCE-SHA256.json', all_sources)
    shutil.copyfile(app / 'output/DISASTER-DEMONSTRATION.json', PACKET / 'DISASTER-DEMONSTRATION.json')
    shutil.copyfile(app / 'output/DEMONSTRATION.json', PACKET / 'EXECUTION-DEMONSTRATION.json')
    shutil.copyfile(app / 'output/OPERATOR-DEMONSTRATION.json', PACKET / 'OPERATOR-DEMONSTRATION.json')
    shutil.copyfile(bench / 'output/BENCHMARKS.json', PACKET / 'BENCHMARKS.json')
    benchmarks = json.loads((PACKET / 'BENCHMARKS.json').read_text())
    assert len(benchmarks['samples']) == 4
    assert all(x['uncertain_reexecution_count'] == 0 for x in benchmarks['samples'])
    processes = []
    for command in sorted((core / 'output/pytest').glob('test_independent_sigkill_disas*/case/command.json')):
        config = json.loads(command.read_text())
        processes.append({'mode': config['mode'], 'stage': config['stage'],
                          'artifacts': str(command.parent.relative_to(PACKET)), 'result': 'PASS'})
    assert len(processes) == 15
    write('CRASH-RECOVERY.json', {
        'new_independent_SIGKILL_cases': processes,
        'core_process_cases_including_prior_regressions': 40,
        'additional_actual_app_process_crash_scenario': 1,
        'simulation_scope': 'Real independent processes killed at instrumented boundaries; fsync/SQLite process crash evidence, not physical power-loss qualification.',
        'behavior': {'unprepared_restore': 'preserved_manual_quarantine_no_reconstruction',
                     'prepared_restore': 'verified_existing_artifact_then_no_replace_publication',
                     'rollover_without_link': 'refuses_startup_explicit_bound_operator_admission',
                     'rollover_with_link': 'authenticated_unique_transition_continuation',
                     'recovery_grant_expiry': 'same_durable_admission_only_no_new_authorization',
                     'export_without_attestation': 'restore_refused_until_audited_reconciliation'}})
    summaries = []
    for directory, result in runs:
        summaries.append({'run': directory.name, 'status': result['status'],
                          'child_status': result['child']['status'],
                          'tests': result['child'].get('tests', result['child'].get('regressions')),
                          'guard_stop': result['guard_stop']})
    write('RESULTS.json', {
        'at': datetime.now(UTC).isoformat(), 'status': 'PASS',
        'final_runs': {'core': core.name, 'full_app': app.name, 'benchmark': bench.name},
        'pytest': {'passed': 308, 'failed': 0, 'skipped': 0, 'core': 254, 'application_regressions': 54,
                   'new_sprint_cases': 63, 'prior_cases_rerun': 245},
        'additional_checks': {'application_scenario_groups': 11, 'native_probes': 3, 'benchmark_cases': 4},
        'same_application_sources': 97, 'all_runs': summaries,
        'full_repository_suite_claimed': False, 'live_qualification_claimed': False,
        'prior_seals_unchanged': baseline['prior_seals'], 'completion_log_original_prefix_preserved': True,
        'warnings': {'upstream_deprecations': 2, 'expected_synthetic_startup_lines': 21},
        'resources': {mode: {k: r[k] for k in ['elapsed_seconds', 'peak_observed_rss', 'peak_observed_files',
                        'peak_observed_bytes', 'peak_owned_processes_including_bwrap', 'guard_stop', 'limits']}
                      for mode, r in [('core', c), ('full_app', a), ('benchmark', b)]}})
    rows = []
    for x in benchmarks['samples']:
        ms = lambda value: f'{value * 1000:.3f}' if value is not None else 'not sampled'
        rows.append('| ' + ' | '.join([x['case'], str(x['tasks']), str(x['checkpoint_head_before_restart']['sequence']),
                      str(x['generations']), ms(x['verification_uncached']['median_seconds']),
                      ms(x['verification_cached']['median_seconds']), ms(x['checkpoint_commit_median_seconds']),
                      ms(x['rollover_commit_median_seconds']), ms(x['export_seconds']), ms(x['restore_seconds']),
                      ms(x['startup_seconds'])]) + ' |')
    (PACKET / 'PERFORMANCE.md').write_text('''# Bounded synthetic performance evidence

Final run: `runs/''' + bench.name + '''/RUN.json`. Raw samples, storage, memory,
query/reconciliation times and logical throughput: [BENCHMARKS.json](BENCHMARKS.json).
Same 97 application hashes as final core and full-app runs. Four sequential cases;
unchanged 120s wall/768MiB aggregate/1GiB per-process limits. No network or service.

| Case | Tasks | Checkpoint sequence | Generations | Verify uncached ms | Verify cached ms | Commit median ms | Rollover commit median ms | Export ms | Restore ms | Startup ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
''' + '\n'.join(rows) + '''

Three warmed verification/query samples per case. Uncached refers to disabled
decode/HMAC memoization, not a physically cold filesystem. The cache still reads,
hashes and validates every file and hashes complete logical SQLite state. Returned
values are copied. The 2048-entry cache is bounded. Tampering after cache warmup
is independently tested. Checkpoint commit measurements include transaction,
intent/final durability; rollover samples include generation transition overhead.

State scaling uses one synthetic batch of held historical fixtures under a fenced
mutation; the normal max_pending=128 gate is unchanged. One real synthetic UNKNOWN
operation is created before the batch and retained across restore/startup/reconcile.
History scaling uses 256 individually checkpointed control mutations. No fabricated
completed task, automatic retry or migration of real state occurs. The first
benchmark fixture incorrectly tried to admit after the held batch; conservative
queue-capacity refusal stopped it. Reordering fixture setup fixed it without
raising capacity. That failed run is retained.

The longest history shows the measured HMAC/JSON cache benefit, but verification
and protected queries still scan all history/state. Raw SQL component timings
are included to show this cost, not proposed as a bypass. RSS is a cumulative
process maximum; apparent and allocated storage are separately reported. Run
aggregate RSS includes supervisors. No production SLO, million-row throughput,
cold-cache, power-loss or unbounded retention claim is made.
''')
    print(json.dumps({'final_runs': [core.name, app.name, bench.name], 'changed_files': len(files),
                      'source_hashes': len(all_sources), 'new_SIGKILL_cases': len(processes)}))

if __name__ == '__main__':
    main()
