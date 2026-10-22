"""Verify final public evidence, append required completion log, seal exclusively."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
P=Path(__file__).resolve().parent.parent;W=P.parent.parent;E=P/'evidence'
required=['FINAL-REPORT.md','GATE6J-ENTRY-VERIFICATION.md','ARCHIVE-EXTRACTION-SECURITY.md','DEPENDENCY-ARTIFACT-VERIFICATION.md','DISPOSABLE-VM-IDENTITY-AND-APPROVAL.md','PREQUALIFICATION-RESULTS.md','MULTI-UID-KERNEL-RESULTS.md','AF-UNIX-CROSS-UID-RESULTS.md','PROTECTED-TRANSACTION-RESULTS.md','ROLLBACK-AND-CRASH-RESULTS.md','AUTHORITY-AND-SIGNER-SEPARATION.md','RUNNER-DEFECTS-AND-FIXES.md','TEST-RESULTS.md','PRODUCTION-NONMUTATION.md','REMAINING-APPROVALS.md','HUMAN-EXECUTION-AND-EVIDENCE-HANDOFF.md']
assert not (P/'SHA256SUMS').exists() and not P.with_suffix('.seal').exists()
assert all((P/n).is_file() for n in required)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def verify(root,manifest,expected=None):
 if expected:assert sha(manifest)==expected
 rows=manifest.read_text().splitlines();names=set()
 for row in rows:
  h,n=row.split('  ',1);assert n not in names and not Path(n).is_absolute() and '..' not in Path(n).parts;names.add(n)
  f=root/n;assert f.is_file() and not f.is_symlink() and sha(f)==h,n
 return len(rows)
J=W/'tasks/p7-b2-gate6j-security-and-os-qualification';JR=Path('/home/nexus/.local/share/jarvis-gate6j-redteam/release-r2')
historical={'gate6j_evidence_members':verify(J,J/'SHA256SUMS','1714a8e6d1c31dcb54a8f9f921ec057d24c8e06eb2733fc7466cd41f7f1148b0'),'gate6j_source_members':verify(JR,JR/'SOURCE-SHA256SUMS','9e824f0c3da92c0edb872ff5f3cbcbd9c32a98f228b49403a92d154584d746fe')}
assert sha(JR.parent/'gate6j-release-r2.tar')=='c8347d9e2c193fb96976cec7e36d2db8c92cb4851616ea84c58f497ad1161c00'
I=json.loads((E/'candidate-identity.json').read_text());R=Path(I['release']);assert verify(R,R/'SOURCE-SHA256SUMS',I['source_manifest'])==615 and sha(Path(I['archive']))==I['archive_sha256']
assert len([f for f in R.rglob('*') if f.is_file()])==616
for record in ('candidate-r1-identity.json','candidate-identity.json'):
 v=json.loads((E/record).read_text());root=Path(v['release']);verify(root,root/'SOURCE-SHA256SUMS',v['source_manifest']);assert sha(Path(v['archive']))==v['archive_sha256']
(E/'historical-and-candidate-reverification.json').write_text(json.dumps(historical|{'gate6j_archive':'MATCH','gate6k_r1':'PRESERVED_MATCH','gate6k_r2':'MATCH'},indent=2)+'\n')
assert not json.loads((E/'production-comparison.json').read_text())['changed_fields']
assert json.loads((E/'runs/full-r2/full-r2-result.json').read_text())['exit']==0
assert 'Ran 84 tests' in (E/'unprivileged-r2-final.txt').read_text() and (E/'unprivileged-r2-final.txt').read_text().rstrip().endswith('OK')
assert not any(f.is_symlink() for f in P.rglob('*'))
# Only reviewed public documents/code/status/test outputs; never fixture/key trees.
assert not any(f.name in ('signing.key','.env','id_rsa','id_ed25519') for f in P.rglob('*'))
now=datetime.now(timezone.utc).isoformat()
entry=f'''\n## [{now}] Task Completed
- Task: Gate 6K authorized isolated prequalification, strict archive extraction, VM/artifact/mount preflight hardening and read-only production verification.
- Files changed: tasks/p7-b2-gate6k-disposable-multiuid-qualification/; new isolated jarvis-gate6k-prequalification/release-r1 and release-r2 packages; tasks/loop-log.md. No production or historical archive changes.
- Result: PARTIAL against overall acceptance:84 standalone checks passed (54 new),200 focused passed, final7741 passed/11 deselected/zero failed; archive/source/evidence verified; fresh production unchanged. Genuine multi-UID NOT RUN; independent offline artifacts and exact VM authorization missing.
- Next: Human review of sealed packet; supply reviewed offline artifacts; authorize exact VMID/UUID/node/machine/disk/console/scope/preservation and revised source/archive/artifact digests before Phase B. No retirement, successor, deployment or pilot authorization.
'''
with (W/'tasks/loop-log.md').open('a') as output:output.write(entry)
(E/'completion-log-entry.md').write_text(entry)
files=[f for f in sorted(P.rglob('*')) if f.is_file()]
manifest=''.join(sha(f)+'  '+str(f.relative_to(P))+'\n' for f in files)
with (P/'SHA256SUMS').open('x') as out:out.write(manifest)
count=verify(P,P/'SHA256SUMS');seal=sha(P/'SHA256SUMS')
with P.with_suffix('.seal').open('x') as out:out.write(seal+'  '+P.name+'/SHA256SUMS\n')
print(json.dumps({'verdict':'JARVIS P7 GATE 6K — PARTIAL, ENVIRONMENT OR DEPENDENCY BLOCKED','entries':count,'evidence_seal':seal,'candidate_source_manifest':I['source_manifest'],'archive_sha256':I['archive_sha256'],'production_final':json.loads((E/'production-final.json').read_text())['utc']}))
