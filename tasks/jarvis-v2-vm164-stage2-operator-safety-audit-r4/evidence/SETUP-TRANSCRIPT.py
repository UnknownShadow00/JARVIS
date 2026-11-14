from pathlib import Path
import json,hashlib,shutil,tempfile,subprocess,stat,os
C=Path('/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS');W=C.parent/'JARVIS-v2-stage2-safety-remediation-r4';P=W/'tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r4'
A=C/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r4';A.mkdir(exist_ok=False)
for n in ('tests','evidence'): (A/n).mkdir()
T=Path(tempfile.mkdtemp(prefix='jarvis-r4-independent-'));(T/'tasks').mkdir()
for d in (W/'tasks').iterdir():
 if d.name in (P.name,'jarvis-v2-vm164-stage2-operator-safety-remediation-r3-verified'):shutil.copytree(d,T/'tasks'/d.name,symlinks=True)
 elif d.is_dir():(T/'tasks'/d.name).symlink_to(d,target_is_directory=True)
B=T/'original-audit';shutil.copytree(C/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r3',B,symlinks=True)
(B/'evidence/WORKSPACE.json').write_text(json.dumps({'disposable_copy':str(T)}))
state={'audit':str(A),'disposable':str(T),'candidate':str(T/'tasks'/P.name),'r3':str(T/'tasks/jarvis-v2-vm164-stage2-operator-safety-remediation-r3-verified'),'original_audit':str(B),'reviewed_worktree':str(W),'reviewed_packet':str(P)}
Path('/tmp/r4audit-state.json').write_text(json.dumps(state));(A/'evidence/WORKSPACE.json').write_text(json.dumps(state,indent=2)+'\n')
def git(*a,cwd=W):
 r=subprocess.run(['git',*a],cwd=cwd,capture_output=True,text=True,timeout=30);assert r.returncode==0;return r.stdout
identity={'commit':git('rev-parse','HEAD').strip(),'tree':git('rev-parse','HEAD^{tree}').strip(),'parent':git('rev-parse','HEAD^').strip(),'status':git('status','--porcelain=v1'),'branch':git('branch','--show-current').strip(),'canonical_status':git('status','--porcelain=v1','--untracked-files=no',cwd=C),'canonical_diff_sha256':hashlib.sha256(git('diff','--binary',cwd=C).encode()).hexdigest(),'canonical_log_sha256':hashlib.sha256((C/'tasks/loop-log.md').read_bytes()).hexdigest()}
assert identity['commit']=='5c5d5c2543ed469025ec6cf06b0545c9bdb5eaa6' and identity['tree']=='b0bfd1ea642a9d51ac580b152f2aa50c60aceb87' and identity['parent']=='d153ccd001d1f673b6110782da288e6d114d8762' and not identity['status']
(A/'evidence/GIT-IDENTITY.json').write_text(json.dumps(identity,indent=2)+'\n')
for file in ('tests/fresh_probes.py','tests/run_fresh.py','MANIFEST.json','SECURITY-FINDINGS.md','FIRST-SUPERVISED-ACTION.json'):
 target=A/('tests/original-'+Path(file).name if file.startswith('tests/') else 'evidence/R3-'+Path(file).name);shutil.copyfile(C/'tasks/jarvis-v2-vm164-stage2-operator-safety-audit-r3'/file,target)
print(json.dumps(state,indent=2))
