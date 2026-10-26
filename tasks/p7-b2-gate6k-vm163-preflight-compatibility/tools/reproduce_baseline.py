"""Read-only reproduction against sealed Gate6K. Never call qualification main."""
import json,subprocess,sys
from pathlib import Path
OLD=Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2')
sys.path.insert(0,str(OLD/'disposable'))
from safety_preflight import validate_environment
root='1 0 8:1 / / rw - ext4 /dev/sda1 rw'
rows=[]
for name,kwargs in [('ordinary_preparation_home',{'credential_paths':['/home/jarvis']}),('empty_systemd_container',{'credential_paths':['/run/credentials']}),('cloud_instance_directory',{'credential_paths':['/var/lib/cloud/instance']}),('separate_private_boot',{'mountinfo':root+'\n2 1 8:2 / /boot rw - ext4 /dev/sda2 rw'})]:
    args=dict(hostname='jarvis-security',interfaces=['lo'],mountinfo=root,credential_paths=[]);args.update(kwargs)
    try:validate_environment(**args);outcome='UNEXPECTED_ACCEPT'
    except RuntimeError as e:outcome=str(e)
    rows.append(dict(case=name,original_outcome=outcome,layer='synthetic metadata argument'))
script='import runpy; runpy.run_path('+repr(str(OLD/'disposable/qualify_all.py'))+',run_name="import_only")'
r=subprocess.run([sys.executable,'-I','-B','-c',script],capture_output=True,text=True,timeout=15)
rows.append(dict(case='isolated_import_only_no_execution',exit=r.returncode,confirmed="No module named 'qualify_multi_uid'" in r.stderr))
assert all(x.get('original_outcome')!='UNEXPECTED_ACCEPT' for x in rows)
assert rows[-1]['confirmed']
output=Path(__file__).resolve().parent.parent/'evidence/baseline-reproductions.json'
with output.open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
print(json.dumps(rows))
