"""Four integrated scenario groups, same history, isolated synthetic scratch only."""
import asyncio,json
from pathlib import Path
from app.config import settings
settings.logging.audit_log='/scratch/work/synthetic-audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.server.enable_voice_on_startup=False
settings.server.enable_hotkey_listener=False
settings.memory.mem0_enabled=False
settings.memory.chromadb_enabled=False
settings.memory.graphiti_enabled=False
from app import server
from app.agent import runtime
from app.logs.audit import audit
import integration_application
async def noop(*args,**kwargs):pass
server._log_startup_checks=lambda:None
server._register_runtime_callbacks=lambda *args:None
server.resource_manager.start_idle_monitor=noop
server.resource_manager.stop_idle_monitor=noop
server.resource_manager.mark_activity=lambda *args:None
server.tts.stop=lambda:None
try:
 groups=asyncio.run(integration_application.run(server.app,server,runtime))
 demo=json.loads(Path('/scratch/work/INTEGRATED-DEMONSTRATION.json').read_text())
 assert runtime._authority is None and runtime._execution_worker is None
 print(json.dumps({'passed_scenario_groups':groups,'fixture_mode':'Existing Sprint6 fixture; scratch path adapted only; unrelated housekeeping inert; real product authorization/durability/recovery unchanged','demonstration':demo},sort_keys=True))
finally:audit._shutdown()
