"""Shared-temp path mechanics only; no desktop access and only dummy bytes/files."""
import json,os,tempfile
from pathlib import Path
from types import SimpleNamespace
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
settings.safety.dry_run=False
import mss
from app.computer import screenshot
from app.logs.audit import audit
# Model a shared temp parent; does not claim actual cross-UID qualification.
shared=Path('/scratch/shared');shared.mkdir(mode=0o777);shared.chmod(0o1777)
victim=Path('/scratch/victim');victim.mkdir(mode=0o700)
target=victim/'dummy-config.json';target.write_text('{"dummy":"must survive screenshot"}');target.chmod(0o600)
precreated=shared/'jarvis_screenshots';precreated.mkdir(mode=0o777);precreated.chmod(0o777)
leaf=precreated/'jarvis_shot_FIXED.png';leaf.symlink_to(target)
class FakeCapture:
 monitors=[{'dummy':True}]
 def __enter__(self):return self
 def __exit__(self,*_):pass
 def grab(self,_):return SimpleNamespace(rgb=b'\x00\x00\x00',size=(1,1))
mss.mss=FakeCapture
screenshot.tempfile.gettempdir=lambda:str(shared)
screenshot.time.strftime=lambda _: 'FIXED'
result=screenshot.execute({})
print(json.dumps({'fixture_only_not_cross_uid_qualified':True,'source_output_path':result.get('path'),'leaf_is_symlink':leaf.is_symlink(),'victim_now_png':target.read_bytes().startswith(b'\x89PNG'),'victim_mode':oct(target.stat().st_mode&0o777),'bytes':target.stat().st_size,'hardware_capture_mocked':True,'png_writer':'real mss.tools.to_png'},sort_keys=True))
audit._shutdown()
