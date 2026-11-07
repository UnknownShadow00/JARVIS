"""Run only through sandbox-runner: real isolated socket, dummy admitted state."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from uuid import uuid4

from app.config import settings

settings.logging.audit_log = "/scratch/authority-audit.jsonl"
settings.openjarvis.trace_logging_enabled = False
settings.server.enable_voice_on_startup = False
settings.server.enable_hotkey_listener = False
settings.memory.mem0_enabled = False
settings.memory.chromadb_enabled = False
settings.memory.graphiti_enabled = False

from app import server
from app.agent import runtime
from app.agent.authority import AuthorityError
from app.logs.audit import audit
from synthetic_authority import fixture_authority
import uvicorn


CLIENT = r'''
import http.client,json,os,sys,uuid
input=json.load(sys.stdin);port=input['port'];key=input['key'];task=input['task']
def request(method,path,headers=None):
    conn=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
    try:
        conn.request(method,path,headers=headers or {})
        result=conn.getresponse();body=result.read(65536)
        return {'status':result.status,'allow_origin':result.getheader('access-control-allow-origin'),
                'dummy_credential_reflected':bool(key and key.encode() in body)}
    finally:conn.close()
headers={'Authorization':'Bearer '+key} if key else {}
path='/tasks/'+task
result={
 'client_uid':os.getuid(),
 'missing':request('GET',path),
 'wrong':request('GET',path,{'Authorization':'Bearer wrong-dummy-key'}),
 'malformed':request('GET',path,{'Authorization':'not-a-bearer'}),
 'query_only':request('GET',path+'?token=synthetic-query-value'),
 'foreign_host_origin_missing':request('GET',path,{'Host':'foreign.invalid','Origin':'https://foreign.invalid'}),
 'identity_control':request('GET',path,headers),
 'foreign_origin_with_identity':request('GET',path,{**headers,'Origin':'https://foreign.invalid'}),
 'foreign_preflight':request('OPTIONS',path,{**headers,'Origin':'https://foreign.invalid',
    'Access-Control-Request-Method':'DELETE','Access-Control-Request-Headers':'Authorization'}),
 'cancel_missing':request('DELETE',path+'?request_id='+str(uuid.uuid4())),
 'health':request('GET','/health'),
}
if key:result['cancel_valid']=request('DELETE',path+'?request_id='+str(uuid.uuid4()),headers)
print(json.dumps(result,sort_keys=True))
'''


async def noop(*args, **kwargs):
    pass


async def probe(label, key):
    assert runtime._authority is None and runtime._execution_worker is None
    settings.server.api_token = key
    authority = fixture_authority(Path("/scratch") / label / "state.sqlite")
    runtime.bind_authority(authority)
    operation = str(uuid4())
    authority.submit(runtime.SERVICE_ACTOR, operation, "dummy operator-owned task")
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))
    listener.listen(8)
    port = listener.getsockname()[1]
    config = uvicorn.Config(server.app, loop="asyncio", lifespan="on", ws="none",
                            log_config=None, log_level="critical", access_log=False,
                            timeout_keep_alive=1, limit_concurrency=8)
    service = uvicorn.Server(config)
    running = asyncio.create_task(service.serve(sockets=[listener]))
    try:
        for _ in range(200):
            if service.started:
                break
            if running.done():
                await running
                raise AssertionError("synthetic server did not start")
            await asyncio.sleep(0.01)
        assert service.started
        child = await asyncio.create_subprocess_exec(
            sys.executable, "-I", "-S", "-c", CLIENT,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        output, error = await asyncio.wait_for(child.communicate(json.dumps({
            "port": port, "key": key, "task": operation,
        }).encode()), timeout=8)
        assert child.returncode == 0, error.decode()
        observations = json.loads(output)
        observations.update(
            mode=label, genuine_lifespan_started=True,
            server_uid=os.getuid(), distinct_process=True,
            distinct_uid=False, no_actual_browser=True,
            task_status_after_requests=authority.get_task(runtime.SERVICE_ACTOR, operation)["status"],
        )
        return observations
    finally:
        service.should_exit = True
        await asyncio.wait_for(running, timeout=4)
        listener.close()
        assert runtime._authority is None


async def main():
    # These substitute only unrelated provider/hardware/background housekeeping.
    # Real Authority admission, scheduler, HTTP server and route policies run.
    server._log_startup_checks = lambda: None
    server._register_runtime_callbacks = lambda *args: None
    server.resource_manager.start_idle_monitor = noop
    server.resource_manager.stop_idle_monitor = noop
    server.resource_manager.mark_activity = lambda *args: None
    server.tts.stop = lambda: None
    runtime.PROJECT_ROOT = Path("/scratch/unprovisioned-stock")
    settings.server.api_token = ""
    stock_error = None
    try:
        async with server.app.router.lifespan_context(server.app):
            raise AssertionError("unprovisioned startup admitted")
    except AuthorityError as exc:
        stock_error = exc.code
    assert stock_error == "authority_unenrolled_or_missing"
    assert not runtime.PROJECT_ROOT.exists()
    results = [await probe("admitted-empty-token", ""),
               await probe("admitted-configured-token", "synthetic-socket-probe-token")]
    assert all(not item["dummy_credential_reflected"] for row in results for item in row.values() if isinstance(item, dict))
    print(json.dumps({"stock_startup_error": stock_error, "stock_database_created": False,
                      "network_scope": "bwrap unshared network namespace; ephemeral loopback socket only",
                      "results": results}, sort_keys=True))


try:
    asyncio.run(main())
finally:
    audit._shutdown()
