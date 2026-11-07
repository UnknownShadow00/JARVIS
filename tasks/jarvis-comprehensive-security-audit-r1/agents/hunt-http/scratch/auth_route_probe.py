"""Synthetic route-layer check only; does not establish stock lifespan reachability."""
import json
from pathlib import Path
from uuid import uuid4
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.memory.mem0_enabled=False
settings.memory.chromadb_enabled=False
settings.memory.graphiti_enabled=False
from app.agent import runtime
from synthetic_authority import fixture_authority
from fastapi.testclient import TestClient
from app.server import app
from app.logs.audit import audit

# No context manager: no lifespan, model calls, schedulers, voice or execution.
# This intentionally models a separately admitted/bound authority only.
a=fixture_authority('/scratch/authority/state.sqlite')
runtime.bind_authority(a)
owner_id=str(uuid4())
created=a.submit(runtime.SERVICE_ACTOR,owner_id,'synthetic-owner-goal')
task_id=created['result']['task_id']
client=TestClient(app,base_url='http://untrusted.invalid')
settings.server.api_token=''
get_response=client.get('/tasks/'+task_id,headers={'Origin':'http://untrusted.invalid'})
cancel_response=client.delete('/tasks/'+task_id,params={'request_id':str(uuid4())},headers={'Origin':'http://untrusted.invalid'})
operator_response=client.get('/operator/diagnostics')
settings.server.api_token='synthetic-test-token'
protected=client.get('/tasks/'+task_id)
authorized=client.get('/tasks/'+task_id,headers={'Authorization':'Bearer synthetic-test-token'})
print(json.dumps({'mode':'synthetically-bound-authority-lifespan-skipped','unauthenticated_read_status':get_response.status_code,'read_goal':get_response.json().get('goal'),'unauthenticated_cancel_status':cancel_response.status_code,'cancelled_status':a.get_task(runtime.SERVICE_ACTOR,task_id)['status'],'operator_diagnostics_status_empty_token':operator_response.status_code,'configured_token_missing_header_status':protected.status_code,'configured_token_valid_header_status':authorized.status_code},sort_keys=True))
runtime.close_authority()
audit._shutdown()
