"""Build new, unapproved data-only ISO using retained pinned OFFLINE builder.

No mutation of existing ISO, predecessor packet or anything outside new outdir.
Native xorriso runs inside the predecessor's network-isolated, unprivileged bwrap
invocation. No guest command or service manager is invoked.
"""
import argparse,hashlib,importlib.util,json
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
OLD=TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-r1'
def build(out):
 source=OLD/'tools/build_media.py'
 expected=json.loads((TASK/'evidence/ENTRY.json').read_text())['predecessor_files'][str(source.relative_to(TASK.parents[1]))]
 if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise ValueError('sealed_builder_source_changed')
 spec=importlib.util.spec_from_file_location('old_offline_builder',source);b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
 b.TASK=TASK
 b.build(out.resolve())
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,required=True);build(p.parse_args().out)
