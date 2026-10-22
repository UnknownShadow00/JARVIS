"""Finalize actual results only; run after full regression and final readback."""
from pathlib import Path
import json,re,hashlib,tarfile
P=Path(__file__).resolve().parent.parent;E=P/'evidence'
if (P/'SHA256SUMS').exists():raise RuntimeError('SEALED')
I=json.loads((E/'candidate-identity.json').read_text());F=json.loads((E/'runs/full-r2/full-r2-result.json').read_text());C=json.loads((E/'production-final.json').read_text());A=json.loads((E/'production-entry.json').read_text())
log=(E/'runs/full-r2/full-r2.txt').read_text();match=re.search(r'(\d+) passed, (\d+) deselected(?:, (\d+) warnings)?',log);assert F['exit']==0 and match
passed,deselected=int(match[1]),int(match[2]);assert (passed,deselected)==(7741,11)
changed=[k for k in A if k!='utc' and A[k]!=C.get(k)];assert not changed,changed
(E/'production-comparison.json').write_text(json.dumps({'entry_utc':A['utc'],'final_utc':C['utc'],'comparable_fields':len(A)-1,'changed_fields':changed},indent=2)+'\n')
release=Path(I['release']);expected={str(f.relative_to(release)):hashlib.sha256(f.read_bytes()).hexdigest() for f in release.rglob('*') if f.is_file()}
associations=[]
for label in ('focused','full-final','full-r2'):
 run_release=release if label=='full-r2' else release.parent/'release-r1'
 run_expected={str(f.relative_to(run_release)):hashlib.sha256(f.read_bytes()).hexdigest() for f in run_release.rglob('*') if f.is_file()}
 with tarfile.open(release.parent/(label+'.tar')) as t:actual={m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t if m.isfile()}
 assert actual==run_expected
 stage=json.loads((E/'runs'/label/'source-verification.json').read_text());assert not stage['mismatches']
 associations.append({'run':label,'files':len(actual),'source_manifest':hashlib.sha256((run_release/'SOURCE-SHA256SUMS').read_bytes()).hexdigest(),'final_candidate':label=='full-r2','mismatches':[]})
(E/'final-test-source-association.json').write_text(json.dumps(associations,indent=2)+'\n')
text=(P/'TEST-RESULTS.md').read_text().replace('# Test results — full run still pending','# Actual test results').replace('RUNNING |historical baseline7741/11 deselected/0 failed; final result not yet claimed',f'{passed} passed /{deselected} deselected /0 failed /2 warnings |exact revised616-file candidate; no new application cases')
text=text.replace('81 passed,0 failed |30 existing +51 new','84 passed,0 failed |30 existing +54 new').replace('New standalone prequalification cases:51','New standalone prequalification cases:54').replace('final81 pass','final r2 84 pass').replace('Final81','Final84')
text+=f'\nPreserved r1 also completed7741/11/0 before the mount-override correction. The final r2 run below is independently source-verified. Focused200 ran on r1; runtime code is identical.\nFull duration: {F["seconds"]:.3f}s. Candidate: `{F["candidate"]}`. All616 staged files match the final bundle. The focused200 cases overlap the full7741; the84 standalone runner cases are separate. No final failure or silently skipped failure. The11 marker deselections preserve the historical applicable suite. No Golden/model-capable evaluation ran.\n'
(P/'TEST-RESULTS.md').write_text(text)
(P/'PRODUCTION-NONMUTATION.md').write_text(f'''# Fresh read-only production verification

Entry {A['utc']}; final {C['utc']}. All{len(A)-1} comparable fields match. Existing trusted SSH used BatchMode/StrictHostKeyChecking; no host-key enrollment, environment dump, credentials or application HTTP/WS probe. The readback script forbids application writes and network operations and uses SQLite mode=ro/query_only. Only minimized public status/source hashes were retained.

HEAD `{C['source_head']}`; source/config/worktree unchanged; installed source baseline has no mismatches. V2 inactive/dead, disabled, PID0, Restart=no. Epoch606a991a06b74fd79ed72b308417cc3f remains CLOSED_COMPLETE/input_complete1; attempts/submissions/receipt joins0. Original OPERATOR_STOP unchanged. D06current=None,last=None,version1; D04namespace absent; Hermes flags false. No production V3 unit/known installation root or successor observed. Admissions remain closed through inactive runtime and terminal epoch.

Only private isolated ext4 test stages were created on Core; they were outside the canonical repository/state and protected by the existing offline kernel harness. No production source/config/controller/D04/D06/D09/unit/user/network change occurred. No real provider request was made by this task; evidence is its guarded execution/action record, not a claim of global AI-server traffic monitoring. AI/Proxmox were not contacted. No retirement/succession/deployment/pilot/measurement occurred.

Evidence: production-entry.json, production-final.json, production-comparison.json, production-versus-gate6j.json, exact readback tool and per-run kernel restriction reports. No new historical reboot investigation was undertaken.
''')
verdict='JARVIS P7 GATE 6K — PARTIAL, ENVIRONMENT OR DEPENDENCY BLOCKED'
(P/'FINAL-REPORT.md').write_text(f'''# {verdict}

Authorized isolated preparation and corrections are finished for the supplied artifacts. The exact offline interpreter/distribution/OS artifacts are missing, and no disposable VM has been authorized. Full real-VM preflight and genuine multi-UID qualification therefore remain NOT RUN/BLOCKED. Passing same-UID tests does not satisfy Phase B. No production mutation or privileged provisioning occurred.

## Identities

Verified Gate6J candidate `/home/nexus/.local/share/jarvis-gate6j-redteam/release-r2/repo`; source manifest9e824f0c3da92c0edb872ff5f3cbcbd9c32a98f228b49403a92d154584d746fe (612 entries); evidence1714a8e6d1c31dcb54a8f9f921ec057d24c8e06eb2733fc7466cd41f7f1148b0 (173 entries); archivec8347d9e2c193fb96976cec7e36d2db8c92cb4851616ea84c58f497ad1161c00 (613 members).

Revised isolated candidate `{I['candidate']}`. Source manifest `{I['source_manifest']}` (615 entries). Archive `{I['archive']}`, SHA256 `{I['archive_sha256']}` (616 members). Exact source diff and changed files are retained. Runtime/application tree is unchanged; changes are confined to the disposable package. Older candidates/seals are preserved.

## Findings and tests

The historical archive's actual members are structurally acceptable under the new policy; historical raw-tar instructions were insufficiently strict. New extraction validates all bytes and member types/paths/conflicts/digests before destination creation, uses no-follow descriptor operations/exclusive creation, assigns fresh safe modes and preserves interrupted trees. Actual revised extraction passed as UID1000. A demonstrated restrictive-umask bug in the first extractor implementation was fixed and regression-tested.

Runner corrections require exact VM/source/artifact approval, bounded strict regular-file marker reads, private mount propagation and no volatile/protected-path mount overrides,20GiB free, x86-64 and fresh state; preserve structured BLOCKED/FAIL evidence; add future invalid/expired signatures from a valid peer and socket mutation denial attempts. The full diff and failing reproductions remain available. No new runtime architecture or experiment changes.

Final r2 standalone checks:84 passed (30 existing+54 new),0 failed. Focused authority/runtime/security on preserved r1:200 passed,0 failed; these runtime files are unchanged in r2. Full applicable isolated regression:**{passed} passed /{deselected} deselected /zero failed**,2 existing warnings,{F['seconds']:.3f}s. Focused cases overlap full total. Real accept sockets and process crash/rollback cases are included; they execute under one UID. Syntax:358 Python modules and4 human shell blocks. A fresh unprivileged kernel probe confirms no_new_privs, non-AF_UNIX socket denial and unchanged UID. These are not cross-UID qualification. Golden12/20 unchanged/not rerun.

Current test-runtime version comparison matches all127 pins, Python3.14.4/SQLite3.46.1/cryptography46.0.5. Independently reviewed offline bytes/build provenance remain missing for127 distributions plus interpreter/SQLite/libseccomp/OS image. The exact missing inventory is supplied. Several pins are system distributions; no blanket pip installation or substitute versions are authorized. New artifact verifier tests demonstrate that matching versions alone cannot bypass required file hashes. Future installed-image/library verification remains pending.

## Actual security scope and remaining gaps

No VM identity or Phase B approval exists. Actual four kernel UID measurements, cross-UID sockets, protected transaction execution and real multi-UID crash/rollback tests: **NOT RUN**. Future prepared cases, same-UID supplements and unconfirmed requirements are separately mapped in evidence/qualification-matrix.json. The runner's journal reopen is not an actual helper-process restart; positive four-attempt/receipt settlement and all malformed-wire/delegation variants need the corresponding actual-UID evidence before full qualification. The package is preparatory, not an already executed OS proof.

Existing isolated protections retain singleton succession, signed commands/nonces, nonrefundable four-attempt high-water, protected SEND/DISPATCH, truthful D04/D09/checkpoints and D06unknown. Rollback against retained protected authority refuses. Whole-authority-owner rollback remains possible by design; same-host root/hypervisor/host rollback is outside the guarantee. No unapproved external witness was added. Independent terminal witness and production source/interpreter/egress/signer controls remain prerequisites.

Fresh production final readback {C['utc']}: {len(A)-1} fields unchanged; HEADbd53dbc799fb9284a21fae8cce3f5d9539e31141; V2inactive/dead/disabled/PID0; epochCLOSED_COMPLETE/zero use; D06clean; no D04namespace; Hermesfalse; no production V3 successor/installation observed. No task real provider requests, operational execution or measurement.

X1–X11 remain operator approval pending, without new experimental deltas. Original four inputs and REST/REST/WS/WS order, legacy-visible/Granite-observational L1 and proposed Qwen8192 remain isolated only. AI/legacy immutable identities, endpoints, host/GPU/runtime/keep-alive/external actors remain unattested.

## Exact next human action

Review this sealed packet and provide the independently reviewed offline artifact set/build provenance. Then issue exact Phase B approval naming new VMID+UUID, hypervisor node, actual guest machine-id, isolated disk, approved operator console/session, synthetic no-powercut scope, preservation policy and this revised archive/source/artifact-record identity. Use HUMAN-EXECUTION-AND-EVIDENCE-HANDOFF.md and the deliberately incomplete approval template. No privileged action is authorized before those records exist. A changed release needs renewed approval.

Evidence SHA256SUMS is verified at closure; its seal is stored separately in the sibling .seal and final response to avoid circular hashing. It is an integrity seal, not human authorization. No private keys/credentials/raw environments are included. Completion is logged before sealing; no commit/push.

GATE 5: COMPLETE HISTORICALLY FOR V2

PRODUCTION V2: VERIFIED INACTIVE/DEAD, DISABLED, PID0; UNCHANGED

V2 EPOCH: CLOSED_COMPLETE — HISTORICAL ZERO-USE TERMINAL STATE, REVERIFIED

V3 CANDIDATE: ISOLATED ONLY

PROTECTED AUTHORITY: ISOLATED TESTS PASS; DISPOSABLE QUALIFICATION PENDING

GENUINE MULTI-UID QUALIFICATION: NOT RUN

X1–X11: OPERATOR APPROVAL PENDING

AI/LEGACY ATTESTATIONS: PENDING

V2 RETIREMENT: NOT AUTHORIZED

V3 SUCCESSOR: NOT CREATED

V3 DEPLOYMENT: NOT AUTHORIZED

REAL PILOT ATTEMPTS: ZERO, REVERIFIED

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE
''')
print(json.dumps({'verdict':verdict,'full_passed':passed,'deselected':deselected,'production_changed_fields':changed,'source_associations':associations}))
