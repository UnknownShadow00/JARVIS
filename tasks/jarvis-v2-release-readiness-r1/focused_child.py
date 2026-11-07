"""Run only in fresh verified cage; source is copied public code, never runtime."""
import ast
from datetime import UTC, datetime
import errno
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import socket
import sys
import traceback

report={'status':'NOT_STARTED','started_at':datetime.now(UTC).isoformat()}
try:
    expected=json.loads(Path('/input/expected.json').read_text())
    guard=Path('/input/guard.py').read_bytes()
    assert hashlib.sha256(guard).hexdigest()==expected['guard_sha256']
    nodes=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef) and n.name=='boundaries']
    assert len(nodes)==1
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'/input/guard.py','exec'),globals())
    report['boundaries']=boundaries(expected)
    assert os.statvfs('/deps').f_flag & os.ST_RDONLY
    versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions(path=['/deps'])}
    assert versions==expected['versions']
    for name,digest in expected['source_sha256'].items():
        p=Path('/input/source')/name
        assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
        ast.parse(p.read_text())
    sys.path[:0]=['/input/source','/deps']
    os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
    import pytest
    results={}
    class Results:
        def pytest_sessionfinish(self,session,exitstatus):
            terminal=session.config.pluginmanager.getplugin('terminalreporter')
            results.update(collected=session.testscollected,failed=session.testsfailed,skipped=len(terminal.stats.get('skipped',[])),exitstatus=int(exitstatus))
    code=pytest.main(['-q','-p','pytest_asyncio.plugin','-p','no:cacheprovider','--basetemp=/work/pytest','/input/tests/test_secure_transport.py'],plugins=[Results()])
    report['tests']=results
    # Attempt actual existing modules with exact available dependencies, no
    # fake sys.modules/provider substitutions. Missing dependency is a blocker,
    # never a claim of full startup/lifespan qualification.
    report['full_app_import_attempts']={}
    for module in [] if 'uvicorn' in versions else ['app.main','app.server']:
        try:
            imported=importlib.import_module(module)
            report['full_app_import_attempts'][module]={'imported':True,'lifespan_tested':False,'blocker':'full lifespan requires complete offline dependency closure'}
        except ModuleNotFoundError as e:
            report['full_app_import_attempts'][module]={'imported':False,'missing_module':e.name,'traceback':traceback.format_exc(limit=6),'lifespan_tested':False}
    assert not any(n=='pip' or n.startswith('pip.') for n in sys.modules)
    report['status']='CORE_PASS' if code==0 and results['skipped']==0 else 'TEST_FAILURE'
except BaseException as e:
    report.update(status='STOPPED',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(limit=10))
finally:
    report['finished_at']=datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='CORE_PASS' else 2)
