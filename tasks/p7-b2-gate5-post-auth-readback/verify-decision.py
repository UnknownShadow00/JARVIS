"""Validate collected, secret-free readbacks and prior immutable seals."""
from pathlib import Path
from datetime import datetime, UTC
import hashlib
import json

E = Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate5-post-auth-readback')
B = Path('/home/jarvis/.hermes-poc/backups/p7-b2')


def load(p):
    return json.loads(p.read_text())


def seal(p):
    result = {}
    for line in (p / 'SHA256SUMS').read_text().splitlines():
        h, n = line.split(None, 1)
        q = p / n.lstrip('*')
        assert q.parent == p
        result[q.name] = hashlib.sha256(q.read_bytes()).hexdigest() == h
    return result


states = [load(p) for p in sorted(E.glob('observation-*.json'))]
first, last = states[0], states[-1]
c = load(E / 'continuity-final.json')
v = load(E / 'minimized-readback.json')
guards = load(E / 'focused-post-auth-guard.json')
prior = load(E / 'prior-seals.json')
prior_checks = {}
for name, expected in prior.items():
    p = E.parent / name
    members = seal(p)
    prior_checks[name] = {'members': members, 'seal_sha256': hashlib.sha256((p / 'SHA256SUMS').read_bytes()).hexdigest()}
    assert all(members.values()) and prior_checks[name]['seal_sha256'] == expected['digest']
baseline_seal = seal(B / 'baseline-5244a125c27e41bb844781032d4f59ff')
assert all(baseline_seal.values())
checks = {
    'human_positive_attestation_recorded': load(E / 'human-attestation.json')['reported_WS'] == 'PASS_101_CLOSE_1000',
    'helper_and_preflight_identities': all(x['expected_match'] for x in v['helper_identities'].values()),
    'identity_and_source_state_clean': all(not x['violations'] and not x['limitations'] for x in states),
    'same_service_invocation': first['service'] == last['service'],
    'same_unit_hashes_and_credential_metadata': first['unit_files'] == last['unit_files'] and first['credential_metadata'] == last['credential_metadata'] and last['credential_metadata_matches_gate4'],
    'source_bound_closed_admission': last['admission']['state'] == 'PILOT_ADMISSION_CLOSED' and not last['source_mismatches'],
    'D09_schema_context_integrity': c['live_database_validation']['schema_exact'] and c['live_database_validation']['context_exact'] and c['live_database_validation']['integrity_check'] == [['ok']] and not c['live_database_validation']['foreign_key_check'] and not c['live_database_validation']['unexpected_views_triggers_indexes'],
    'D09_single_expected_epoch_zero_counts': last['D09']['epochs'] == [['606a991a06b74fd79ed72b308417cc3f', 'OPEN', 1]] and all(n == 0 for k, n in last['D09']['table_counts'].items() if k not in ('epochs', 'pilot_context')),
    'D04_zero_receipts': last['D04']['receipt_count'] == 0 and not last['D04']['namespace_exists'],
    'D06_clean_exact_startup_binding': last['D06']['state'] == {'version': 1, 'current': None, 'last': None} and v['D06_matches_startup_components'] and not c['D06_lock_metadata']['matching_kernel_locks'],
    'startup_checkpoint_baseline_valid': c['startup_validation']['authoritative_readonly_validator'] == 'PASS' and c['startup_validation']['creation_order_valid'] and c['startup_validation']['baseline_all_source_hashes_match'] and c['startup_validation']['checkpoint_implementation_hashes_match'] and all(x['expected_manifest_match'] and all(x['components'].values()) for x in last['backups'].values()),
    'audit_only_expected_pair_since_preparation': v['audit_since_preparation']['counts'] == {'ws_connect': 1, 'ws_disconnect': 1} and v['audit_since_preparation']['complete_suffix'],
    'REST_and_WS_positive_journal_correlation': v['journal']['fixed_marker_counts'].get('REST_FIXED_PATH_404') == 1 and v['journal']['fixed_marker_counts'].get('WS_UPGRADE_ACCEPTED') == 1 and all(x['expected_invocation'] for x in v['journal']['correlation']),
    'no_unexpected_journal_category': v['journal']['unclassified_records'] == 0 and not any(k in v['journal']['fixed_marker_counts'] for k in ('AUTHENTICATION_MISMATCH', 'ERROR_PRIORITY', 'TRACEBACK', 'STARTUP_FAILED', 'POSSIBLE_SECRET_HEADER_MARKER')) and not any(k.startswith('OPERATION_REVIEW_') for k in v['journal']['fixed_marker_counts']),
    'runtime_provenance_ownership_controller_unchanged': all(x['unchanged'] for name, x in v['prior_runtime_metadata_comparison'].items() if name != 'logs/audit.jsonl'),
    'no_added_app_module_or_distribution_name': all(v['source_and_distribution_inventory'][k] for k in ('application_python_inventory_unchanged', 'installed_distribution_names_unchanged')),
    'offline_477_passed': '477 passed, 2 warnings' in (E / 'focused-post-auth.txt').read_text(),
    'offline_guards_zero_forbidden_activity': all(n == 0 for g in guards.values() for k, n in g['counts'].items() if k != 'approved_offline_children'),
    'no_Codex_live_probes': all(x['http_ws_probes'] == 0 and x['task_provider_requests'] == 0 for x in states),
}
assert all(checks.values()), {k: v for k, v in checks.items() if not v}
# Review result artifacts only; source files deliberately contain symbolic header
# APIs and dummy credentials, so source text is not mistaken for captured values.
result_files = [p for p in E.iterdir() if p.suffix in ('.json', '.txt') and 'source-manifest' not in p.name]
leak_markers = {}
for p in result_files:
    text = p.read_text()
    leak_markers[p.name] = any(marker in text for marker in ('Authorization: Bearer ', '"authorization":', '"Authorization":', '"request_headers":', '"raw_provider_response":'))
assert not any(leak_markers.values())
r = {'utc': datetime.now(UTC).isoformat(), 'mandatory_closed_state_requirements': checks,
     'decision': 'JARVIS P7 GATE 5 — COMPLETE, ZERO-GENERATION VERIFIED',
     'prior_seals_reverified': prior_checks, 'baseline_checksum_members': baseline_seal,
     'post_probe_snapshot_window': {'first_utc': first['utc'], 'last_utc': last['utc'], 'samples': len(states)},
     'source_review_and_result_artifact_structural_leakage_check': {'captured_sensitive_header_or_raw_provider_markers': leak_markers, 'real_token_value_comparison': 'NOT_PERFORMED_TOKEN_NEVER_ACCESSED'},
     'AI_host_fresh_identity_and_Ollama_counters': {'verified': False, 'classification': 'SEPARATE_EXTERNAL_PREREQUISITE_BEFORE_GATE6', 'reason': 'Approved sealed Gate4 Gate5 requirements concern no-message authentication and source-bound CLOSED JARVIS state. Observable-metadata limits remain explicit; no remote/global stability PASS is asserted.'},
     'Gate6_authorized': False, 'measurement_started': False}
(E / 'decision-checks.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps({'decision': r['decision'], 'checks': checks, 'window': r['post_probe_snapshot_window']}, indent=2))
