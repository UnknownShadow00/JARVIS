"""Read-only independent ISO structure/member verification via pinned reader."""
import hashlib,importlib.util,json
from pathlib import Path
TASK=Path(__file__).resolve().parents[1]
def check():
    old=TASK.parent/'jarvis-v2-vm164-trusted-bootstrap-r1/tools/check_media.py'
    expected=json.loads((TASK/'evidence/ENTRY.json').read_text())['predecessor_files'][str(old.relative_to(TASK.parents[1]))]
    if hashlib.sha256(old.read_bytes()).hexdigest()!=expected:raise ValueError('reader_pin')
    spec=importlib.util.spec_from_file_location('pinned_iso_reader',old);reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
    path=TASK/'media-build-5';delivery=json.loads((path/'DELIVERY.json').read_text())
    r=reader.check(path/'probe-data.iso',delivery)
    if (path/'probe-data.iso').read_bytes()!=(TASK/'media-build-6/probe-data.iso').read_bytes():raise ValueError('nonreproducible_media')
    if hashlib.sha256((TASK/'payload/BOOT.PY').read_bytes()).hexdigest()!=delivery['files']['BOOT.PY']:raise ValueError('source_media_disagree')
    r.update(reproducible_builds=[5,6],root_boot_go=False,installation_qualified=False,
             approved_or_attached=False)
    return r
if __name__=='__main__':print(json.dumps(check(),indent=2))
