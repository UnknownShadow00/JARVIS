import sys,json,importlib.metadata
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
