"""Validate retained CycloneDX schemas offline using already-qualified local tools."""
from pathlib import Path
import json,hashlib,subprocess,os,resource,datetime
P=Path(__file__).resolve().parents[1]
TARGET=Path('/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages')
def main():
 run=P/'runs'/('sbom-'+datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%S%fZ'));run.mkdir(mode=0o700)
 source=run/'child.py';source.write_text('''import sys,json,importlib.metadata
from pathlib import Path
sys.path.insert(0,'/deps')
import jsonschema
from referencing import Registry,Resource
root=Path('/input/evidence/sbom-schemas');store={}
for name in ['bom-1.6.schema.json','spdx.schema.json','jsf-0.82.schema.json']:
 data=json.loads((root/name).read_text());resource=Resource.from_contents(data)
 for protocol in ['http','https']:store[protocol+'://cyclonedx.org/schema/'+name]=resource
registry=Registry().with_resources(store.items())
bom=json.loads(Path('/input/SBOM.cdx.json').read_text())
jsonschema.Draft7Validator(json.loads((root/'bom-1.6.schema.json').read_text()),registry=registry).validate(bom)
refs=[x['bom-ref'] for x in bom['components']];assert len(set(refs))==len(refs)
assert all(x in refs for d in bom['dependencies'] for x in d['dependsOn'])
print(json.dumps({'status':'PASS_CYCLONEDX_1_6_SCHEMA','jsonschema_version':importlib.metadata.version('jsonschema'),'components':len(refs),'network_resolution':False,'licenses_unknown_when_not_declared':True}))
''')
 argv=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--setenv','PATH','/usr/bin:/bin','--ro-bind','/usr','/usr','--ro-bind','/lib','/lib','--ro-bind','/lib64','/lib64','--ro-bind',str(P),'/input','--ro-bind',str(TARGET),'/deps','--ro-bind',str(source),'/child.py','--proc','/proc','--dev','/dev','--tmpfs','/tmp','--chdir','/tmp','--remount-ro','/','--','/usr/bin/python3.14','-I','-B','-S','/child.py']
 def limits():
  resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912));resource.setrlimit(resource.RLIMIT_CPU,(10,10));resource.setrlimit(resource.RLIMIT_CORE,(0,0))
 r=subprocess.run(argv,stdin=subprocess.DEVNULL,capture_output=True,text=True,timeout=20,preexec_fn=limits,env={'PATH':'/usr/bin:/bin'})
 (run/'stdout.txt').write_text(r.stdout);(run/'stderr.txt').write_text(r.stderr)
 result={'exitcode':r.returncode,'run':str(run.relative_to(P)),'result':json.loads(r.stdout) if r.returncode==0 else None,'schema_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (P/'evidence/sbom-schemas').glob('*.schema.json')}}
 (P/'SBOM-VALIDATION.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2));return r.returncode
if __name__=='__main__':raise SystemExit(main())
