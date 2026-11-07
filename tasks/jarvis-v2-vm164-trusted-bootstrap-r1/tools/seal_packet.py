"""Create exclusive local hash seal AFTER all preparation artifacts are final."""
import hashlib,importlib.util,json
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
if __name__=='__main__':
 spec=importlib.util.spec_from_file_location('verify',TASK/'tools/verify_packet.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
 assert not (TASK/'MANIFEST.json').exists() and not (TASK/'SEAL.json').exists(),'ALREADY_SEALED_NO_OVERWRITE'
 raw=(json.dumps(v.inventory(),indent=2,sort_keys=True)+'\n').encode()
 with (TASK/'MANIFEST.json').open('xb') as f:f.write(raw)
 d={'manifest_sha256':hashlib.sha256(raw).hexdigest(),'cryptographic_signature':False,'scope':'local preparation artifacts, not guest results','vm_operation_performed':False}
 with (TASK/'SEAL.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
 print(json.dumps(d,indent=2))
