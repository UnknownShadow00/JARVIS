"""Read-only Core metadata supplement. Never imports/runs the auth helper."""
from pathlib import Path
from datetime import datetime, UTC
import collections
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
R = Path('/home/jarvis/JARVIS')
E = Path('/home/jarvis/.hermes-poc/evidence/p7-b2-gate5-post-auth-readback')
G = E.parent / 'p7-b2-gate5-human-auth-handoff'
B = Path('/home/jarvis/.hermes-poc/backups/p7-b2')


def guard(event, args):
    if event in ('socket.connect', 'socket.bind', 'socket.getaddrinfo'):
        raise RuntimeError('NETWORK_FORBIDDEN')
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        p = Path(os.fsdecode(args[0])).absolute()
        private = Path('/home/jarvis/.config/jarvis')
        if p == private or private in p.parents:
            raise RuntimeError('CREDENTIAL_OPEN_FORBIDDEN')
        if (args[2] or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND):
            if E not in p.parents:
                raise RuntimeError('EXTERNAL_WRITE_FORBIDDEN')


sys.addaudithook(guard)


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def meta(p):
    s = p.lstat()
    return dict(inode=s.st_ino, device=s.st_dev, size=s.st_size,
                mtime_ns=s.st_mtime_ns, ctime_ns=s.st_ctime_ns,
                mode=oct(s.st_mode & 0o777), uid=s.st_uid, gid=s.st_gid)


r = {'readback_utc': datetime.now(UTC).isoformat(), 'raw_messages_preserved': False,
     'exact_operator_execution_utc_supplied': False, 'live_probes': 0}
prior = json.loads((G / 'observation-20261010T030924Z.json').read_text())
p = R / 'logs/audit.jsonl'
before = prior['audit']
after = p.stat()
assert after.st_ino == before['inode'] and after.st_size >= before['size']
with p.open('rb') as f:
    f.seek(before['size'])
    data = f.read(1048576)
assert len(data) == after.st_size - before['size']
events = []
for line in data.splitlines():
    v = json.loads(line)
    event = v.get('event_type', '')
    assert re.fullmatch(r'[a-z_]{1,64}', event)
    t = v.get('timestamp')
    if isinstance(t, str):
        datetime.fromisoformat(t.replace('Z', '+00:00'))
    else:
        t = None
    events.append({'event_type': event, 'recorded_timestamp': t})
r['audit_since_preparation'] = {
    'preparation_utc': prior['utc'], 'boundary_size': before['size'],
    'current_size': after.st_size, 'inode': after.st_ino,
    'complete_suffix': True, 'events': events,
    'counts': dict(collections.Counter(e['event_type'] for e in events)),
    'client_address_and_event_payload_excluded': True}

q = subprocess.run(['journalctl', '--user', '-u', 'jarvis.service', '--since',
                    '2026-10-09 21:25:32 UTC', '-o', 'json', '--no-pager'],
                   capture_output=True, text=True)
assert q.returncode == 0
counts = collections.Counter()
correlation = []
total = 0
other = 0
for line in q.stdout.splitlines():
    v = json.loads(line)
    total += 1
    msg = v.get('MESSAGE', '')
    codes = []
    if v.get('SYSLOG_IDENTIFIER') == 'systemd' and 'Started' in msg and 'jarvis.service' in msg:
        codes.append('SYSTEMD_UNIT_STARTED')
    if 'GET /gate5-auth-inspection HTTP/1.1' in msg:
        m = re.search(r'GET /gate5-auth-inspection HTTP/1\.1"\s+(\d{3})\b', msg)
        codes.append('REST_FIXED_PATH_' + (m.group(1) if m else 'STATUS_UNPARSED'))
    if 'WebSocket /ws' in msg and '[accepted]' in msg:
        codes.append('WS_UPGRADE_ACCEPTED')
    for marker, code in [('connection open', 'WS_CONNECTION_OPEN'),
                         ('connection closed', 'WS_CONNECTION_CLOSED'),
                         ('Waiting for application startup', 'WAITING_STARTUP'),
                         ('Uvicorn running on', 'SERVER_LISTENING'),
                         ('Started server process', 'SERVER_PROCESS_START'),
                         ('Application startup complete', 'STARTUP_COMPLETE'),
                         ('Application startup failed', 'STARTUP_FAILED'),
                         ('Traceback', 'TRACEBACK'),
                         ('AUTHENTICATION_MISMATCH', 'AUTHENTICATION_MISMATCH'),
                         ('PILOT_ADMISSION_CLOSED', 'ADMISSION_CLOSED_MARKER')]:
        if marker in msg:
            codes.append(code)
    if int(v.get('PRIORITY', '6')) <= 3:
        codes.append('ERROR_PRIORITY')
    if re.search(r'(?i)(authorization\s*[:=]|bearer\s+[A-Za-z0-9])', msg):
        codes.append('POSSIBLE_SECRET_HEADER_MARKER')
    # These are review markers, not categorical proof of an operational action.
    for marker in ('unload', 'warmup', 'wake', 'generation', 'tool execution',
                   'scheduler dispatch', 'provider submission'):
        if marker in msg.lower():
            codes.append('OPERATION_REVIEW_' + marker.upper().replace(' ', '_'))
    counts.update(codes)
    if not codes:
        other += 1
    if any(c.startswith('REST_FIXED_PATH_') or c.startswith('WS_') for c in codes):
        timestamp = v.get('__REALTIME_TIMESTAMP')
        utc = datetime.fromtimestamp(int(timestamp) / 1000000, UTC).isoformat() if timestamp else None
        correlation.append({'journal_utc': utc, 'categories': codes,
                            'expected_invocation': v.get('_SYSTEMD_INVOCATION_ID') ==
                            '103e420f4f334237a96654048a3edaf4'})
r['journal'] = {'returncode': q.returncode, 'records': total,
                'fixed_marker_counts': dict(counts), 'correlation': correlation,
                'unclassified_records': other,
                'raw_headers_messages_and_exceptions_excluded': True,
                'limits': 'Access metadata is correlation, not credential inspection or packet capture; nonmatching logs do not prove global absence.'}

checks = {}
for name, want in [('HUMAN-ONLY-GATE5-AUTH.py', '437276dda518b6e5f7196d38c1399fbe53df47a40aa0ac79065546f05070ee51'),
                   ('READ-ONLY-PREFLIGHT.py', 'cd836ec3c9df91892365c09b5dfc19e8b64755f032a82f3b112cc1fae07f218b')]:
    p = R / 'tasks/p7-b2-gate5-human-auth-handoff' / name
    checks[name] = {'sha256': sha(p), 'expected_match': sha(p) == want,
                    'executed_by_this_task': False}
r['helper_identities'] = checks
current = json.loads((E / 'continuity-entry.json').read_text())
old = json.loads((E.parent / 'p7-b2-gate5-zero-generation-verification/continuity-final.json').read_text())
r['source_and_distribution_inventory'] = {
    'application_python_inventory_unchanged': current['application_python_inventory'] == old['application_python_inventory'],
    'installed_distribution_names_unchanged': current['installed_distribution_inventory'] == old['installed_distribution_inventory'],
    'limit': 'Distribution directory names, not hashes of every dependency file.'}
r['backup_component_metadata'] = {
    d.name: {p.name: meta(p) for p in sorted(d.iterdir()) if p.is_file()}
    for d in (B / 'baseline-5244a125c27e41bb844781032d4f59ff', B / '9315a199492449709dfd6bd51b2666a5')}
r['runtime_metadata'] = {
    str(d.relative_to(R)): {p.name: meta(p) for p in sorted(d.iterdir()) if p.is_file()}
    for d in (R / 'data/model-ownership-v1', R / 'data/p7-b2-pilot-controller-v1')}
r['D06_marker_sha256'] = sha(R / 'data/model-ownership-v1.managed')
r['D06_scope_sha256'] = sha(R / 'data/model-ownership-v1/scope.json')
r['D06_state_sha256'] = sha(R / 'data/model-ownership-v1/state.json')
r['D06_matches_startup_components'] = all(
    r[key] == current['startup_validation']['manifest']['files'][member]
    for key, member in [('D06_marker_sha256', 'ownership.managed'),
                        ('D06_scope_sha256', 'scope.json'), ('D06_state_sha256', 'state.json')])
r['live_controller_sha256'] = sha(R / 'data/p7-b2-pilot-controller-v1/controller.sqlite3')
r['live_controller_matches_startup'] = (r['live_controller_sha256'] ==
    current['startup_validation']['manifest']['files']['controller.sqlite3'])
r['physical_controller_comparison_limit'] = ('The SQLite backup is a separate physical database; byte equality is not required. Exact schema/epoch/count associations and unchanged live-file metadata establish continuity.')
previous_stores = json.loads((E.parent / 'p7-b2-gate5-zero-generation-verification/runtime-store-metadata-final.json').read_text())['files']
r['prior_runtime_metadata_comparison'] = {}
for name, expected in previous_stores.items():
    actual = meta(R / name)
    r['prior_runtime_metadata_comparison'][name] = {
        'unchanged': all(actual[k] == v for k, v in expected.items()),
        'expected_no_message_audit_append': name == 'logs/audit.jsonl',
        'actual': actual}
units = subprocess.check_output(['systemctl', '--user', 'list-units', '--all', '--plain', '--no-legend', '--no-pager'], text=True)
relevant = []
for line in units.splitlines():
    fields = line.split()
    if fields and any(k in fields[0].lower() for k in ('jarvis', 'hermes', 'ollama', 'wake')):
        relevant.append(fields[:4])
r['core_lifecycle_unit_metadata'] = relevant
r['startup_flags_and_children_basis'] = 'Source-bound registration suppression, startup audit flags false, no service children; unprivileged metadata cannot exclude arbitrary privileged/private actors.'
r['remote_AI_host'] = {'fresh_identity_verified': False, 'fresh_Ollama_counters_verified': False,
                       'basis': 'Reviewed sealed Gate5B AI-HOST-KEY-VERIFICATION.md; no trust bypass, new key acceptance or remote model interaction.'}
(E / 'minimized-readback.json').write_text(json.dumps(r, indent=2) + '\n')
print(json.dumps(r, indent=2))
