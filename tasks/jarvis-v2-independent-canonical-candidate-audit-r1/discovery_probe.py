"""Safe pytest path-discovery probe: original archive code is NEVER imported.

Replaces archived modules with inert sentinel definitions in disposable trees.
Only ordinary collector behavior and an optional prospective guard are tested.
"""
from pathlib import Path
import json
import os
import subprocess
import tempfile

os.umask(0o077)
OUT=Path(__file__).resolve().parent
STATE=json.loads((OUT/'INITIAL-STATE.json').read_text())
SOURCE=Path(STATE['new_detached_audit_checkout'])
DEPS='/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages'
ARCHIVE=Path('tasks/jarvis-v2-baseline-reconciliation-r1/preserved-development-tests')
archive_names=sorted(p.name for p in (SOURCE/ARCHIVE).glob('test_*.py'))
rows=[]
for case in ('before_no_archive','combined_archive_paths','prospective_testpaths_guard'):
 with tempfile.TemporaryDirectory(prefix='jarvis-archive-inert-probe-') as temporary:
  root=Path(temporary);(root/'tests').mkdir();(root/'tests/test_control.py').write_text('def test_control(): pass\n')
  config=(SOURCE/'pytest.ini').read_text()
  if case=='prospective_testpaths_guard':config+='\ntestpaths = tests\n'
  (root/'pytest.ini').write_text(config)
  if case!='before_no_archive':
   (root/ARCHIVE).mkdir(parents=True)
   for name in archive_names:(root/ARCHIVE/name).write_text('def test_archive_path_sentinel(): pass\n')
  runner="""import json,pytest
observed=[]
class Collector:
 def pytest_collection_finish(self,session):observed.extend(i.nodeid for i in session.items)
code=pytest.main(['--collect-only','-p','no:terminal','-p','no:cacheprovider','-c','/fixture/pytest.ini'],plugins=[Collector()])
print(json.dumps({'pytest_exit':int(code),'nodeids':observed}))
"""
  command=['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session','--cap-drop','ALL','--ro-bind','/usr','/usr','--symlink','usr/bin','/bin','--symlink','usr/lib','/lib','--symlink','usr/lib64','/lib64','--ro-bind',DEPS,'/deps','--ro-bind',str(root),'/fixture','--tmpfs','/tmp','--proc','/proc','--dev','/dev','--clearenv','--setenv','PATH','/usr/bin:/bin','--setenv','PYTHONPATH','/deps','--setenv','PYTEST_DISABLE_PLUGIN_AUTOLOAD','1','--setenv','PYTHONDONTWRITEBYTECODE','1','--chdir','/fixture','/usr/bin/python3.14','-B','-c',runner]
  p=subprocess.run(command,capture_output=True,text=True,timeout=30)
  (OUT/(case+'.stdout')).write_text(p.stdout);(OUT/(case+'.stderr')).write_text(p.stderr)
  body=json.loads(p.stdout);count=sum(n.startswith(str(ARCHIVE)+'/') for n in body['nodeids'])
  expected=12 if case=='combined_archive_paths' else 0
  rows.append(dict(case=case,command=command,process_exit=p.returncode,pytest_exit=body['pytest_exit'],observed_nodeids=body['nodeids'],archive_modules_collected=count,expected_archive_count=expected,passed=p.returncode==body['pytest_exit']==0 and count==expected))
(OUT/'DISCOVERY-PROBES.json').write_text(json.dumps({'original_archived_code_executed':False,'inert_probe_only':True,'reviewed_source_modified':False,'archive_test_modules':archive_names,'cases':rows},indent=2))
print([(r['case'],r['archive_modules_collected'],r['passed']) for r in rows])
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
