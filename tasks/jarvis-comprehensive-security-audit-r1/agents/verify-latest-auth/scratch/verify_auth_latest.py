"""Parent-only bounded verification; no providers, live sockets or real state."""
import json
from pathlib import Path
from uuid import uuid4
from app.config import settings
settings.logging.audit_log='/scratch/verification-audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.memory.mem0_enabled=False
settings.memory.chromadb_enabled=False
settings.memory.graphiti_enabled=False
settings.server.enable_voice_on_startup=False
settings.server.enable_hotkey_listener=False
from app.agent import runtime
from app.agent.authority import AuthorityError
from app import server
from app.logs.audit import audit
from fastapi.testclient import TestClient
from synthetic_authority import fixture_authority

assert runtime._authority is None
stock_database=runtime.PROJECT_ROOT/'data/authority/queue.sqlite'
assert not stock_database.exists()
startup_error=None
try:
    with TestClient(server.app):
        raise AssertionError('stock source startup unexpectedly admitted')
except AuthorityError as exc:
    startup_error=exc.code
assert startup_error=='authority_unenrolled_or_missing'
assert runtime._authority is None and not stock_database.exists()

# This explicit synthetic compatibility approval is not ordinary startup.
a=fixture_authority('/scratch/verification-authority/state.sqlite')
runtime.bind_authority(a)
try:
    operation=str(uuid4())
    created=a.submit(runtime.SERVICE_ACTOR,operation,'dummy operator-owned task')
    task_id=created['result']['task_id']
    client=TestClient(server.app,base_url='http://untrusted.invalid')
    foreign={'Origin':'https://untrusted.example'}
    settings.server.api_token=''
    read=client.get('/tasks/'+task_id,headers=foreign)
    cancelled=client.delete('/tasks/'+task_id,params={'request_id':str(uuid4())},headers=foreign)
    diagnostics=client.get('/operator/diagnostics')
    settings.server.api_token='synthetic-verifier-token'
    refused=client.get('/tasks/'+task_id)
    accepted=client.get('/tasks/'+task_id,headers={'Authorization':'Bearer synthetic-verifier-token'})
    out={'stock_lifespan_error':startup_error,'stock_database_created':stock_database.exists(),
         'conditional_fixture':'explicitly bound synthetic authority; route checks skip lifespan',
         'arbitrary_host_and_origin_native_read':read.status_code,
         'arbitrary_host_and_origin_native_cancel':cancelled.status_code,
         'dummy_task_state':a.get_task(runtime.SERVICE_ACTOR,task_id)['status'],
         'operator_diagnostics_empty_token':diagnostics.status_code,
         'configured_token_missing_header':refused.status_code,
         'configured_token_valid_header':accepted.status_code,
         'real_socket_or_browser_or_other_uid_tested':False}
    assert out['arbitrary_host_and_origin_native_read']==200 and out['arbitrary_host_and_origin_native_cancel']==200
    assert out['dummy_task_state']=='cancelled'
    assert (diagnostics.status_code,refused.status_code,accepted.status_code)==(401,401,200)
    print(json.dumps(out,sort_keys=True))
finally:
    runtime.close_authority()
    audit._shutdown()
