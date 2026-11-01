"""Verified PyPA installer only after fresh namespace/canary/limit checks."""
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

report={'status':'NOT_STARTED','started_at':datetime.now(UTC).isoformat()}
try:
    expected=json.loads(Path('/input/expected.json').read_text())
    guard=Path('/input/guard.py').read_bytes()
    assert hashlib.sha256(guard).hexdigest()==expected['guard_sha256']
    nodes=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef) and n.name=='boundaries']
    assert len(nodes)==1
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'/input/guard.py','exec'),globals())
    report['boundaries_before_installer']=boundaries(expected)
    assert hashlib.sha256(Path('/input/pip.whl').read_bytes()).hexdigest()=='71138adf1f4ca900cdb7d289c21b7494329f2332b6d85f0e1c42108c0384ed3e'
    assert hashlib.sha256(Path('/input/plan.json').read_bytes()).hexdigest()==expected['plan_sha256']
    assert hashlib.sha256(Path('/input/full-app.lock').read_bytes()).hexdigest()==expected['lock_sha256']
    plan=json.loads(Path('/input/plan.json').read_text())
    for row in plan['selected'].values():
        assert hashlib.sha256((Path('/input/wheels')/row['filename']).read_bytes()).hexdigest()==row['artifact_sha256']
    # PyPA wheel is recognized and hash-bound. No setup.py/build backend or
    # candidate-package import; target is new, private, disposable task state.
    sys.path.insert(0,'/input/pip.whl')
    sys.argv=['pip','--isolated','--disable-pip-version-check','install','--no-cache-dir','--no-index','--no-deps','--only-binary=:all:','--no-compile','--require-hashes','--find-links=/input/wheels','--target=/work/site-packages','-r','/input/full-app.lock']
    report['installer_argv']=sys.argv[:]
    try:runpy.run_module('pip',run_name='__main__',alter_sys=True)
    except SystemExit as e:assert e.code in (None,0),e.code
    versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions(path=['/work/site-packages'])}
    assert versions==expected['versions']
    report['versions']=versions
    report['candidate_imports']=[n for n in sys.modules if n=='app' or n.startswith('app.')]
    assert not report['candidate_imports']
    report['status']='EXACT28_MATERIALIZED'
except BaseException as e:
    report.update(status='STOPPED',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(limit=10))
finally:
    report['finished_at']=datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='EXACT28_MATERIALIZED' else 2)
