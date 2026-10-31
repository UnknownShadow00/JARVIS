"""Fresh guarded interpreter; reuse a verified read-only target, never bootstrap pip."""
import ast
from datetime import UTC, datetime
import errno
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import socket
import sys
import traceback

report = {'started_at': datetime.now(UTC).isoformat(), 'status': 'NOT_STARTED'}
try:
    expected = json.loads(Path('/input/expected.json').read_text())
    guard = Path('/input/guard_source.py').read_bytes()
    assert hashlib.sha256(guard).hexdigest() == expected['guard_source_sha256']
    nodes = [node for node in ast.parse(guard).body if isinstance(node, ast.FunctionDef) and node.name == 'boundaries']
    assert len(nodes) == 1
    # Reuse only the previous stdlib canary function, not its installer/tests or
    # top-level statements. No candidate is imported before this call returns.
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '/input/guard_source.py', 'exec'), globals())
    report['boundaries_before_imports'] = boundaries(expected)
    assert os.statvfs('/deps').f_flag & os.ST_RDONLY, 'verified target mount must be read-only'
    report['dependency_target_readonly'] = True
    assert not any(name == 'pip' or name.startswith('pip.') for name in sys.modules)
    for name, digest in expected['source_sha256'].items():
        assert hashlib.sha256((Path('/input/source') / name).read_bytes()).hexdigest() == digest
    versions = {dist.metadata['Name'].lower().replace('_', '-'): dist.version for dist in importlib.metadata.distributions(path=['/deps'])}
    assert versions == expected['versions']
    report['target_versions'] = versions
    sys.path.insert(0, '/deps')
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    import pytest
    results = {}

    class Results:
        def pytest_sessionfinish(self, session, exitstatus):
            results.update({'collected': session.testscollected, 'failed': session.testsfailed, 'exitstatus': int(exitstatus)})

    exitcode = pytest.main(['-q', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider',
                            '--basetemp=/work/pytest-temp', '/input/durable_tests.py'], plugins=[Results()])
    report['tests'] = results
    assert exitcode == 0, ('durable fixture tests failed', int(exitcode))
    assert not any(name == 'pip' or name.startswith('pip.') for name in sys.modules)
    assert not any(name == 'app' or name.startswith('app.') for name in sys.modules)
    report['pip_modules'] = []
    report['real_app_modules'] = []
    report['module_origins'] = {name: sys.modules[name].__file__ for name in ['fastapi', 'starlette', 'pydantic', 'pydantic_core', 'apscheduler', 'pytest', 'pytest_asyncio', 'httpx'] if name in sys.modules}
    assert all(origin.startswith('/deps/') for origin in report['module_origins'].values())
    native = sys.modules['pydantic_core._pydantic_core']
    report['native_extension'] = {'origin': native.__file__, 'sha256': hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest()}
    files = sorted(path for path in Path('/work/pytest-temp').rglob('*.json') if path.is_file())
    report['synthetic_store_files'] = [{'path': str(path), 'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in files]
    report['status'] = 'DURABLE_FIXTURE_INTEROPERABILITY_PASSED'
except BaseException as error:
    report.update({'status': 'STOPPED_NO_FALLBACK', 'error_type': type(error).__name__, 'error': str(error), 'traceback': traceback.format_exc(limit=10)})
finally:
    report['finished_at'] = datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('DURABLE_RESULT=' + json.dumps(report, sort_keys=True))
raise SystemExit(0 if report['status'] == 'DURABLE_FIXTURE_INTEROPERABILITY_PASSED' else 2)
