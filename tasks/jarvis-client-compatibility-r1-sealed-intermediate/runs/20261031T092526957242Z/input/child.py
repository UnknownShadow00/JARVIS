"""Pip-free reader-only qualification in the existing fresh isolated tool cage."""
import ast
from datetime import UTC, datetime
import errno
import hashlib
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import sys
import traceback
import unittest

report={'status':'NOT_STARTED','started_at':datetime.now(UTC).isoformat()}
try:
    expected=json.loads(Path('/input/expected.json').read_text())
    guard=Path('/input/guard.py').read_bytes()
    assert hashlib.sha256(guard).hexdigest()==expected['guard_sha256']
    nodes=[n for n in ast.parse(guard).body if isinstance(n,ast.FunctionDef) and n.name=='boundaries']
    assert len(nodes)==1
    exec(compile(ast.Module(body=nodes,type_ignores=[]),'/input/guard.py','exec'),globals())
    report['boundaries_before_imports']=boundaries(expected)
    assert os.statvfs('/deps').f_flag & os.ST_RDONLY
    for name,digest in expected['source_sha256'].items():
        assert hashlib.sha256((Path('/input/source')/name).read_bytes()).hexdigest()==digest
    assert hashlib.sha256(Path('/input/test_reporter.py').read_bytes()).hexdigest()==expected['tests_sha256']
    versions={d.metadata['Name'].lower().replace('_','-'):d.version for d in importlib.metadata.distributions(path=['/deps'])}
    assert versions==expected['versions']
    sys.path.insert(0,'/deps')
    import yaml
    project=Path('/work/project')
    shutil.copytree('/input/source/app',project/'app')
    config=yaml.safe_load(Path('/input/example.yaml').read_text())
    config['safety']['dry_run']=True
    config['server'].update(host='127.0.0.1',api_token='',enable_voice_on_startup=False,enable_hotkey_listener=False,remote_access_enabled=False)
    config['comms'].update(discord_enabled=False,telegram_enabled=False,discord_token='',telegram_token='',discord_channel_id='',telegram_chat_id='')
    config['logging'].update(audit_log='/work/synthetic-audit.jsonl',log_to_file=False,log_file='/work/synthetic.log')
    config['routing']['embedding_enabled']=False
    config['models']['ollama_base_url']='http://127.0.0.1:9'
    for name in config['paths']:config['paths'][name]='/work/synthetic-'+name
    for key in ['mem0_enabled','chromadb_enabled','graphiti_enabled']:config['memory'][key]=False
    (project/'config.yaml').write_text(json.dumps(config))
    sys.path.insert(0,str(project))
    spec=importlib.util.spec_from_file_location('reader_cases','/input/test_reporter.py')
    tests=importlib.util.module_from_spec(spec);spec.loader.exec_module(tests)
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(tests))
    report['tests']={'run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}
    assert result.wasSuccessful() and result.testsRun==10 and not result.skipped
    from app.agent import reporter
    from app.agent.runtime import _authority
    assert _authority is None
    reporter.audit._shutdown()
    report['reporter_origin']=reporter.__file__
    report['reporter_sha256']=hashlib.sha256(Path(reporter.__file__).read_bytes()).hexdigest()
    report['comms_disabled']=not reporter.settings.comms.discord_enabled and not reporter.settings.comms.telegram_enabled
    assert not any(n=='pip' or n.startswith('pip.') or n=='app.server' or n=='app.boot' for n in sys.modules)
    report['status']='ACTUAL_REPORTER_READ_COMPATIBILITY_PASS'
except BaseException as e:
    report.update(status='FAILED_OR_BLOCKED',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc(limit=10))
finally:
    report['finished_at']=datetime.now(UTC).isoformat()
    Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='ACTUAL_REPORTER_READ_COMPATIBILITY_PASS' else 2)
