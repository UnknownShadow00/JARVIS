"""Offline artifact builder: writes only this NEW task packet, never host paths."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'tests')];sys.dont_write_bytecode=True
import packet as p,catalog,fixtures,results
from common import canonical,sha

def write(path,value):
 target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(value,indent=2)+'\n')

write('COMMAND-CATALOG.json',catalog.build())
prior=ROOT.parent/'jarvis-v2-vm164-stage2-operator-safety-audit-r1/FIRST-SUPERVISED-ACTION.json'
(ROOT/'FIRST-SUPERVISED-ACTION.json').write_bytes(prior.read_bytes())
write('SOURCE-MANIFEST.json',{'kind':'R2_OFFLINE_SOURCE_MANIFEST','stage2_source_sha256':p.source_hash(),'r3_source_sha256':p.SOURCE_PIN,'callback_sha256':p.CALLBACK_PIN,'files':{f.name:sha(f.read_bytes()) for f in sorted((ROOT/'src').glob('*.py'))}})
r,a=fixtures.record()
write('evidence/SYNTHETIC-12-CASE.json',r)
for path,data in a.items():
 target=ROOT/'evidence/SYNTHETIC-ARTIFACTS'/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o600)
write('evidence/SYNTHETIC-VALIDATION.json',results.validate(r,a,expected_manifest_sha256=r['evidence_manifest_sha256'],expected_packet_manifest_sha256='e'*64))
write('templates/PREFLIGHT-INPUT.json',{'kind':'MANDATORY_STAGE2_PREFLIGHT','authorization_granted':False,'session':{key:None for key in fixtures.session()},'identity':{key:None for key in fixtures.ident()},'sample':None,'collision':None,'occupied':None,'used':None,'notes':'All fresh fields mandatory; historical/source pins require independent verification. Never populate from synthetic fixtures.'})
write('templates/RESULT-NOT-RUN.json',{'kind':'CAPTURED_STAGE2_R2_RESULT','authorization_granted':False,'result':'NOT_RUN','stage2_sha256':p.source_hash(),'source_pin':p.SOURCE_PIN,'callback_pin':p.CALLBACK_PIN,'packet_manifest_sha256':None,'session':None,'identity':None,'operator':None,'independent_reviewer':None,'authorization_reference':None,'expiration_guaranteed':False,'live_qualification':False,'cases':{case:{'status':'NOT_RUN','evidence':None} for case in p.CASES},'closure':None,'evidence_manifest':None,'evidence_manifest_sha256':None})
write('RESULT-SCHEMA.json',{'$schema':'https://json-schema.org/draft/2020-12/schema','title':'R2 mandatory shape; executable cross-binding validation ALSO required','type':'object','required':list(r),'properties':{'kind':{'enum':['SYNTHETIC_STAGE2_R2_RESULT','CAPTURED_STAGE2_R2_RESULT']},'live_qualification':{'const':False},'expiration_guaranteed':{'const':False},'cases':{'type':'object','required':list(p.CASES),'additionalProperties':False,'properties':{case:{'type':'object','required':list(row),'properties':{'status':{'const':results.EXPECTED[case]}}} for case,row in r['cases'].items()}}}})
print(json.dumps({'kind':'ARTIFACTS_BUILT_OFFLINE','stage2_sha256':p.source_hash(),'synthetic_cases':12}))
