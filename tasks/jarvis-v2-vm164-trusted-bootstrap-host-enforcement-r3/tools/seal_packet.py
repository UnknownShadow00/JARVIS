"""Create exclusive local integrity seal; never replace a previous seal."""
import hashlib,importlib.util,json
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 s=importlib.util.spec_from_file_location('r3_local_verify',TASK/'tools/verify_packet.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
 if (TASK/'MANIFEST.json').exists() or (TASK/'SEAL.json').exists():raise SystemExit('SEALED_NO_OVERWRITE')
 v.predecessors();v.source_and_archive();raw=(json.dumps(v.inventory(),indent=2,sort_keys=True)+'\n').encode()
 with (TASK/'MANIFEST.json').open('xb') as f:f.write(raw)
 result={'manifest_sha256':hashlib.sha256(raw).hexdigest(),'status':'PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY','signature':False,'root_boot_go':False,'live_qualification':False}
 with (TASK/'SEAL.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result,indent=2))
