"""Actual app.main/server/lifespan with synthetic configuration, no HTTP listener."""
import ast
import asyncio
from datetime import UTC, datetime
import errno
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import resource
import shutil
import socket
import sys
import traceback
import uuid

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
    sys.path.insert(0,'/deps')
    import yaml
    import psutil
    from pydantic_core import SchemaValidator
    assert SchemaValidator({'type':'int'}).validate_python('42')==42
    assert yaml.load('synthetic: 1',Loader=yaml.CSafeLoader)=={'synthetic':1}
    assert psutil.Process().memory_info().rss>0
    report['native_execution']={}
    for name in ['pydantic_core._pydantic_core','yaml._yaml','psutil._psutil_linux']:
        module=importlib.import_module(name)
        path=Path(module.__file__)
        assert str(path).startswith('/deps/')
        report['native_execution'][name]={'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    project=Path('/work/project')
    shutil.copytree('/input/source/app',project/'app')
    raw=yaml.safe_load(Path('/input/source/config.yaml').read_text())
    raw['models']['ollama_base_url']='http://127.0.0.1:9'
    for name in ['main','coder','router','vision']:raw['models'][name]='synthetic-unused'
    raw['safety']['dry_run']=True
    raw['server'].update(host='127.0.0.1',api_token='',remote_access_enabled=False,enable_voice_on_startup=False,enable_hotkey_listener=False)
    raw['resource_mode'].update(enabled=False,preload_primary_model_on_wake=False,auto_light_sleep=False,auto_deep_sleep=False)
    raw['routing']['embedding_enabled']=False
    for key in ['mem0_enabled','chromadb_enabled','graphiti_enabled']:raw['memory'][key]=False
    raw['memory'].update(mem0_base_url='http://127.0.0.1:9',neo4j_uri='bolt://127.0.0.1:9',chromadb_path='/work/synthetic-memory',index_paths=[],neo4j_password_env='SYNTHETIC_UNUSED')
    raw['comms'].update(discord_enabled=False,telegram_enabled=False,discord_token='',telegram_token='',discord_channel_id='',telegram_chat_id='')
    raw['agent']['hermes_enabled']=False
    raw['tools']['obsidian_enabled']=False
    raw['tools']['obsidian_vault_path']='/work/synthetic-vault'
    raw['boot']['enabled']=False
    for name in raw['paths']:raw['paths'][name]='/work/synthetic-'+name
    raw['logging'].update(audit_log='/work/synthetic-audit.jsonl',log_file='/work/synthetic-app.log',log_to_file=False)
    raw['openjarvis'].update(trace_logging_enabled=False,optimization_enabled=False,traces_dir='/work/synthetic-traces')
    (project/'config.yaml').write_text(json.dumps(raw))
    report['synthetic_config_sha256']=hashlib.sha256((project/'config.yaml').read_bytes()).hexdigest()
    sys.path.insert(0,str(project))
    sys.path.insert(0,'/input')
    shutil.copytree('/input/repository',project,dirs_exist_ok=True)
    os.chdir(project)
    sys.path.insert(0,str(project/'tests'))
    mode=Path('/input/mode.txt').read_text()
    import pytest
    report['collection_errors']=[];report['deselected']=[];report['collected_nodes']=[];report['outcomes']=[]
    class Results:
        def pytest_collectreport(self,report):
            if report.failed:globals()['report']['collection_errors'].append({'nodeid':report.nodeid,'error':str(report.longrepr)})
        def pytest_collection_finish(self,session):
            report['collected_nodes']=[{'nodeid':i.nodeid,'markers':sorted(m.name for m in i.iter_markers())} for i in session.items]
        def pytest_deselected(self,items):report['deselected'].extend(i.nodeid for i in items)
        def pytest_runtest_logreport(self,r):
            if r.when=='call' or r.failed or r.skipped:report['outcomes'].append({'nodeid':r.nodeid,'when':r.when,'outcome':r.outcome,'details':str(r.longrepr) if r.longrepr else None})
        def pytest_sessionfinish(self,session,exitstatus):report['tests']={'collected':session.testscollected,'failed':session.testsfailed,'exitstatus':int(exitstatus)}
    args=['-q','-p','pytest_asyncio.plugin','-p','no:cacheprovider','--continue-on-collection-errors','--basetemp=/work/broad-tmp','--import-mode=importlib']
    if mode=='broad-collect':args+=['--collect-only','-o','addopts=']
    # Inventory mode deliberately attempts every module; execution classifications
    # are based on its recorded results, not imports on the real host.
    if mode!='broad-collect':
        selected=json.loads(Path('/input/selection.json').read_text());args+=selected[mode]
    else:args+=['tests']
    code=pytest.main(args,plugins=[Results()])
    report['status']='BROAD_PASS' if code==0 else 'BROAD_INCOMPLETE'
except BaseException as exc:
    report.update(status='ERROR',exception=type(exc).__name__,message=str(exc),traceback=traceback.format_exc())
report['finished_at']=datetime.now(UTC).isoformat()
Path('/work/RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='BROAD_PASS' else 1)
