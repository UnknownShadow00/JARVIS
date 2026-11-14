"""Run unchanged reviewed test assertions from the committed worktree.
Only replay output/root routing and one legacy read-only fixture path are relocated.
No implementation/test file in the checkout is rewritten.
"""
import hashlib,json,sys
from pathlib import Path
REPORT=Path(__file__).resolve().parents[1]
CANON=REPORT.parents[1]
meta=json.loads((REPORT/'evidence/BASELINE-COMMIT.json').read_bytes())
WT=Path(meta['worktree']);AUDIT=WT/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r2'
source=AUDIT/'tests/replay.py'
expected=json.loads((AUDIT/'MANIFEST.json').read_bytes())['files']['tests/replay.py']['sha256']
raw=source.read_bytes()
if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('reviewed harness changed')
code=raw.decode()
old='ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];TASKS=ROOT.parent'
new='ROOT=Path('+repr(str(REPORT))+');REPO=Path('+repr(str(WT))+');TASKS=REPO/"tasks"'
if code.count(old)!=1:raise ValueError('harness relocation anchor')
code=code.replace(old,new)
old="load('independent',ROOT/'tests/test_independent.py')"
new="load('independent',TASKS/'jarvis-v2-vm164-stage2-operator-safety-audit-r2/tests/test_independent.py')"
if code.count(old)!=1:raise ValueError('probe relocation anchor')
code=code.replace(old,new)
# The preserved regression has one absolute canonical fixture reference. Redirect
# that read to its independently hash-matched, tracked checkout counterpart.
legacy=CANON/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r1/FIRST-SUPERVISED-ACTION.json'
replacement=WT/legacy.relative_to(CANON)
original_open=Path.open;redirects=[]
def relocated_open(self,*a,**kw):
 if self==legacy:
  mode=a[0] if a else kw.get('mode','r')
  if any(c in mode for c in 'wax+'):raise ValueError('fixture write forbidden')
  redirects.append({'from':str(self),'to':str(replacement)})
  return original_open(replacement,*a,**kw)
 return original_open(self,*a,**kw)
Path.open=relocated_open
# Any other dependency read from canonical would invalidate checkout isolation.
def no_canonical_reads(event,args):
 if event=='open' and not isinstance(args[0],int):
  path=Path(args[0]).absolute()
  if path.is_relative_to(CANON) and not path.is_relative_to(REPORT):
   raise AssertionError('unexpected canonical dependency: '+str(path))
sys.addaudithook(no_canonical_reads)
ns={'__name__':'reviewed_replay','__file__':str(source)}
exec(compile(code,str(source),'exec'),ns)
status=ns['main']()
origins={name:str(Path(m.__file__).resolve()) for name,m in sys.modules.items() if getattr(m,'__file__',None) and str(getattr(m,'__file__','')).startswith(str(WT))}
(REPORT/'evidence'/('CHECKOUT-ORIGINS-'+sys.argv[1]+'.json')).write_text(json.dumps({'worktree':str(WT),'commit':meta['commit'],'harness_sha256':expected,'relocations':'Only replay ROOT/TASKS and independent probe file location; no test assertions changed','legacy_fixture_redirects':redirects,'module_origins':origins,'runner_exit_code':status},indent=2)+'\n')
raise SystemExit(status)
