"""Structured evidence validation. No target imports, exception text or payloads."""
import hashlib
import math

VERSION = 2
PHASES = ('setup', 'call', 'teardown')
CATEGORIES = frozenset({'assertion', 'timeout', 'storage', 'import', 'runtime', 'other'})


class InvalidEvidence(ValueError):
    def __init__(self, code='invalid_completion_evidence'):
        super().__init__(code)
        self.code = code


def case_id(nodeid):
    return hashlib.sha256(nodeid.encode()).hexdigest()


def case_identifiers(nodeids):
    # Parameter values can contain secrets. Hash only trusted source test names
    # and their collection ordinal, never the parameter text itself.
    counters, identities = {}, {}
    for nodeid in nodeids:
        base = nodeid.split('[', 1)[0]
        ordinal = counters.get(base, 0)
        counters[base] = ordinal + 1
        identities[nodeid] = case_id(base + '#' + str(ordinal))
    return identities


def category(exception):
    # Never serialize the exception, its dynamic class name, or its attributes.
    for kind, label in ((AssertionError, 'assertion'), (TimeoutError, 'timeout'),
                        (OSError, 'storage'), (ImportError, 'import'), (RuntimeError, 'runtime')):
        if isinstance(exception, kind):
            return label
    return 'other'


def validate(report, *, run_id, seed, mode, returncode, required=None):
    def require(condition, code='invalid_completion_evidence'):
        if not condition:
            raise InvalidEvidence(code)
    collection = None
    if required is not None:
        require(type(report) is dict and 'collection' in report)
        report = dict(report)
        collection = report.pop('collection')
        require(type(collection) is dict and set(collection) == {'skipped', 'deselected'})
        require(all(type(v) is int and v >= 0 for v in collection.values()))
        required = list(required)
        require(len(set(required)) == len(required))
    require(type(report) is dict and set(report) == {'protocol', 'run_id', 'seed', 'mode', 'session', 'expected', 'scenarios', 'completion'})
    require(type(report['seed']) is int and type(report['mode']) is str and type(report['run_id']) is str)
    require(type(report['protocol']) is int and report['protocol'] == VERSION and report['run_id'] == run_id and report['seed'] == seed and report['mode'] == mode)
    require(report['completion'] == 'pytest-returned-v2')
    expected, session, scenarios = report['expected'], report['session'], report['scenarios']
    require(type(expected) is list and all(type(i) is str and len(i) == 64 and set(i) <= set('0123456789abcdef') for i in expected))
    require(len(set(expected)) == len(expected))
    require(type(session) is dict and set(session) == {'started', 'collected', 'finished', 'interrupted', 'internal_error', 'collection_error', 'unexpected_report', 'pytest_exit_code', 'collected_count'})
    require(all(type(session[k]) is bool for k in session if k not in {'pytest_exit_code', 'collected_count'}))
    require(type(session['pytest_exit_code']) is int and 0 <= session['pytest_exit_code'] <= 5)
    require(type(session['collected_count']) is int and session['collected_count'] == len(expected), 'mismatched_test_count')
    require(type(scenarios) is list and len(scenarios) == len(expected), 'mismatched_test_count')
    normalized = []
    for i, scenario in enumerate(scenarios):
        require(type(scenario) is dict and set(scenario) == {'id', 'phases', 'timed_out'})
        require(scenario['id'] == expected[i] and type(scenario['timed_out']) is bool)
        phases = scenario['phases']
        require(type(phases) is list and len(phases) <= 3)
        for phase in phases:
            require(type(phase) is dict and set(phase) == {'phase', 'outcome', 'duration_seconds', 'category'})
            require(phase['phase'] in PHASES and phase['outcome'] in {'passed', 'failed', 'skipped'})
            require(type(phase['duration_seconds']) in (float, int) and 0 <= phase['duration_seconds'] <= 600 and math.isfinite(phase['duration_seconds']))
            require(phase['category'] is None or type(phase['category']) is str and phase['category'] in CATEGORIES)
        names = [phase['phase'] for phase in phases]
        require(len(names) == len(set(names)) and names == sorted(names, key=PHASES.index))
        complete = names == list(PHASES)
        failed = [phase for phase in phases if phase['outcome'] == 'failed']
        skipped = any(phase['outcome'] == 'skipped' for phase in phases)
        if scenario['timed_out']:
            status = 'FAIL'
        elif failed:
            status = 'ERROR' if any(phase['phase'] != 'call' for phase in failed) else 'FAIL'
        elif skipped:
            status = 'SKIP'
        elif not complete:
            status = 'INCOMPLETE'
        else:
            status = 'PASS'
        normalized.append(dict(id=scenario['id'], status=status, phases=phases,
                               complete=complete, timed_out=scenario['timed_out'],
                               duration_seconds=sum(phase['duration_seconds'] for phase in phases)))
    counts = {status: sum(s['status'] == status for s in normalized) for status in ('PASS', 'FAIL', 'ERROR', 'SKIP', 'INCOMPLETE')}
    success = bool(expected) and returncode == 0 and session['pytest_exit_code'] == 0 and all(session[k] for k in ('started', 'collected', 'finished')) and not any(session[k] for k in ('interrupted', 'internal_error', 'collection_error', 'unexpected_report')) and counts['PASS'] == len(expected)
    missing = len(set(required or ()) - set(expected))
    unexpected = len(set(expected) - set(required or ())) if required is not None else 0
    if required is not None and (missing or unexpected or any(collection.values())):
        success = False
    reason = 'required_collection_mismatch' if required is not None and (missing or unexpected or any(collection.values())) else 'complete' if success else 'no_tests_collected' if not expected else 'incomplete_test_phases' if counts['INCOMPLETE'] else 'verification_failed'
    return dict(required_missing=missing, unexpected_collected=unexpected, collection=collection, reason=reason, protocol=VERSION, mode=mode, seed=seed, session=session, collected=len(expected),
                attempted=sum(bool(s['phases']) for s in normalized),
                executed=sum(s['complete'] for s in normalized), scenarios=normalized, counts=counts,
                timed_out=any(s['timed_out'] for s in normalized), status='PASS' if success else 'FAIL',
                gate_exit_code=0 if success else 1)
