"""Parent-only bounded harness: six dummy cases; no effects/providers/hardware."""
import ast
import asyncio
import contextlib
import json
from pathlib import Path
import sys
import types

ROOT = Path('/target')
if not (ROOT / 'app/server.py').is_file():
    ROOT = Path.cwd()
assert (ROOT / 'app/server.py').is_file(), 'run with captured snapshot cwd or /target'

def mod(name, **attrs):
    m = types.ModuleType(name)
    for key, value in attrs.items(): setattr(m, key, value)
    sys.modules[name] = m
    return m

settings = types.SimpleNamespace(safety=types.SimpleNamespace(dry_run=False, approval_mode='balanced'), server=types.SimpleNamespace(ue5_enabled=False))
mod('app', __path__=[])
mod('app.tools', __path__=[])
sys.modules['app'].tools = sys.modules['app.tools']
mod('app.config', settings=settings)
audit_events=[]
mod('app.logs', __path__=[])
mod('app.logs.audit', audit=types.SimpleNamespace(log=lambda *a: audit_events.append(a)))
mod('app.observability', __path__=[])
mod('app.observability.tracing', emit_event=lambda *a, **k: None, trace_span=lambda *a, **k: contextlib.nullcontext())
regns = {'__name__':'dummy_registry'}
exec(compile((ROOT/'app/tools/registry.py').read_text(), 'app/tools/registry.py', 'exec'), regns)
r=regns['ToolRegistry']()
effects=[]
r._tools['shell']=types.SimpleNamespace(execute=lambda p: effects.append(p), SAFETY_LEVEL=0)

def denied(fn):
    try: fn({'command':'DUMMY'})
    except regns['ToolError'] as exc:
        assert str(exc)=='real_execution_disabled_independent_authorization_required'
        return
    raise AssertionError('did not deny')

for confirmed in (False, True):
    for dry in (False, True):
        settings.safety.dry_run=dry
        for mode in ('balanced','safe','strict'):
            settings.safety.approval_mode=mode
            denied(lambda p: r.call('shell',p,confirmed=confirmed))
            denied(lambda p: r.execute('shell',p,confirmed=confirmed))
assert not effects
print(json.dumps({'case':'registry_flags','denied_calls':24,'effects':0}))

for fn in (regns['TOOLS']['shell'],r.TOOLS['shell'],r.get_tool('shell').execute,r.get('shell').execute,r._load_tool('shell').execute): denied(fn)
assert r.get('does-not-exist') is None
assert all(item['execution_enabled'] is False for item in r.list_tools())
assert 'app.tools.shell' not in sys.modules
print(json.dumps({'case':'raw_getters','denied_callbacks':5,'tool_module_imported':False,'effects':0}))

mod('app.brain', __path__=[])
mod('app.brain.router', RouterResult=lambda *a: types.SimpleNamespace(intent=a[0], confidence=a[1]))
mod('app.comms', __path__=[])
mod('app.comms.ue5_bridge', build_emotion_event=lambda e:{},parse_emotion_from_reply=lambda s:None,ue5_manager=types.SimpleNamespace())
server_tree=ast.parse((ROOT/'app/server.py').read_text())
selected=[n for n in server_tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name in ('_process','_process_stream')]
ns={'__name__':'dummy_server','asyncio':asyncio,'settings':settings,'trace_span':lambda *a,**k:contextlib.nullcontext(),'clean':lambda v:v,'_is_cancel_command':lambda s:False,'check_voice':lambda s:False,'is_active':lambda:True,'intent_router':types.SimpleNamespace(classify=lambda text:types.SimpleNamespace(intent=text,confidence=1.0))}
exec(compile(ast.Module(body=selected,type_ignores=[]),'app/server.py','exec'),ns)
async def exercise():
    for intent in ('use_tool','confirm_action','vision'):
        assert await ns['_process_stream'](intent) is None
        reply,result=await ns['_process'](intent)
        assert reply.startswith('Real tool execution is disabled.')
    print(json.dumps({'case':'stream_then_normal','intents':3,'effects':0}))
    ns['is_active']=lambda:False
    reply,_=await ns['_process']('use_tool')
    assert reply=='Standing by, sir.'
    assert await ns['_process_stream']('use_tool') is None
    print(json.dumps({'case':'inactive_pipeline','effects':0}))
asyncio.run(exercise())

# Route inventory only: no FastAPI app import/lifespan and no HTTP execution.
confirm_routes=[]
for n in ast.walk(server_tree):
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in ('post','get','route') and n.args and isinstance(n.args[0],ast.Constant):
        if isinstance(n.args[0].value,str) and n.args[0].value.startswith('/confirm'):confirm_routes.append(n.args[0].value)
assert not confirm_routes
print(json.dumps({'case':'confirmation_route_inventory','routes':confirm_routes}))

dns={'__name__':'dummy_dictation'}
exec(compile((ROOT/'app/voice/dictation.py').read_text(),'app/voice/dictation.py','exec'),dns)
d=dns['Dictation']()
assert d.handle_transcript('DUMMY_SECRET') is False
assert d._write_clipboard('DUMMY_SECRET') is False
assert d._type_out('DUMMY_SECRET') is False
assert 'DUMMY_SECRET' not in repr(audit_events)
print(json.dumps({'case':'dictation','clipboard_effects':0,'typing_effects':0,'raw_transcript_audited':False}))
