"""Safe discovery/CI regressions: no historical, provider or config-writing tests."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest
import yaml
from gauntlet_protocol import InvalidEvidence, case_identifiers
from test_enrollment import check_enrollment

ROOT = Path('/source')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


@pytest.fixture
def guard():
    return module('safety_guard_fixture', ROOT/'conftest.py')


@pytest.fixture
def entry():
    return module('safety_entry_fixture', ROOT/'scripts/offline_acceptance.py')


@pytest.mark.parametrize('kind', ['required', 'ancestor', 'historical', 'unsafe', 'new', 'symlink'])
def test_collector_allowlist_before_import(tmp_path, guard, kind):
    tests = tmp_path/'tests';tests.mkdir()
    required = tests/'test_required.py';required.write_text('')
    choices = {'required': required, 'ancestor': tests, 'historical': tmp_path/'tasks/test_old.py',
               'unsafe': tests/'test_switch_models.py', 'new': tests/'test_unreviewed.py', 'symlink': tests/'test_link.py'}
    if kind == 'symlink':choices[kind].symlink_to(required)
    elif kind not in ('required', 'ancestor'):
        choices[kind].parent.mkdir(parents=True, exist_ok=True)
        choices[kind].write_text("raise RuntimeError('SYNTHETIC_PRIVATE_IMPORT')")
    assert guard.permitted(choices[kind], {required}) is (kind in ('required', 'ancestor'))
    if kind not in ('required', 'ancestor'):
        collector=SimpleNamespace(path=choices[kind],config=SimpleNamespace(_jarvis_allowed_paths={required}))
        with pytest.raises(pytest.UsageError):guard.pytest_collectstart(collector)


@pytest.mark.parametrize('invocation', ['root', 'tests', 'collect', 'historical', 'unsafe'])
def test_direct_pytest_refuses_before_any_import(tmp_path, invocation):
    (tmp_path/'conftest.py').write_bytes((ROOT/'conftest.py').read_bytes())
    (tmp_path/'pytest.ini').write_bytes((ROOT/'pytest.ini').read_bytes())
    (tmp_path/'tests').mkdir();(tmp_path/'tasks/archive').mkdir(parents=True)
    marker = tmp_path/'imported'
    payload = "from pathlib import Path\nPath("+repr(str(marker))+").write_text('bad')\nraise RuntimeError('SYNTHETIC_PRIVATE_IMPORT')\n"
    (tmp_path/'tests/test_switch_models.py').write_text(payload)
    (tmp_path/'tasks/archive/test_old.py').write_text(payload)
    options = {'root': [], 'tests': ['tests'], 'collect': ['--collect-only'],
               'historical': ['tasks/archive/test_old.py'], 'unsafe': ['tests/test_switch_models.py']}[invocation]
    env = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD='1', PYTHONPATH='/deps', JARVIS_ALLOW_PYTEST='1')
    result = subprocess.run([sys.executable, '-B', '-m', 'pytest', *options], cwd=tmp_path, env=env, capture_output=True, text=True, timeout=10)
    assert result.returncode == 4 and not marker.exists()
    assert 'scripts/offline_acceptance.py' in result.stderr
    assert 'SYNTHETIC_PRIVATE_IMPORT' not in result.stdout+result.stderr


@pytest.mark.parametrize('args', [['pytest'], ['/runner.py'], ['/runner.py', '--child', '1', 'safety'] ], ids=['host', 'short', 'incomplete'])
def test_environment_variable_cannot_enable_host_pytest(monkeypatch, guard, args):
    monkeypatch.setenv('JARVIS_ALLOW_PYTEST', '1')
    monkeypatch.setattr(sys, 'argv', args)
    with pytest.raises(pytest.UsageError):guard.pytest_configure(SimpleNamespace())


@pytest.mark.parametrize('fault', ['added', 'missing', 'changed', 'symlink'])
def test_module_enrollment_fails_closed(tmp_path, fault):
    tests = tmp_path/'tests';tests.mkdir();file = tests/'test_one.py';file.write_text('def test_one(): pass\n')
    body = {'version':1, 'modules':{'tests/test_one.py':{'disposition':'required','reason':'synthetic regression', 'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}}}
    policy = tmp_path/'policy.json';policy.write_text(json.dumps(body));digest = hashlib.sha256(policy.read_bytes()).hexdigest()
    if fault == 'added':(tests/'test_new.py').write_text('raise RuntimeError("SYNTHETIC_PRIVATE_IMPORT")')
    if fault == 'missing':file.unlink()
    if fault == 'changed':file.write_text('def test_substitution(): pass\n')
    if fault == 'symlink':
        private=tmp_path/'synthetic_private';private.write_text('SYNTHETIC_PRIVATE_CONTENT');file.unlink();file.symlink_to(private)
    with pytest.raises(InvalidEvidence):check_enrollment(tmp_path, policy, expected_digest=digest)


def test_original_886_exact_nodes_retained_and_all_modules_enrolled():
    baseline = json.loads((ROOT/'scripts/required_nodes_6341648.json').read_text())['nodeids']
    manifest = json.loads(Path('/inventory.json').read_text())
    nodes = [n for k,s in manifest['suites'].items() if k != 'probe' and not k.startswith('case:') for n in s['nodeids']]
    policy = json.loads((ROOT/'scripts/test_enrollment.json').read_text())['modules']
    assert len(baseline) == len(set(baseline)) == 886 and set(baseline) <= set(nodes)
    assert len(nodes) == len(set(nodes))
    assert {n.split('::')[0] for n in nodes} == {n for n,e in policy.items() if e['disposition']=='required'}
    assert sum(e['disposition']=='excluded_offline_scope' for e in policy.values()) == 39
    assert sum(e['disposition']=='excluded_live_or_hardware' for e in policy.values()) == 11


def test_all_twelve_historical_modules_preserved_as_evidence():
    body=json.loads((ROOT/'scripts/historical_packet_inventory.json').read_text())
    paths=[n for n in body['files'] if '/preserved-development-tests/test_' in n and n.endswith('.py')]
    assert len(paths)==12 and len(body['files'])==883
    assert all(n.startswith('tasks/') for n in paths)
    config=(ROOT/'pytest.ini').read_text()
    assert 'testpaths = tests' in config and 'norecursedirs = tasks ' in config


@pytest.mark.parametrize('fault', ['missing', 'changed', 'extra'])
def test_historical_integrity_is_not_silently_rewritten(tmp_path, entry, fault):
    (tmp_path/'scripts').mkdir();folder=tmp_path/'tasks/history';folder.mkdir(parents=True);file=folder/'test_old.py';file.write_text('historical evidence')
    body={'folders':['tasks/history'],'files':{'tasks/history/test_old.py':hashlib.sha256(file.read_bytes()).hexdigest()}}
    (tmp_path/'scripts/historical_packet_inventory.json').write_text(json.dumps(body))
    if fault=='missing':file.unlink()
    if fault=='changed':file.write_text('different history')
    if fault=='extra':(folder/'extra.txt').write_text('not reviewed')
    with pytest.raises(ValueError):entry.packet_hashes(tmp_path)
    if fault=='extra':
        (folder/'extra.txt').unlink()
        target=tmp_path/'synthetic_private_dir';target.mkdir()
        (folder/'linked_directory').symlink_to(target,target_is_directory=True)
        with pytest.raises(ValueError):entry.packet_hashes(tmp_path)


def test_ci_routes_to_complete_gate_without_install_or_broad_pytest():
    body=yaml.load((ROOT/'.github/workflows/tests.yml').read_text(),Loader=yaml.BaseLoader)
    assert body['permissions']=={'contents':'read'}
    steps=body['jobs']['test']['steps']
    assert body['jobs']['test']['runs-on']=="${{ vars.JARVIS_QUALIFIED_OFFLINE_RUNNER || 'ubuntu-latest' }}"
    assert steps[0]['with']['persist-credentials']=='false'
    commands=[s['run'] for s in steps if 'run' in s]
    assert commands==['python3 -B scripts/offline_acceptance.py --output-dir "$RUNNER_TEMP/jarvis-offline-acceptance"']
    assert all(term not in '\n'.join(commands) for term in ('pytest ', 'pip ', 'apt-get', 'sudo ', '--list-required', '--coverage'))
    assert 'pull_request' in body['on'] and 'push' in body['on']


def test_new_ci_entrypoint_requires_review(tmp_path, entry):
    (tmp_path/'scripts').mkdir();folder=tmp_path/'.github/workflows';folder.mkdir(parents=True)
    (folder/'tests.yml').write_text('reviewed')
    (tmp_path/'scripts/offline_environment.json').write_text(json.dumps({'workflow_paths':['.github/workflows/tests.yml']}))
    entry.check_ci_inventory(tmp_path)
    (folder/'unsafe.yml').write_text('run: pytest tests/')
    with pytest.raises(ValueError):entry.check_ci_inventory(tmp_path)
    # A newly enrolled suite must never be ignored by a fixed CI mode list.
    (tmp_path/'scripts/required_tests.json').write_text(json.dumps({'suites':{'new_unreviewed_mode':{'nodeids':[]}}}))
    with pytest.raises(ValueError, match='unreviewed_positive_suite'):entry.required_nodes(tmp_path)


def test_symlink_ci_directory_fails_before_read(tmp_path, entry):
    (tmp_path/'scripts').mkdir()
    (tmp_path/'scripts/offline_environment.json').write_text(json.dumps({'workflow_paths':['.github/workflows/tests.yml']}))
    private=tmp_path/'synthetic_private';private.mkdir();(private/'tests.yml').write_text('SYNTHETIC_PRIVATE_CONTENT')
    (tmp_path/'.github').symlink_to(private, target_is_directory=True)
    with pytest.raises(ValueError):entry.check_ci_inventory(tmp_path)


def test_qualified_dependencies_are_explicit(entry, tmp_path, monkeypatch):
    body=json.loads((ROOT/'scripts/offline_environment.json').read_text())
    assert body['packages']['APScheduler']=='3.11.3' and body['python']=='3.14.4'
    assert set(entry.MODES)=={'safety','coverage','reconciliation','r3','r2','new','existing'}
    monkeypatch.setattr(entry, 'DEPS', tmp_path)
    with pytest.raises(ValueError, match='unqualified_offline_environment'):entry.check_environment()


def test_historical_adapter_only_adds_public_fixture_inputs():
    # The full outer CLI matrices execute the preserved helpers. This test
    # asserts the adapter cannot become an application/provider entrypoint.
    text=(ROOT/'scripts/offline_contracts.py').read_text()
    assert 'PUBLIC_ADDITIONS' in text and 'conftest.py' in text and '.github/workflows/tests.yml' in text
    assert '.write_text(' not in text and '.write_bytes(' not in text


def evidence():
    nodes=['tests/test_one.py::test_one','tests/test_two.py::test_two'];ids=list(case_identifiers(nodes).values())
    body=dict(status='PASS',gate_exit_code=0,child_exit_code=0,required_missing=0,unexpected_collected=0,executed=2,
              collection=dict(skipped=0,deselected=0),counts=dict(PASS=2,FAIL=0,ERROR=0,SKIP=0,INCOMPLETE=0),
              session=dict(started=True,collected=True,finished=True,interrupted=False,internal_error=False,collection_error=False,unexpected_report=False,pytest_exit_code=0,collected_count=2),
              scenarios=[dict(id=i,complete=True,timed_out=False,phases=[dict(phase=p,outcome='passed') for p in ('setup','call','teardown')]) for i in ids])
    return nodes,body


@pytest.mark.parametrize('fault',['missing','duplicate','substitution','phase','session','skip','zero_exit_partial'])
def test_ci_zero_exit_cannot_replace_complete_execution(entry, fault):
    nodes,body=evidence();body=deepcopy(body)
    if fault in ('missing','zero_exit_partial'):body['scenarios'].pop()
    if fault=='duplicate':body['scenarios'][1]['id']=body['scenarios'][0]['id']
    if fault=='substitution':body['scenarios'][0]['id']='0'*64
    if fault=='phase':body['scenarios'][0]['phases'].pop()
    if fault=='session':body['session']['finished']=False
    if fault=='skip':body['scenarios'][0]['phases'][1]['outcome']='skipped'
    assert body['child_exit_code']==0 and not entry.complete_suite(body,nodes)


def test_legitimate_complete_execution(entry):
    nodes,body=evidence();assert entry.complete_suite(body,nodes)
