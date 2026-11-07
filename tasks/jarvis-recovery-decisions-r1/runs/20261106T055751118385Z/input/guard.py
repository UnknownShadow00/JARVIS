"""Guarded conditional installer/framework child. Never import the real application."""
import ast
from datetime import UTC, datetime
import errno
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import runpy
import socket
import sys
import traceback

report = {'started_at': datetime.now(UTC).isoformat(), 'status': 'NOT_STARTED', 'stages': []}


def inventory():
    files = [p for p in Path('/work').rglob('*') if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    assert len(files) <= 100000 and total <= 2 * 1024**3, 'workspace bound exceeded'
    return {'files': len(files), 'bytes': total}


def boundaries(expected):
    result = {}
    for name, parent in expected['parent_namespaces'].items():
        actual = os.readlink('/proc/self/ns/' + name)
        assert actual != parent, ('namespace not isolated', name)
        result[name + '_namespace'] = actual
    status = dict(line.split(':', 1) for line in Path('/proc/self/status').read_text().splitlines() if ':' in line)
    assert int(status['CapEff'].strip(), 16) == 0 and status['NoNewPrivs'].strip() == '1'
    result['cap_eff'], result['no_new_privs'] = status['CapEff'].strip(), status['NoNewPrivs'].strip()
    assert resource.getrlimit(resource.RLIMIT_AS) == (1073741824, 1073741824)
    assert resource.getrlimit(resource.RLIMIT_CPU) == (120, 121)
    assert resource.getrlimit(resource.RLIMIT_FSIZE) == (67108864, 67108864)
    assert resource.getrlimit(resource.RLIMIT_NOFILE) == (64, 64)
    assert resource.getrlimit(resource.RLIMIT_CORE) == (0, 0)
    assert hashlib.sha256(Path('/input/readonly-canary.txt').read_bytes()).hexdigest() == expected['readable_canary_sha256']
    for path, flags in [('/input/readonly-canary.txt', os.O_WRONLY), (expected['outside_canary_path'], os.O_RDONLY)]:
        try:
            descriptor = os.open(path, flags)
        except OSError as error:
            assert error.errno in {errno.EROFS, errno.EACCES, errno.EPERM, errno.ENOENT}
            result[path] = error.errno
        else:
            os.close(descriptor)
            raise AssertionError('filesystem deny boundary failed')
    fds = {}
    for name in os.listdir('/proc/self/fd'):
        try:fds[name] = os.readlink('/proc/self/fd/' + name)
        except FileNotFoundError:pass
    assert set(fds) <= {'0', '1', '2'}
    assert not any(expected['outside_canary_path'] in target for target in fds.values())
    result['fds'] = fds
    assert os.path.realpath('/tmp') == '/work/tmp'
    Path('/work/write-canary.txt').write_text('new integration fixture only\n')
    for family, address in [(socket.AF_INET, ('192.0.2.1', 9)), (socket.AF_INET6, ('2001:db8::1', 9))]:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as connection:
                connection.settimeout(0.25)
                connection.connect(address)
        except OSError as error:
            assert error.errno in {errno.ENETUNREACH, errno.EHOSTUNREACH, errno.EAFNOSUPPORT, errno.EPERM, errno.EACCES}
            result['network_family_' + str(int(family))] = error.errno
        else:raise AssertionError('external network boundary failed')
    return result


try:
    expected = json.loads(Path('/input/expected.json').read_text())
    report['boundaries_before_any_candidate_or_installer'] = boundaries(expected)
    report['stages'].append('synthetic_boundaries_passed')
    for relative, digest in expected['source_sha256'].items():
        path = Path('/input/source') / relative
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
        ast.parse(path.read_text(), filename=str(path))  # Parse only; no full app import.
    wheel_path = '/input/bootstrap/pip-26.2.1-py3-none-any.whl'
    assert hashlib.sha256(Path(wheel_path).read_bytes()).hexdigest() == expected['pip_sha256']
    assert hashlib.sha256(Path('/input/closure.lock').read_bytes()).hexdigest() == expected['lock_sha256']
    # Exact recognized PyPA wheel, guarded before execution. This standard runpy
    # bootstrap is confined to this child and removed before framework imports.
    original_path, original_argv = sys.path[:], sys.argv[:]
    sys.path.insert(0, wheel_path)
    sys.argv = ['pip', '--isolated', '--disable-pip-version-check', 'install', '--no-cache-dir',
                '--no-index', '--no-deps', '--only-binary=:all:', '--no-compile', '--require-hashes',
                '--find-links=/input/wheels', '--target=/work/site-packages', '-r', '/input/closure.lock']
    report['installer_argv'] = sys.argv[:]
    try:
        try:runpy.run_module('pip', run_name='__main__', alter_sys=True)
        except SystemExit as error:
            assert error.code in (None, 0), ('installer exited', error.code)
    finally:
        sys.path[:], sys.argv[:] = original_path, original_argv
    report['stages'].append('exact_hash_required_offline_target_materialized')
    report['workspace_after_install'] = inventory()
    site = Path('/work/site-packages')
    versions = {d.metadata['Name'].lower().replace('_', '-'): d.version for d in importlib.metadata.distributions(path=[str(site)])}
    assert versions == expected['selected_versions'], (versions, expected['selected_versions'])
    report['installed_target_versions'] = versions
    sys.path.insert(0, str(site))
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
    import pydantic_core
    from pydantic_core import SchemaValidator
    assert SchemaValidator({'type': 'int'}).validate_python('42') == 42
    report['native_pydantic_core'] = {'version': pydantic_core.__version__, 'package_origin': pydantic_core.__file__,
                                    'extension_origin': sys.modules['pydantic_core._pydantic_core'].__file__,
                                    'basic_native_validation': True}
    import pytest
    test_result = {}

    class Results:
        def pytest_sessionfinish(self, session, exitstatus):
            test_result.update({'collected': session.testscollected, 'failed': session.testsfailed, 'exitstatus': int(exitstatus)})

    status = pytest.main(['-q', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider',
                          '--basetemp=/work/pytest-temp', '/input/fixture_tests.py'], plugins=[Results()])
    report['framework_tests'] = test_result
    assert status == 0, ('framework tests failed', int(status))
    report['stages'].append('narrow_real_framework_fixture_tests_passed')
    forbidden = sorted(name for name in sys.modules if name == 'app' or name.startswith('app.'))
    assert not forbidden, forbidden
    report['real_app_namespace_modules'] = forbidden
    report['dependency_module_origins'] = {name: sys.modules[name].__file__ for name in ['fastapi', 'starlette', 'pydantic', 'pydantic_core', 'apscheduler', 'pytest', 'pytest_asyncio', 'httpx', 'packaging'] if name in sys.modules}
    assert all(path.startswith(str(site) + '/') for path in report['dependency_module_origins'].values())
    report['workspace_final'] = inventory()
    report['status'] = 'NARROW_FIXTURE_INTEGRATION_PASSED'
except BaseException as error:
    report.update({'status': 'STOPPED_AT_FAILED_STAGE_NO_FALLBACK', 'error_type': type(error).__name__,
                   'error': str(error), 'traceback': traceback.format_exc(limit=10)})
finally:
    report['finished_at'] = datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report, indent=2) + '\n')
    print('INTEGRATION_RESULT=' + json.dumps(report, sort_keys=True))
raise SystemExit(0 if report['status'] == 'NARROW_FIXTURE_INTEGRATION_PASSED' else 2)
