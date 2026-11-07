"""Bounded synthetic checks only: dummy tool and scratch-local note, no providers."""
import asyncio,json
from pathlib import Path
from types import SimpleNamespace
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.memory.mem0_enabled=settings.memory.chromadb_enabled=settings.memory.graphiti_enabled=False
settings.routing.embedding_enabled=False
settings.comms.discord_enabled=settings.comms.telegram_enabled=False
settings.comms.discord_channel_id=settings.comms.telegram_chat_id=''
settings.safety.dry_run=False
settings.safety.approval_mode='balanced'
settings.server.api_token='synthetic-audit-token'
settings.tools.obsidian_enabled=False
settings.tools.obsidian_vault_path='/scratch/vault'
from app import server
from app.brain import kill_switch
from app.brain.llm_client import OllamaConnectionError
from app.logs.audit import audit
from fastapi.testclient import TestClient
server.filler_manager.play_for_tool=lambda _: None
calls=[]
server.registry._tools['shell']=SimpleNamespace(SAFETY_LEVEL=2,DESCRIPTION='Dummy audit tool only',execute=lambda p:calls.append(dict(p)) or 'dummy-marker')
async def normal_reply(*a,**k):return 'Please approve, sir.'
server.llm_client.chat=normal_reply
async def pending():
 kill_switch.reset()
 await server._process('run harmless-audit-command')
asyncio.run(pending())
assert len(server._pending_confirmations)==1
rid=next(iter(server._pending_confirmations))
kill_switch.trigger('synthetic local operator emergency stop')
active_before=kill_switch.is_active()
client=TestClient(server.app)
response=client.post('/confirm/'+rid,headers={'Authorization':'Bearer synthetic-audit-token'})
kill_result={'mode':'route-only-lifespan-skipped','active_before_confirmation':active_before,'http_status':response.status_code,'confirmed':response.json().get('confirmed'),'dummy_effect_count':len(calls),'active_after_confirmation':kill_switch.is_active()}
kill_switch.reset()
async def offline_reply(*a,**k):raise OllamaConnectionError('synthetic model unavailable')
server.llm_client.chat=offline_reply
async def duplicate_note():
 msg='[ACTION:OBSIDIAN:note_append:Audit note]single-marker'
 result=await server._process_stream(msg)
 assert result is None
 first=(Path('/scratch/vault')/'Audit note.md').read_text()
 await server._process(msg)  # exact fallback chosen by WS and voice callers
 second=(Path('/scratch/vault')/'Audit note.md').read_text()
 return {'stream_returned_none':True,'marker_count_after_stream':first.count('single-marker'),'marker_count_after_native_fallback':second.count('single-marker'),'note_text':second,'safety_mode':settings.safety.approval_mode}
print(json.dumps({'kill_switch_confirmation':kill_result,'stream_fallback_note':asyncio.run(duplicate_note())},sort_keys=True))
audit._shutdown()
