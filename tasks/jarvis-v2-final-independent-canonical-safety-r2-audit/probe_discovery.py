"""Independent inert discovery probes; never imports original archived/unsafe code."""
from pathlib import Path
import json, os, subprocess, tempfile, sys, hashlib
A=Path(__file__).resolve().parent
C=Path(json.loads((A/'CHECKOUT.json').read_text())['path'])
D='/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages'
F=Path(tempfile.mkdtemp(prefix='jarvis-inert-pytest-discovery-'))
(F/'conftest.py').write_bytes((C/'conftest.py').read_bytes())
(F/'pytest.ini').write_bytes((C/'pytest.ini').read_bytes())
(F/'tests').mkdir();(F/'tasks/archive').mkdir(parents=True)
marker=F/'IMPORTED'
payload='from pathlib import Path\nPath('+repr(str(marker))+').write_text("INERT_IMPORT_ONLY")\ndef test_inert(): pass\n'
for n in ['tests/test_switch_models.py','tests/test_current.py','tasks/archive/test_old.py']:(F/n).write_text(payload)
(F/'tasks/archive/alternate.ini').write_text('[pytest]\n')
variants=[
 ('root',F,[],{}),('module_tests',F,['tests'],{}),('collect',F,['--collect-only'],{}),
 ('explicit_archive',F,['tasks/archive/test_old.py'],{}),('explicit_unsafe',F,['tests/test_switch_models.py'],{}),
 ('tests_cwd',F/'tests',[],{}),('archive_cwd',F/'tasks/archive',[],{}),
 ('archive_cwd_explicit',F/'tasks/archive',['test_old.py'],{}),
 ('external_cwd_absolute',F.parent,[str(F/'tasks/archive/test_old.py')],{}),
 ('override_empty_config',F,['-c','/dev/null','tasks/archive/test_old.py'],{}),
 ('archive_own_config',F/'tasks/archive',['-c','alternate.ini','test_old.py'],{}),
 ('explicit_rootdir',F,['--rootdir=tasks/archive','tasks/archive/test_old.py'],{}),
 ('env_allow',F,['tasks/archive/test_old.py'],{'JARVIS_ALLOW_PYTEST':'1'}),
 ('env_selection',F,[],{'PYTEST_ADDOPTS':'tasks/archive/test_old.py'}),
 ('deliberate_confcutdir',F,['--confcutdir=tasks/archive','tasks/archive/test_old.py'],{}),
 ('deliberate_noconftest',F,['--noconftest','tasks/archive/test_old.py'],{}),
]
rows=[]
for name,cwd,args,extra in variants:
 if marker.exists():marker.unlink()
 env={'PATH':'/usr/bin:/bin','PYTHONPATH':D,'PYTEST_DISABLE_PLUGIN_AUTOLOAD':'1',**extra}
 cmd=[sys.executable,'-B','-m','pytest','-p','no:cacheprovider',*args]
 p=subprocess.run(cmd,cwd=cwd,env=env,text=True,capture_output=True,timeout=20)
 rows.append(dict(name=name,cwd=str(cwd),command=cmd,environment=extra,exit=p.returncode,imported=marker.exists(),stdout=p.stdout,stderr=p.stderr))
(A/'DISCOVERY-PROBES.json').write_text(json.dumps({'fixture':str(F),'guard_sha256':hashlib.sha256((F/'conftest.py').read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n')
print([(r['name'],r['exit'],r['imported']) for r in rows])
