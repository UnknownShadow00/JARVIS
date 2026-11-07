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
    sys.path.insert(0,'/input')
    from benchmark_workload import run
    report['benchmarks']=run()
    from enrollment_benchmark import run as enrollment_costs
    report['enrollment_benchmarks']=enrollment_costs()
    Path('/work/ENROLLMENT-BENCHMARKS.json').write_text(json.dumps(report['enrollment_benchmarks'],indent=2)+'\n')
    assert not any(n=='pip' or n.startswith('pip.') for n in sys.modules)
    report['status']='BENCHMARK_PASS'
except BaseException as e:
    report.update(status='STOPPED',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(limit=10))
finally:
    report['finished_at']=datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='BENCHMARK_PASS' else 2)
