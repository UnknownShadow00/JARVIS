#!/usr/bin/env python3
"""Source AST plus retained official wheel metadata plan; never import the app.

No installs/builds/extraction/downloads or runtime tests. The verified prior
metadata reader is reused as a data-only tool with normal installed packaging.
"""
from __future__ import annotations

import ast
from collections import deque
from datetime import UTC, datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKET = Path(__file__).resolve().parent
PRIOR = ROOT / 'tasks/jarvis-framework-closure-r1'
VERIFIER_SHA = 'b6e3414c2da4aebe72c38732923be31a605a023cd78e6eedba9b1573f8bbab97'
PROVENANCE = ROOT / 'tasks/jarvis-offline-provenance-r1'
PROVENANCE_SEAL = '85637a307d48615233471efb342c0e6faad55ef8efa146c5ed6850eb44f11da4'
ARTIFACT_SHA = '9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837'
PIN_SHA = 'b07d5613eb50547b99229b2230bf90bd9d884dfcc869ecc025ffb003449d680a'
NARROW_LOCK_SHA = 'c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8'
MODULE_DISTRIBUTIONS = {'fastapi': 'fastapi', 'pydantic': 'pydantic', 'pydantic_settings': 'pydantic-settings',
                        'yaml': 'pyyaml', 'httpx': 'httpx', 'psutil': 'psutil', 'uvicorn': 'uvicorn',
                        'starlette': 'starlette', 'apscheduler': 'apscheduler'}
FORBIDDEN = {'app', 'uvicorn', 'yaml', 'pydantic_settings', 'psutil', 'fastapi', 'starlette',
             'pydantic', 'pydantic_core', 'apscheduler', 'pytest', 'pytest_asyncio', 'httpx'}
ATTEMPTS = []


def guard(event, arguments):
    if event in {'socket.connect', 'socket.bind', 'socket.getaddrinfo'} or event == 'socket.__new__':
        ATTEMPTS.append(event)
        raise RuntimeError('network_forbidden')
    if event == 'import' and arguments and arguments[0].split('.')[0] in FORBIDDEN:
        ATTEMPTS.append('payload_import:' + arguments[0])
        raise RuntimeError('payload_import_forbidden')


sys.addaudithook(guard)


def load_verifier():
    path = PRIOR / 'verify_closure.py'
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != VERIFIER_SHA:
        raise RuntimeError('retained_verifier_hash_mismatch')
    spec = importlib.util.spec_from_file_location('retained_wheel_metadata_data_tool', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def module_path(module):
    if not module or not (module == 'app' or module.startswith('app.')):
        return None
    plain = ROOT.joinpath(*module.split('.'))
    return plain.with_suffix('.py') if plain.with_suffix('.py').is_file() else (
        plain / '__init__.py' if (plain / '__init__.py').is_file() else None)


def handles_missing(handlers):
    for handler in handlers:
        if handler.type is None:
            return True
        names = {node.id for node in ast.walk(handler.type) if isinstance(node, ast.Name)}
        if names & {'ImportError', 'ModuleNotFoundError', 'Exception', 'BaseException'}:
            return True
    return False


def import_rows(tree, relative):
    rows = []

    def visit(statements, optional=False, lazy=False):
        for node in statements:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    modules = [alias.name for alias in node.names]
                else:
                    if node.level:
                        raise RuntimeError('relative_import_requires_manual_review:' + relative)
                    modules = [node.module or '']
                    for alias in node.names:
                        possible = (node.module + '.' + alias.name) if node.module else alias.name
                        if module_path(possible):
                            modules.append(possible)
                rows.extend({'source': relative, 'line': node.lineno, 'module': name,
                             'optional_missing_import_handled': optional, 'lazy': lazy} for name in modules)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                visit(node.body, optional, True)
            elif isinstance(node, ast.ClassDef):
                visit(node.body, optional, lazy)
            elif isinstance(node, ast.Try):
                visit(node.body, optional or handles_missing(node.handlers), lazy)
                for handler in node.handlers:
                    visit(handler.body, optional, lazy)
                visit(node.orelse, optional, lazy)
                visit(node.finalbody, optional, lazy)
            elif isinstance(node, ast.If):
                if isinstance(node.test, ast.Name) and node.test.id == 'TYPE_CHECKING':
                    continue
                visit(node.body, optional, lazy)
                visit(node.orelse, optional, lazy)
            else:
                for field in ('body', 'orelse', 'finalbody'):
                    body = getattr(node, field, None)
                    if isinstance(body, list):
                        visit(body, optional, lazy)
    visit(tree.body)
    return rows


def source_graph(v, budget):
    pending = deque(['app.main'])
    seen, files, imports, mandatory, unknown = set(), {}, [], set(), []
    while pending:
        module = pending.popleft()
        if module in seen:
            continue
        seen.add(module)
        if len(seen) > 128:
            raise RuntimeError('source_module_limit')
        path = module_path(module)
        if path is None:
            raise RuntimeError('source_module_missing:' + module)
        raw = v.read_data(path, budget)
        relative = path.relative_to(ROOT).as_posix()
        files[relative] = v.sha(raw)
        rows = import_rows(ast.parse(raw, filename=relative), relative)
        imports.extend(rows)
        for index in range(1, len(module.split('.'))):
            parent = '.'.join(module.split('.')[:index])
            if module_path(parent):
                pending.append(parent)
        for row in rows:
            if row['lazy'] or row['optional_missing_import_handled']:
                continue
            name = row['module']
            root = name.split('.')[0]
            if root == 'app':
                pending.append(name)
            elif root in sys.stdlib_module_names or root == '__future__':
                continue
            elif root in MODULE_DISTRIBUTIONS:
                mandatory.add(MODULE_DISTRIBUTIONS[root])
            else:
                unknown.append(row)
    # A module-level import graph alone omits these known eager-to-lifespan edges.
    # Their source is recorded and was reviewed as text, never executed here.
    manual = [
        {'source': 'app/server.py::lifespan -> app/agent/scheduler.py::Scheduler.start',
         'distribution': 'apscheduler', 'reason': 'mandatory scheduler startup imports AsyncIOScheduler'},
        {'source': 'app/tools/registry.py::_discover_tool_modules', 'module': 'app.tools',
         'reason': 'called during module initialization; package __init__ is empty, tool modules remain lazy'},
    ]
    mandatory.add('apscheduler')
    return {'entrypoint': 'app.main', 'source_sha256': files, 'import_rows': imports,
            'mandatory_runtime_distributions': sorted(mandatory), 'unmapped_mandatory_imports': unknown,
            'manual_initialization_edges': manual,
            'assumptions': ['voice and hotkey startup disabled in future synthetic configuration',
                            'Mem0/Graphiti absent guarded imports; ChromaDB and tool backends remain lazy',
                            'no real chat/tool/model/provider execution',
                            'uvicorn bare mandatory import closure; [standard]/websocket extras not requested',
                            'static AST is not a full interprocedural runtime proof; future actual entrypoint validation remains required']}


def main():
    if (PACKET / 'DEPENDENCY-PLAN.json').exists() or (PACKET / 'full-app.lock').exists():
        raise SystemExit('new_plan_outputs_required; existing evidence is never overwritten')
    started = datetime.now(UTC).isoformat()
    v = load_verifier()
    budget = v.Budget()
    report = {'started_at': started, 'status': 'INCOMPLETE', 'verifier_sha256': VERIFIER_SHA,
              'scope': 'current source AST + retained official wheel metadata only; no app import/install/test',
              'packaging_tool': {'version': v.packaging.__version__, 'origin': v.packaging.__file__},
              'blockers': [], 'limits': {'metadata_and_payload_hash_read_bytes': v.CAP,
                                        'source_modules': 128, 'metadata_entry_bytes': v.ENTRY_CAP}}
    inspected = {}
    try:
        graph = source_graph(v, budget)
        report['source_graph'] = graph
        if graph['unmapped_mandatory_imports']:
            raise RuntimeError('unmapped_mandatory_source_imports')
        sums = v.read_data(PROVENANCE / 'SHA256SUMS', budget, expected=PROVENANCE_SEAL)
        evidence_name = 'evidence-20261030T222449706209Z.json'
        expected = next(line.split('  ', 1)[0] for line in sums.decode().splitlines() if line.endswith('  ' + evidence_name))
        provenance_raw = v.read_data(PROVENANCE / evidence_name, budget, maximum=2 * v.ENTRY_CAP, expected=expected)
        provenance = json.loads(provenance_raw)
        selected_sha = provenance['gate6l_archive']['member_hashes']['results/selected-artifacts.json']['sha256']
        selected_rows = json.loads(v.read_data(v.BUNDLE / 'results/selected-artifacts.json', budget, expected=selected_sha))
        official = {v.canonicalize_name(row['name']): row for row in selected_rows}
        records = json.loads(v.read_data(v.BUNDLE / 'locks/gate6k-ARTIFACTS.json', budget, expected=ARTIFACT_SHA))
        by_name = {v.canonicalize_name(key.split(':', 1)[1]): row for key, row in records.items() if key.startswith('distribution:')}
        lock_raw = v.read_data(v.BUNDLE / 'locks/requirements-versions.txt', budget, expected=PIN_SHA)
        pins = {}
        for line in lock_raw.decode().splitlines():
            if not line.strip() or line.lstrip().startswith('#'):
                continue
            requirement = v.Requirement(line)
            specs = list(requirement.specifier)
            if len(specs) != 1 or specs[0].operator != '==' or '*' in specs[0].version or requirement.marker or requirement.extras or requirement.url:
                raise RuntimeError('unexpected_exact_lock_schema')
            name = v.canonicalize_name(requirement.name)
            if name in pins:
                raise RuntimeError('duplicate_pin')
            pins[name] = str(v.Version(specs[0].version))
        narrow_raw = v.read_data(PRIOR / 'proposed-closure-20261030T231119946730Z.lock', budget, expected=NARROW_LOCK_SHA)
        narrow_names = {v.canonicalize_name(v.Requirement(line.split(' --hash=', 1)[0]).name)
                        for line in narrow_raw.decode().splitlines() if line.strip() and not line.startswith('#')}
        roots = sorted(set(graph['mandatory_runtime_distributions']) | {'pytest', 'pytest-asyncio'})
        missing_roots = sorted(set(roots) - set(pins))
        if missing_roots:
            raise RuntimeError('mandatory_root_missing_pin:' + ','.join(missing_roots))
        environment, tags = v.default_environment(), set(v.sys_tags())
        report.update({'roots_no_extras': roots, 'environment': environment,
                       'inputs': {'provenance_manifest_sha256': PROVENANCE_SEAL,
                                  'provenance_evidence_sha256': v.sha(provenance_raw),
                                  'selected_artifacts_sha256': selected_sha,
                                  'artifact_record_sha256': ARTIFACT_SHA, 'version_lock_sha256': PIN_SHA,
                                  'narrow22_lock_sha256': v.sha(narrow_raw)}})

        def obtain(name, version):
            row, selection = by_name.get(name), official.get(name)
            if not row or not selection or v.Version(row['version']) != v.Version(version):
                raise v.Blocker('artifact_pin_identity', name)
            if selection.get('artifact_type') != 'PyPI wheel':
                raise v.Blocker('not_retained_official_wheel', name + ':' + str(selection.get('artifact_type')))
            payload = selection.get('artifact', {})
            relative = payload.get('path', '')
            v.safe_name(relative)
            retained = provenance['dependency_checks']['wheel_members'].get(relative)
            if not retained or payload.get('sha256') != row['sha256'] or retained['sha256'] != row['sha256']:
                raise v.Blocker('retained_official_wheel_identity', name)
            result = v.inspect_wheel(v.BUNDLE / relative, Path(relative).name, row['sha256'], budget,
                                     tags, v.Version(environment['python_full_version']))
            result.update({'relative_path': relative, 'official_source_url': payload.get('url'),
                           'retained_verification_claim': selection.get('verification'),
                           'record_provenance': row.get('provenance_record'),
                           'native_payload_not_executed': any(not tag.endswith('-none-any') for tag in result['matched_tags'])})
            inspected[name] = result
            return result

        selected, edges, extras = v.fixed_closure([f'{name}=={pins[name]}' for name in roots], pins, obtain, environment)
        missing_narrow = sorted(narrow_names - selected.keys())
        if missing_narrow:
            raise RuntimeError('narrow_closure_not_preserved:' + ','.join(missing_narrow))
        report.update({'status': 'OFFICIAL_WHEEL_METADATA_PLAN_READY_NOT_INSTALLED', 'selected': selected,
                       'selected_count': len(selected), 'dependency_edges': edges, 'activated_extras': extras,
                       'active_edges': sum(row['active'] for rows in edges.values() for row in rows),
                       'record_payloads_verified': sum(row['record_payloads_verified'] for row in selected.values()),
                       'beyond_narrow22': sorted(selected.keys() - narrow_names),
                       'native_payloads_require_execution_qualification': sorted(name for name, row in selected.items() if row['native_payload_not_executed']),
                       'narrow22_preserved_as_subset': True})
    except Exception as error:
        report['status'] = 'BLOCKED_NO_COMPLETE_FULL_APP_LOCK'
        report['blockers'].append({'code': error.code if isinstance(error, v.Blocker) else type(error).__name__,
                                   'detail': error.detail if isinstance(error, v.Blocker) else str(error)})
        report['inspected_before_blocker'] = inspected
    report.update({'finished_at': datetime.now(UTC).isoformat(), 'bounded_read_bytes': budget.used,
                   'network_or_payload_import_attempts': ATTEMPTS,
                   'forbidden_payload_modules_imported': sorted(name for name in sys.modules if name.split('.')[0] in FORBIDDEN),
                   'limitations': ['metadata/hash/tag success does not qualify native ABI/library execution or full app startup',
                                   'no package installed/extracted/imported; no candidate path injection',
                                   'optional voice/tool/provider/config-enabled feature dependencies excluded',
                                   'no publisher signature revalidation; retained claims attributed only',
                                   'actual app import reads configuration/starts audit and other singletons; none was executed here']})
    if ATTEMPTS or report['forbidden_payload_modules_imported']:
        report['status'] = 'BLOCKED_NO_COMPLETE_FULL_APP_LOCK'
        report['blockers'].append({'code': 'prohibited_effect_attempt', 'detail': 'see recorded attempts'})
    encoded = (json.dumps(report, indent=2) + '\n').encode()
    budget.take(len(encoded))
    with (PACKET / 'DEPENDENCY-PLAN.json').open('xb') as stream:
        stream.write(encoded)
    if report['status'] == 'OFFICIAL_WHEEL_METADATA_PLAN_READY_NOT_INSTALLED':
        lines = ['# Proposed full actual-app mandatory imports plus retained test scope; no extras.\n',
                 '# Metadata verified only: not installed, not runtime/native-ABI qualified.\n']
        lines.extend(f"{name}=={row['version']} --hash=sha256:{row['artifact_sha256']}\n" for name, row in sorted(report['selected'].items()))
        with (PACKET / 'full-app.lock').open('x') as stream:
            stream.writelines(lines)
    print(json.dumps({key: report.get(key) for key in ('status', 'roots_no_extras', 'selected_count', 'beyond_narrow22',
                                                     'native_payloads_require_execution_qualification', 'active_edges',
                                                     'record_payloads_verified', 'blockers', 'bounded_read_bytes')}, indent=2))
    return 0 if report['status'] == 'OFFICIAL_WHEEL_METADATA_PLAN_READY_NOT_INSTALLED' else 2


if __name__ == '__main__':
    raise SystemExit(main())
