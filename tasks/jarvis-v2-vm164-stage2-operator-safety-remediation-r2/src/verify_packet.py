"""Read-only integrity verification. Does not execute host or test commands."""
import json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import need,sha,canonical
import packet
ROOT=Path(__file__).resolve().parents[1]
def inventory(root,exclude=()):
 result={}
 for path in sorted(root.rglob('*')):
  need(not path.is_symlink(),'packet symlink')
  if path.is_file() and path.relative_to(root).as_posix() not in exclude:
   raw=path.read_bytes();result[path.relative_to(root).as_posix()]={'sha256':sha(raw),'bytes':len(raw)}
 return result

def verify():
 manifest_raw=(ROOT/'MANIFEST.json').read_bytes();manifest=json.loads(manifest_raw);seal=json.loads((ROOT/'SEAL.json').read_bytes())
 need(seal['manifest_sha256']==sha(manifest_raw),'manifest seal')
 need(manifest['files']==inventory(ROOT,('MANIFEST.json','SEAL.json')),'packet file integrity')
 sources=json.loads((ROOT/'SOURCE-MANIFEST.json').read_bytes())
 need(sources['stage2_source_sha256']==packet.source_hash()==seal['stage2_source_sha256'],'R2 source pin')
 actual_sources={p.name:sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('*.py'))}
 need(sources['files']==actual_sources,'source manifest')
 predecessors=json.loads((ROOT/'evidence/PREDECESSOR-INVENTORY.json').read_bytes())
 for name,expected in predecessors.items():need(inventory(ROOT.parent/name)==expected,'predecessor altered')
 canary=ROOT.parent/'jarvis-v2-vm164-trusted-bootstrap-host-enforcement-r3/src/stage2_canary.py'
 need(sha(canary.read_bytes())==packet.CALLBACK_PIN,'callback pin')
 first=json.loads((ROOT/'FIRST-SUPERVISED-ACTION.json').read_bytes())
 prior=json.loads((ROOT.parent/'jarvis-v2-vm164-stage2-operator-safety-audit-r1/FIRST-SUPERVISED-ACTION.json').read_bytes())
 need(first==prior and first['argv']==['/usr/bin/python3','-I','-B','-S','-c',packet.CLOCK_CODE],'first action changed')
 return dict(status='PASS_OFFLINE_INTEGRITY',payload_files=len(manifest['files']),predecessors={k:len(v) for k,v in predecessors.items()},stage2_source_sha256=packet.source_hash(),manifest_sha256=sha(manifest_raw),live_action=False)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
