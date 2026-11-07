"""Two in-memory dummy sessions; no lifespan, socket or real state."""
import json
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.server.api_token='synthetic-ue5-token'
from app import server
from app.comms.ue5_bridge import ue5_manager
from app.logs.audit import audit
from fastapi.testclient import TestClient
client=TestClient(server.app)
headers={'Authorization':'Bearer synthetic-ue5-token'}
ue5_manager.active.clear();failure=None
try:
    with client.websocket_connect('/ue5',headers=headers) as ws:
        ws.send_bytes(b'x')
        ws.receive_json()
except Exception as exc:
    failure=type(exc).__name__
retained=len(ue5_manager.active)
ue5_manager.active.clear()
with client.websocket_connect('/ue5',headers=headers):pass
normal=len(ue5_manager.active)
ue5_manager.active.clear()
assert failure=='KeyError' and retained==1 and normal==0
print(json.dumps({'fixture':'two-in-memory-credentialed-ue5-sessions-no-lifespan','binary_payload_hex':'78','exception':failure,'retained_after_binary_session':retained,'retained_after_normal_disconnect':normal,'no_socket_browser_other_uid_or_shared_outage_test':True},sort_keys=True))
audit._shutdown()
