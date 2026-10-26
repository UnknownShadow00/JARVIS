"""Seal actual evidence only after successful final regressions and identity checks."""
import datetime,hashlib,json,re,shutil
from pathlib import Path
P=Path(__file__).resolve().parent.parent;E=P/'evidence';B=Path('/home/nexus/.local/share/jarvis-gate6k-preflight-fix');W=B/'release-r1';C=B/'candidate-r1'
OLD=Path('/home/nexus/.local/share/jarvis-gate6k-prequalification/release-r2')
OLD_PACKET=P.parent/'p7-b2-gate6k-disposable-multiuid-qualification'
if (P/'SHA256SUMS').exists():raise RuntimeError('ALREADY_SEALED')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
full=json.loads((W/'full-r2-result.json').read_text());text=(W/'full-r2.txt').read_text()
assert full['exit']==0 and '7741 passed, 11 deselected' in text
for f in ('standalone-recorded.txt','standalone-extracted.txt'):
    t=(B/f).read_text();assert 'Ran 133 tests' in t and t.rstrip().endswith('OK')
    shutil.copyfile(B/f,E/f)
assert json.loads((W/'canary-result.json').read_text())['exit']==0
assert 'Ran 5 tests' in (E/'handoff-gate-checks.txt').read_text() and (E/'handoff-gate-checks.txt').read_text().rstrip().endswith('OK')
for label in ('full','full-r2','canary'):
    shutil.copyfile(W/(label+'-result.json'),E/(label+'-result.json'))
    shutil.copyfile(W/(label+'-broker.json'),E/(label+'-broker.json'))
    log=(W/(label+'.txt')).read_text()
    (E/(label+'-summary.txt')).write_text(log[log.index('=================================== FAILURES'): ] if '=================================== FAILURES' in log else '\n'.join(log.splitlines()[-16:])+'\n')
index=[]
for f in [B/'standalone-first.txt',B/'standalone-second.txt',B/'standalone-final.txt',B/'standalone-final-r2.txt',B/'standalone-recorded.txt',B/'standalone-extracted.txt',W/'full.txt',W/'full-r2.txt']:
    index.append({'path':str(f),'sha256':h(f),'bytes':f.stat().st_size})
(E/'retained-log-index.json').write_text(json.dumps(index,indent=2)+'\n')

def verify_rows(root,manifest):
    rows=manifest.read_text().splitlines()
    for row in rows:
        digest,name=row.split('  ',1)
        assert not Path(name).is_absolute() and '..' not in Path(name).parts
        assert h(root/name)==digest,(name,'DIGEST_MISMATCH')
    return len(rows)
assert h(OLD/'SOURCE-SHA256SUMS')=='5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03'
assert h(OLD.parent/'gate6k-release-r2.tar')=='ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d'
assert h(OLD_PACKET/'SHA256SUMS')=='5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6'
identity=json.loads((E/'candidate-identity.json').read_text())
assert h(C/'SOURCE-SHA256SUMS')==identity['source_manifest_sha256']
assert h(Path(identity['archive']))==identity['archive_sha256']
assert h(Path(identity['bootstrap']))==identity['bootstrap_sha256']
validation=dict(old_source_files=verify_rows(OLD,OLD/'SOURCE-SHA256SUMS'),old_evidence_files=verify_rows(OLD_PACKET,OLD_PACKET/'SHA256SUMS'),new_source_files=verify_rows(C,C/'SOURCE-SHA256SUMS'),tested_working_files=verify_rows(W,C/'SOURCE-SHA256SUMS'),archive_extracted_files=verify_rows(B/'extraction-check-r1',C/'SOURCE-SHA256SUMS'),historical_archives_unchanged=True,utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
(E/'final-identity-verification.json').write_text(json.dumps(validation,indent=2)+'\n')
counts={};audit_files=sorted(W.glob('audit-*.json'))
for f in audit_files:
    a=json.loads(f.read_text())
    for k,v in a['counts'].items():counts[k]=counts.get(k,0)+v
(E/'offline-guard-summary.json').write_text(json.dumps({'audit_records':len(audit_files),'aggregate_counts':counts,'scope':'all local full/canary runs; not per-run inference counts','kernel_guard':full['kernel_restrictions'],'real_provider_requests':'NONE: non-AF_UNIX socket creation denied by seccomp'},indent=2)+'\n')
(P/'TEST-RESULTS.md').write_text(f'''# Actual offline results

| Layer | Result | Interpretation |
|---|---|---|
| Standalone runner/preflight |133 passed,0 failed |84 existing +49 new cases; actual files, metadata, malformed mounts and import-only subprocesses; same UID fixtures |
| Extracted replacement archive standalone |133 passed,0 failed |Repeat of the same cases on actual extracted bytes; do not add to total |
| Full applicable isolated suite |7741 passed,11 deselected,0 failed,2 warnings |Final run {full['seconds']:.3f}s; application/dependency pins unchanged |
| Handoff destination/host/interface policy |5 passed |Separate mocked CLI gates; extraction mocked; no root/UID qualification |
| Focused sandbox canary |1 passed |Subset of full suite; actual libc file-read denial and non-AF_UNIX socket denial |
| Archive validation/extraction |619 members verified/extracted |618 source entries plus manifest; unprivileged Nexus fixture |
| Source syntax |361 Python modules parsed |Human shell blocks:3 syntax-valid, not executed |
| Ubuntu compatibility |Ubuntu26.04 LTS,x86-64,kernel7.0.0-38-generic |Actual Nexus OS; VM-specific mounts/credentials remain fixtures/operator reports |
| Required runtime |Python3.14.4,SQLite3.46.1,crypto46.0.5,pytest9.1.1,127 pins matched |No package/system Python changes |
| Genuine distinct-UID / privileged VM qualification |NOT RUN |No VM connection or qualification entrypoint execution |

Final tests ran with LandlockABI8 and seccomp denying non-AF_UNIX sockets, external writes and dangerous syscalls. The signal broker retains direct-child, UID, executable, cwd and pidfd validation. Fake integrations only. Existing real AF_UNIX and crash/rollback cases are included in the full suite; they are not new cross-UID evidence. Golden12/20 is historical and was not run.

New tests cover empty OS containers, real synthetic credential payloads (including empty payload files), cache review/snapshot invalidation, known credential indicators, ownership/modes, symlinks/hardlinks/FIFO, inaccessible/changing metadata, directory-only opening, bounded traversal, approved/unapproved `/boot`, unsafe/shared/protected mounts, credential tmpfs flags, active networking/prohibited hosts, protocol approval fields and `-I` import without qualification execution.

Intermediate failures are preserved: first130-case run had8 fixture failures because Nexus's default umask made synthetic parents group-writable. Setting the fixture umask to022 restored the intended safe baseline while separate unsafe-mode assertions remained. The first guarded133-case run had7 errors because no permitted TMPDIR was configured; the runner now supplies its isolated stage. Initial full run:7740 passed,1 failed,11 deselected; the explicit historical `/tmp/jarvis-gate6c-denied-dummy.txt` canary was absent (ENOENT), not denied (EACCES/EPERM). Exclusive creation of that harmless synthetic file fixed the prerequisite, with no assertion/source change. Its inode/owner identity is retained in the private canary record; no existing unknown file was read or overwritten. Final full rerun passes all7741. No failures were deselected or silently skipped.

Full and intermediate raw logs remain private at paths/digests in evidence/retained-log-index.json. Minimized summaries, final standalone logs and kernel restriction records are sealed here. The2 warnings are existing FastAPI/Starlette deprecations. Static pyright/ruff and coverage tools are absent from the pinned environment: NOT RUN / coverage NOT MEASURED; no dependencies were added to obtain those optional results.
''')
(P/'FINAL-REPORT.md').write_text(f'''# Gate6K VM163 preflight compatibility fix

**ISOLATED FIX COMPLETE — VM UPDATE AND QUALIFICATION AUTHORIZATION PENDING**

The confirmed path-existence blocker is repaired in a separately versioned candidate. Ordinary protected preparation directories no longer imply credential exposure. Active systemd credential payloads still refuse. Opaque cloud-init cache is never read or deserialized and requires a snapshot-bound human fresh-image provenance review when populated. Unknown or exposed credentials, unsafe mounts and prohibited identities remain fail-closed.

Two additional compatibility defects are repaired: isolated `-I` sibling import and explicit private `/boot` partition handling. The offline regression harness now binds to the Nexus interpreter instead of a Core path. All V3 application files, protected-authority implementation and dependency pins remain unchanged.

- Prior Gate6K manifest: `5a68588e2153989e2774a6d58c36a2c25f96fbc343c6522f5377c5618183af03`; archive: `ec9cc8ea6705149b0c5b9b4b267f604b81def97af8df1254477f8ee1873a778d`; evidence seal: `5bfba9ba2c371435af72fa16a7bf688d4a5aee7ff97c0723ce3f6b532ef492e6`. All historical source/evidence entries reverify.
- Replacement: `{identity['archive']}` ({identity['archive_bytes']:,} bytes,619 members).
- Archive SHA256: `{identity['archive_sha256']}`.
- Source manifest SHA256: `{identity['source_manifest_sha256']}`.
- Bootstrap SHA256: `{identity['bootstrap_sha256']}`.
- Tests:133 standalone passes (84 existing +49 new), repeated successfully on extracted archive;5 additional mocked handoff-gate checks pass; full7741 passed /11 deselected /0 failed. The full suite initially exposed a missing synthetic canary prerequisite; it was corrected without changing the assertion and the full suite rerun. See TEST-RESULTS.md.

Nexus is actually Ubuntu26.04 LTS x86-64 with the required runtime versions; the supplied VM163 topology is covered by synthetic fixtures. This does not claim VM163 preflight PASS. Known continuing blockers: mounted offline ISO, absent `/opt/g6k-offline`, absent VM-specific approval marker. Actual systemd credential payloads, cloud provenance, mount propagation, role GIDs/shells, disk free space and protected runtime/artifact review still require human verification.

Exact side-by-side update instructions: OFFLINE-VM-UPDATE-PROCEDURE.md. Install only after explicit approval into `/opt/g6k-preflight-r1`; preserve `/opt/g6j-release`. The invalid approval template deliberately refuses until real identity/review fields are supplied. New release hashes require renewed explicit authorization; prior-digest approval is insufficient. No qualification launch is included in the update commands.

Next action: review this source/patch/evidence and explicitly approve the VM163 offline side-by-side update and read-only diagnostic scope, naming VMID163,UUID `1d279e9b-12cb-4a02-8815-a682cb9457a9`,pve,exact disk and console plus the replacement hashes. Resolve reported blockers under separately approved human preparation. Privileged qualification remains a distinct later authorization.

No VM163,Core,Proxmox or AI host was accessed. No privileged qualification, credentials, real provider operations, production changes, commits or pushes. Production state was not freshly inspected. Evidence seal is recorded separately alongside this packet and in the final handback, avoiding circular hashing.

PRODUCTION JARVIS: UNCHANGED BY THIS TASK; NOT READ BACK

V2 EPOCH: PRESERVED; NOT REVERIFIED

V3 CANDIDATE: ISOLATED ONLY

GENUINE MULTI-UID QUALIFICATION: NOT RUN

VM163 UPDATE / PRIVILEGED QUALIFICATION: SEPARATE AUTHORIZATION REQUIRED

X1–X11: OPERATOR APPROVAL PENDING

AI/LEGACY ATTESTATIONS: PENDING

V2 RETIREMENT / REAL V3 SUCCESSOR / DEPLOYMENT: NOT AUTHORIZED

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE
''')
files=sorted(f for f in P.rglob('*') if f.is_file() and f.name!='SHA256SUMS')
manifest=''.join(h(f)+'  '+str(f.relative_to(P))+'\n' for f in files)
with (P/'SHA256SUMS').open('x') as out:out.write(manifest)
verified=verify_rows(P,P/'SHA256SUMS');seal=h(P/'SHA256SUMS')
seal_path=P.parent/(P.name+'.seal')
with seal_path.open('x') as out:out.write(seal+'  '+P.name+'/SHA256SUMS\n')
with (B/'EVIDENCE-SEAL.txt').open('x') as out:out.write(seal+'  '+str(P/'SHA256SUMS')+'\n')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
log=P.parent/'loop-log.md'
with log.open('a') as out:
    out.write(f'\n## [{now}] Task Completed\n- Task: Gate6K VM163 preflight compatibility fix, isolated Nexus engineering and offline update handoff.\n- Files changed: tasks/{P.name}/*; tasks/{P.name}.seal; tasks/loop-log.md; new private /home/nexus/.local/share/jarvis-gate6k-preflight-fix candidate/archive/bootstrap and synthetic test fixtures.\n- Result: PASS for isolated correction:133 standalone checks (49 new),7741 full passes/11 deselected/zero failures after explicit missing-canary setup;619 archive members and all manifests verified. Evidence seal {seal}. VM163 and production untouched; genuine multi-UID qualification NOT RUN.\n- Next: Explicit VM163 approval for pinned side-by-side offline update/read-only diagnostics; resolve credential/mount/artifact/identity prerequisites; separately authorize privileged qualification.\n')
print(json.dumps({'evidence_seal':seal,'evidence_files':verified,'archive_sha256':identity['archive_sha256'],'source_manifest_sha256':identity['source_manifest_sha256'],'full_passed':7741,'standalone_passed':133},indent=2))
