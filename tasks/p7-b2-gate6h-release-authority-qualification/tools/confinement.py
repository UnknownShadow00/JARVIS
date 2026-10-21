"""Disposable mount confinement at the SAME kernel uid; not privileged DAC proof."""
import json
from pathlib import Path
import subprocess
import tempfile

base = Path(tempfile.mkdtemp(prefix='jarvis-g6h-confinement-'))
base.chmod(0o700)
a = base/'authority'; a.mkdir(mode=0o700)
(a/'state').write_text('protected fixture'); (a/'state').chmod(0o600)
w = base/'work'; w.mkdir(mode=0o700)
script = '''import os,json
from pathlib import Path
r={'kernel_uid':os.getuid(),'uid_map':Path('/proc/self/uid_map').read_text().strip(),'classification':'SAME_KERNEL_UID_MOUNT_CONFINEMENT_NOT_DISTINCT_UID_DAC'}
for name,action in [('write',lambda:Path('/tmp/authority/state').write_text('rollback')),('chmod',lambda:os.chmod('/tmp/authority/state',0o666)),('unlink',lambda:os.unlink('/tmp/authority/state')),('symlink',lambda:os.symlink('/tmp/work/fake','/tmp/authority/link')),('hardlink',lambda:os.link('/tmp/authority/state','/tmp/work/link'))]:
 try: action();r[name]={'denied':False}
 except OSError as e:r[name]={'denied':True,'errno':e.errno}
print(json.dumps(r))
'''
cmd = ['bwrap','--unshare-user','--unshare-net','--die-with-parent','--new-session',
       '--ro-bind','/','/','--tmpfs','/home','--tmpfs','/opt','--tmpfs','/run','--tmpfs','/tmp',
       '--ro-bind',str(a),'/tmp/authority','--bind',str(w),'/tmp/work','--chdir','/tmp/work',
       '--','/usr/bin/python3','-B','-c',script]
p = subprocess.run(cmd,capture_output=True,text=True)
r = {'exit':p.returncode,'stderr':p.stderr,'disposable_root':str(base),
     'result':json.loads(p.stdout) if p.stdout else None,
     'fixture_unchanged':(a/'state').read_text()=='protected fixture'}
print(json.dumps(r,indent=2))
if p.returncode or not all(v['denied'] for k,v in r['result'].items() if isinstance(v,dict)):
    raise SystemExit(1)
