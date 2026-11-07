"""Three tiny in-memory sessions; no lifespan, providers, sockets or real state."""
import json
from app.config import settings
settings.logging.audit_log='/scratch/ws-audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.memory.mem0_enabled=settings.memory.chromadb_enabled=settings.memory.graphiti_enabled=False
settings.server.api_token='synthetic-ws-token'
from app import server
from app.logs.audit import audit
from fastapi.testclient import TestClient

async def awake(_): return True
server.resource_manager.ensure_awake_for_interaction=awake
client=TestClient(server.app)
headers={'Authorization':'Bearer synthetic-ws-token'}
results=[]
for payload in ['[]', '{"message": []}']:
    server.manager.active.clear()
    error=None
    try:
        with client.websocket_connect('/ws',headers=headers) as ws:
            ws.send_text(payload)
            # The ASGI task terminates immediately for the malformed native shape.
            ws.receive_json()
    except Exception as exc:
        error=type(exc).__name__
    results.append({'payload':payload,'exception':error,'retained_after_session':len(server.manager.active)})
server.manager.active.clear()
with client.websocket_connect('/ws',headers=headers):
    pass
results.append({'normal_disconnect_retained':len(server.manager.active)})
server.manager.active.clear()
print(json.dumps({'mode':'TestClient-no-lifespan-no-network','sessions':results},sort_keys=True))
audit._shutdown()
