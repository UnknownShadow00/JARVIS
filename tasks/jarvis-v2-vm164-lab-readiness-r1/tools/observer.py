"""Pinned existing GET-only observer; sanitized diagnostics, no credential output."""
import contextlib,hashlib,http.client,io,json,os,runpy,socket,sys
from datetime import datetime,UTC
from pathlib import Path
CLIENT=Path('/home/nexus/.local/bin/g6k-pve164-readonly')
CLIENT_PIN='5a6d834d5d1941eb34483aa81a8a856186c0fe3f237f33451b3d680e1dde5e7a'
ORIGINAL=Path(__file__).resolve().parents[2]/'proxmox-automation-phase2/tools/observe.py'
ORIGINAL_PIN='953d14138d1f512c622363c95ec60e0891a4047fd0c08457ceebf3ca3777d9c0'
ALLOWED={'/api2/json/version','/api2/json/access/permissions','/api2/json/nodes/pve/qemu/164/config','/api2/json/nodes/pve/qemu/164/status/current'}
def main():
 calls=[];statuses=[];original_request=http.client.HTTPConnection.request;original_response=http.client.HTTPConnection.getresponse
 def request(self,method,url,*args,**kwargs):
  if method!='GET' or url not in ALLOWED:raise PermissionError('observer_scope_refusal')
  calls.append({'method':'GET','path':url})
  return original_request(self,method,url,*args,**kwargs)
 def response(self,*a,**kw):
  r=original_response(self,*a,**kw);statuses.append(r.status);return r
 result={'observed_at_utc':datetime.now(UTC).isoformat(),'status':'BLOCKED','credential_or_permission_changes':False,'guest_console_or_mutation_calls':0}
 try:
  if hashlib.sha256(ORIGINAL.read_bytes()).hexdigest()!=ORIGINAL_PIN:raise PermissionError('observer_wrapper_pin_refusal')
  if hashlib.sha256(CLIENT.read_bytes()).hexdigest()!=CLIENT_PIN:raise PermissionError('observer_pin_refusal')
  http.client.HTTPConnection.request=request;http.client.HTTPConnection.getresponse=response
  out=io.StringIO()
  with contextlib.redirect_stdout(out),contextlib.redirect_stderr(io.StringIO()):
   module=runpy.run_path(str(ORIGINAL));module['main']()
  result.update(status='OBSERVED_READ_ONLY',observation=json.loads(out.getvalue()))
 except (Exception,SystemExit) as e:
  # Only class and numeric errno escape; never print messages, response bodies,
  # module globals, Authorization headers, token paths or captured stdout.
  result['failure_class']=type(e).__name__;result['errno']=getattr(e,'errno',None)
 finally:
  http.client.HTTPConnection.request=original_request;http.client.HTTPConnection.getresponse=original_response
  result.update(client_sha256=hashlib.sha256(CLIENT.read_bytes()).hexdigest(),allowed_requests_attempted=calls,http_statuses=statuses)
 print(json.dumps(result,indent=2,sort_keys=True));return 0 if result['status']=='OBSERVED_READ_ONLY' else 1
if __name__=='__main__':raise SystemExit(main())
