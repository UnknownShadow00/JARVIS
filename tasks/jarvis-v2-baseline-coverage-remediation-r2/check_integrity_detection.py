"""Exercise the exact launcher's hash routines on disposable mutated inputs."""
from pathlib import Path
import ast,hashlib,json,tempfile,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
source=OUT/'accept_snapshot.py';module=ast.parse(source.read_text())
constants={x.targets[0].id:ast.literal_eval(x.value) for x in module.body if isinstance(x,ast.Assign) and isinstance(x.targets[0],ast.Name) and x.targets[0].id in ('PUBLIC_FILES','SCRIPTS')}
functions=ast.Module(body=[x for x in module.body if isinstance(x,ast.FunctionDef) and x.name in ('files','hashes')],type_ignores=[])
ns=dict(Path=Path,hashlib=hashlib,**constants);exec(compile(functions,str(source),'exec'),ns)
results=[]
with tempfile.TemporaryDirectory(prefix='jarvis-integrity-probe-') as tmp:
 r=Path(tmp)
 for f in ns['files'](ROOT):
  dst=r/f.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dst)
 baseline=ns['hashes'](r);results.append(dict(case='unchanged',passed=baseline==ns['hashes'](r)))
 for name,change in [('changed_test',('tests/test_dictation.py','replace')),('new_module',('tests/test_new_unreviewed.py','new')),('deleted_test',('tests/test_dictation.py','delete')),('changed_harness',('tasks/jarvis-v2-baseline-coverage-remediation-r2/check_adversaries.py','replace'))]:
  path=r/change[0];old=path.read_bytes() if path.exists() else None
  if change[1]=='delete':path.unlink()
  else:path.write_text('synthetic integrity mutation\n')
  results.append(dict(case=name,passed=ns['hashes'](r)!=baseline))
  if old is None:path.unlink()
  else:path.write_bytes(old)
(OUT/'INTEGRITY-PROBES.json').write_text(json.dumps(dict(launcher_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),checks=results),indent=2));assert all(x['passed'] for x in results)
