"""Create an exclusive local hash manifest after all engineering is complete."""
import hashlib,importlib.util,json
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
if __name__=='__main__':
    s=importlib.util.spec_from_file_location('verify_r2_for_seal',TASK/'tools/verify_packet.py')
    v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
    if (TASK/'MANIFEST.json').exists() or (TASK/'SEAL.json').exists():raise SystemExit('ALREADY_SEALED_NO_OVERWRITE')
    v.predecessors();v.candidate()
    raw=(json.dumps(v.inventory(),indent=2,sort_keys=True)+'\n').encode()
    with (TASK/'MANIFEST.json').open('xb') as f:f.write(raw)
    d={'manifest_sha256':hashlib.sha256(raw).hexdigest(),'signature':False,
       'scope':'offline candidate, not live authorization','root_boot_go':False}
    with (TASK/'SEAL.json').open('x') as f:json.dump(d,f,indent=2);f.write('\n')
    print(json.dumps(d,indent=2))
