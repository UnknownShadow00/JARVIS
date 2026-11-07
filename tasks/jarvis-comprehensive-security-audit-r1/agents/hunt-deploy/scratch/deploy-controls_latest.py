"""Parent sandbox only: public config variants and mocked CLI HTTP401 behavior."""
import os,json
from pathlib import Path
import yaml
from app.config import load_settings,settings
from pydantic import ValidationError
raw=yaml.safe_load(Path('/target/config.yaml.example').read_text())
out={}
def check(name,server):
 body=dict(raw);body['server']={**raw['server'],**server}
 p=Path('/scratch/'+name+'.yaml');p.write_text(yaml.safe_dump(body))
 try:load_settings(p)
 except ValueError:out[name]='rejected'
 else:out[name]='accepted'
check('anonymous_loopback',{'host':'127.0.0.1','api_token':'','remote_access_enabled':False})
check('anonymous_remote',{'host':'0.0.0.0','api_token':'','remote_access_enabled':True})
check('wildcard_cors',{'host':'127.0.0.1','cors_origins':['*']})
check('foreign_cors_local',{'host':'127.0.0.1','remote_access_enabled':False,'cors_origins':['https://foreign.invalid']})
check('token_remote',{'host':'0.0.0.0','api_token':'dummy-config-token','remote_access_enabled':True})
body=dict(raw);body['server']={**raw['server'],'api_token':'dummy-yaml-token'}
p=Path('/scratch/precedence.yaml');p.write_text(yaml.safe_dump(body))
os.environ['JARVIS_API_TOKEN']='';out['blank_environment_preserves_yaml_token']=load_settings(p).server.api_token=='dummy-yaml-token'
os.environ['JARVIS_API_TOKEN']='dummy-env-token';out['nonempty_environment_overrides_yaml']=load_settings(p).server.api_token=='dummy-env-token'
os.environ.pop('JARVIS_API_TOKEN',None)
settings.logging.audit_log='/scratch/audit.jsonl';settings.openjarvis.trace_logging_enabled=False
from app import cli
from types import SimpleNamespace
from app.logs.audit import audit
calls=[]
def post(url,**kwargs):
 calls.append({'url':url,'has_headers':bool(kwargs.get('headers'))})
 class Reply:
  def raise_for_status(self):raise RuntimeError('synthetic401')
 return Reply()
async def local():
 calls.append({'local_fallback':True});return {'state':'LIGHT_SLEEP','actions':['dummy-only']}
cli.httpx.post=post;cli._local_light_sleep=local
settings.server.api_token='dummy-configured-token'
cli._sleep(SimpleNamespace(light=True))
out['cli_post_401_shape']=calls
print(json.dumps(out,sort_keys=True))
audit._shutdown()
