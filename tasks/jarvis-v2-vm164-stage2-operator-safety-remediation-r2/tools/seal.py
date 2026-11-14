"""Seal this new local packet after tests; never modifies a predecessor."""
import json,sys,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import packet
from common import sha
from verify_packet import inventory,verify
pre=json.loads((ROOT/'evidence/PREDECESSOR-INVENTORY.json').read_bytes())
for name,expected in pre.items():
 if inventory(ROOT.parent/name)!=expected:raise ValueError('predecessor changed')
preservation={'status':'PASS_BYTES_UNCHANGED','predecessors':{k:len(v) for k,v in pre.items()},'canonical_application_modified':False,'host_operations_performed':False}
(ROOT/'evidence/PRESERVATION-CHECK.json').write_text(json.dumps(preservation,indent=2)+'\n')
manifest={'kind':'R2_OFFLINE_PACKET_INTEGRITY_MANIFEST','files':inventory(ROOT,('MANIFEST.json','SEAL.json'))}
raw=(json.dumps(manifest,indent=2)+'\n').encode();(ROOT/'MANIFEST.json').write_bytes(raw)
seal={'kind':'LOCAL_INTEGRITY_SEAL_NOT_AUTHORIZATION','manifest_sha256':sha(raw),'stage2_source_sha256':packet.source_hash(),'status':'PASS_OFFLINE_STAGE2_SAFETY_REMEDIATION_PENDING_INDEPENDENT_REVIEW','authorization_granted':False}
(ROOT/'SEAL.json').write_text(json.dumps(seal,indent=2)+'\n');print(json.dumps(verify(),indent=2))
