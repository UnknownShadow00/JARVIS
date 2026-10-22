"""Require actual final test/readback evidence before writing closure documents."""
from pathlib import Path
import json,re,hashlib,datetime
P=Path(__file__).resolve().parent.parent
if (P/'SHA256SUMS').exists():raise RuntimeError('sealed packet')
E=P/'evidence';I=json.loads((E/'candidate-identity.json').read_text())
newlog=(E/'runs/new-r2-final/new-r2-final.txt').read_text();fulllog=(E/'runs/full-r2-final/full-r2-final.txt').read_text()
n=int(re.search(r'(\d+) passed in ',newlog).group(1));m=re.search(r'(\d+) passed, (\d+) deselected, (\d+) warnings',fulllog)
total,deselected,warnings=map(int,m.groups());assert total==7624+n and deselected==11
for label in ('new-r2-final','full-r2-final'):
 result=json.loads((E/'runs'/label/(label+'-result.json')).read_text());assert result['exit']==0
 verify=json.loads((E/'runs'/label/'source-verification.json').read_text());assert verify['files']==606 and verify['mismatches']==[]
entry=json.loads((E/'production-entry.json').read_text());end=json.loads((E/'production-final.json').read_text())
diff={k:{'entry':entry[k],'final':end.get(k)} for k in entry if k!='utc' and entry[k]!=end.get(k)}
assert not diff,diff
assert end['D09']['epochs']==[['606a991a06b74fd79ed72b308417cc3f','CLOSED_COMPLETE',1]]
assert end['D09']['counts']['attempts']==0 and end['D09']['counts']['submissions']==0 and end['D09']['counts']['receipt_joins']==0
assert end['service']['ActiveState']=='inactive' and end['service']['SubState']=='dead' and end['D06']['current'] is None and end['D06']['last'] is None
(E/'production-comparison.json').write_text(json.dumps(dict(entry_utc=entry['utc'],final_utc=end['utc'],compared_fields=len(entry)-1,differences=diff),indent=2)+'\n')
(P/'PRODUCTION-NONMUTATION.md').write_text(f'''# Production nonmutation readback

Trusted read-only Core entry {entry['utc']} and final {end['utc']}. {len(entry)-1} comparable fields, zero differences. Exact minimized JSON and stdout-only readback source are retained. No authenticated HTTP/WS probe or provider request was used.

- HEAD `{end['source_head']}`; config SHA256 `{end['config_sha256']}`; complete app inventory and pre-existing worktree state unchanged. Original installed-source baseline has no mismatches.
- V2 inactive/dead; autostart disabled, MainPID0, Restart=no. Boot identity unchanged.
- Historical epoch606a991a06b74fd79ed72b308417cc3f CLOSED_COMPLETE/input_complete1. Accepted attempts, provider submissions, receipt joins and refusals zero. Original OPERATOR_STOP remains unmodified.
- D06 current=None/last=None. Canonical D04 namespace absent. Hermes flags false. Admissions remain terminal/closed.
- Canonical data directories unchanged. Proposed V3 roots absent, system V3 unit not-found, no installed successor observed on inspected canonical surfaces.

No task action restarted V2, changed production source/config/state, signed a real succession, opened admissions or operated a model. Test writes were confined to explicitly disposable copied-source stages and separate Nexus candidates/documents. Kernel Landlock restricted filesystem access, seccomp denied all non-AF_UNIX socket families, and audit restrictions limited Unix connections to each test stage. No production credentials were opened/copied. The existing trusted SSH path was used with StrictHostKeyChecking=yes.

No real provider request by this task is supported by its action record and offline enforcement, not by a claim of global AI-host telemetry. No AI/Proxmox access or trust enrollment occurred. Disposable /tmp I/O failures were retained; only this task's already-collected fixture directories were cleaned, with source/logs preserved. Earlier sealed archives were not changed. No Git commit/push/history rewriting.
''')
(P/'TEST-RESULTS.md').write_text(f'''# Actual test results

Final Gate6I release-r2: **{total} passed / {deselected} deselected / zero failures**, {warnings} existing warnings, full applicable suite on ext4. **{n} new focused tests passed on ext4**. Both final stages match all606 source inventory files and the final candidate inventory. Baseline7624 passing tests retained plus{n} new cases; none silently skipped or weakened. Historical Golden12/20 with eight known failures unchanged; potentially real Golden evaluation was not run.

| Run | Revision / actual result |
|---|---|
| initial | Early r1:29 new passed/1 failed; test supplied verb twice, corrected authoring error |
| focused-r2 | r1:488 focused passed |
| runtime-r3 | r1:73 passed/1 failed; real listener worker-start/shutdown race fixed |
| runtime-r4 | r1:82 new passed |
| focused-r5 | r1:538 passed/1 failed/1 setup error; content-reader stat comparison incorrectly included read-induced atime, corrected with regression |
| focused-r6 | r1:incomplete, exit120, disposable /tmp disk I/O errors; partial logs/empty artifacts retained, no passing claim |
| focused-ext4-r7 | r1:548 focused passed on ext4 |
| new-ext4-r8 | r1:93 new passed on ext4 |
| full-final | Earlier r1:7717 passed/11 deselected/zero failed/two existing warnings |
| focused-final | Later r1:552 focused passed including explicit protected-command application |
| new-ext4-final | Later r1:94 new passed on ext4 |
| full-release-final | Later r1:incomplete, exit120, /tmp I/O failure; not relabeled a successful run |
| new-r2-final | Final r2:{n} new passed on ext4, including FIFO refusal |
| full-r2-final | Final r2:{total} passed/{deselected} deselected/zero failed/{warnings} existing warnings on ext4 |

The intermediate focused-r5 count is derived from its540 selected cases and retained terminal summary (one failed, one setup error). Final counts come from pytest summaries. Full/r2 selection is the same applicable suite policy as Gate6H. No model endpoints were contacted; httpx.MockTransport supplied all new provider responses. Real AF_UNIX sockets/peer credentials, SQLite/fsync and process os._exit crash boundaries ran. Genuine distinct-UID tests did NOT run; neither user-namespace nor numeric-UID mocks are reported as DAC qualification.

Compilation passed for144 app/candidate/runner modules without bytecode. Existing environment pip check passed; no package installed. Crypto tests use existing system cryptography via explicit fixture path; a production dependency lock/environment still needs approval/qualification. Two existing framework deprecation warnings are preserved.

Collected source verification uses each run's archived source, and final runs additionally match the final inventory. Minimized logs are in evidence/runs/. Raw disposable logs remain in their stages. Intermediate incomplete audit files remain explicitly incomplete; final passing runs have complete enforcement evidence. Test fixtures were not promoted to LIVE or human-attested provenance.
''')
status='''GATE 5: COMPLETE HISTORICALLY FOR V2

PRODUCTION V2: VERIFIED INACTIVE/DEAD, DISABLED, PID0, UNCHANGED

V2 EPOCH: CLOSED_COMPLETE / ZERO USE, REVERIFIED

V3 CANDIDATE: ISOLATED ONLY

PROTECTED AUTHORITY: RUNTIME INTEGRATED; SAME-UID SOCKET/TRANSACTION QUALIFICATION PASSED; PRODUCTION OS/WITNESS QUALIFICATION PENDING

REAL MULTI-UID SEPARATION: NOT QUALIFIED

X1–X11: OPERATOR DECISION PENDING

V2 RETIREMENT: NOT AUTHORIZED

V3 SUCCESSOR: NOT CREATED

V3 DEPLOYMENT: NOT AUTHORIZED

REAL PILOT ATTEMPTS: ZERO, REVERIFIED

MEASUREMENT: NOT STARTED

FORMAL P7 EXIT: NOT COMPLETE'''
(P/'FINAL-REPORT.md').write_text(f'''# JARVIS P7 GATE 6I — PARTIAL, DISPOSABLE OS QUALIFICATION REQUIRED

The protected authority now gates the actual isolated V3 runtime, including existing REST/WS ingress, D09 acceptance, provider pre-send and coordinated checkpoint paths. This is an implemented/tested integration, not a parallel synthetic controller. Production remains unchanged and deployment unavailable. Genuine distinct-UID separation and the real independent provider terminal witness remain unqualified.

## Exact source identities

Gate6H entry `/home/nexus/.local/share/jarvis-gate6h-authority/release-r1/repo`: source manifest c874b50719a599e4e6a18f051b0395fb45e0b7cc3f0a8338aeca8206cddd9da2; inventory57ad124ec88e4e06b40f4d392c3cae27bc5648b010bbfe28d1c92e00754f7fe2 (601 files); evidence seal3deab83694b8398c184c4deb9a03420760928fa89f63a1d7b4acc88390d7ae74 (245 members). Verified before copying and at closure; no earlier archive/seal changed.

Final `{I['candidate_path']}`: source manifest `{I['source_manifest_sha256']}` (39 members); inventory `{I['inventory_sha256']}` (606 files); archive `{I['archive_sha256']}`. Fourteen changed/new files versus Gate6H, zero production app module changes. Earlier6I exports/run-specific archives retained; only release-r2 is final. SOURCE-AND-MANIFEST.md records paths, hashes and exact original contract source documents.

## Interfaces, transactions and actual qualification

Operational disposable interfaces: real AF_UNIX accept-based authority service, typed read/checkpoint/attempt/provider service client, and separate signed operator client. Explicit runtime owner application retrieves the remotely approved command; it takes no claimed operator peer values and is not exposed by Bearer routes. Approval alone leaves admissions closed. Fixed schemas exclude arbitrary paths/SQL/code/shell/imports/callbacks. Kernel SO_PEERCRED, process start/boot pins, socket/ancestor integrity and Ed25519 validation are separate checks. No signer/private key lives in the runtime client or journal.

Standard Ed25519 and atomic SQLite transactions protect one successor nonce, one-use administrative CLAIM, separately consumed permit, global maximum four accepted attempts, exact D09 IDs and durable possible-send substeps. Checkpoint exports are derived compatibility projections, not a second counter. Root ledger is authoritative. Lost acknowledgment cannot refund or duplicate a committed operation. Source/config/process drift, stale/corrupt/missing authority or inconsistent controller state refuse; no auto-initialization, restore, epoch reopen or restart authority exists.

Rollback tests cover controller/accepted state, command replay, substep history, older backups and replacing all service-writable files while retaining protected history. Nonces, claims, accepted ordinals and pending sends survive process crashes/reopen. Pending SEND is uncertainty, not inference proof. Settlement requires independently associated terminal evidence; fake witness works in tests, absent witness holds. Stop/drain retains D06 remote unknown and truthful D04/delivery joins; authority unavailability makes terminal completion incomplete.

AF_UNIX tests exercise partial/trickling/oversized/malformed/duplicate-key/version/unknown-verb requests, descriptor rejection, nonreading/broken peers, concurrency, stale identity, path replacement, peer rejection, replay, shutdown and committed-state reopen. Real sockets ran under the SAME kernel UID. **Genuine multi-UID testing: NOT RUN.** No separately approved VM was found or assumed. The automated future runner requires four real identities, immutable fixtures, root approval marker, no NIC and no_new_privs/AF_UNIX-only enforcement; it is syntax/nonroot-refusal tested only. Exact root-owned0750/group-connect0660 socket provisioning is documented. No current service/signer DAC isolation is claimed.

A genuinely protected on-host root is still required for production service-UID protection. Root/whole-host/hypervisor rollback can still replace every on-host proof. Stronger resistance requires a separately trusted external anchor/recovery design and separate approval; no off-host export was performed. A compromised UID bypassing the application and issuing arbitrary provider traffic also needs reviewed egress/infrastructure controls, not claims that this helper is a provider proxy.

## Experimental contract and infrastructure

Bounded L1 rules-first behavior retained: original four inputs and REST/REST/WS/WS order, bounded Gemma only unresolved classification, source-backed responder selection, legacy-only visible reply, independent invisible Granite, no operations/confirmation/TTS/retries/fallback/automatic permit. New protected graph requires pinned skills.md snapshot and proposed normal context8192, correcting32768. Frozen Granite64000/128/180s/profile/restrictions unchanged. Fixtures now persist OFFLINE_FIXTURE rather than LIVE.

All original X1–X11 remain operator decisions; recommendations are the requested strict classifier, no deep branch, pinned memory, proposed8192/4096 contexts, keep_alive60, zero retries/fallback and20s/180s deadlines, nonstream/no TTS, empty/action/tool refusal, independently attested topology and four-attempt/11-operation/1500-second envelope. X4/X5/X6/X10 also require external attestation. Nothing was installed as production configuration.

Effective router/responder endpoints, immutable Gemma/Qwen/Granite identities, trusted AI host fingerprint, physical GPU/runtime relationship, external lifecycle actors and D06 conflict-domain isolation remain UNVERIFIED. A concise exact human-only checklist is supplied. No AI/Proxmox contact, trust bypass/enrollment, environment dump or model lifecycle/generation operation occurred.

## Genuine fixes, tests and evidence

Implemented runtime/client/transport integration, separated approval from consumption, closed opening replay through durable CLAIM, enforced exact pre-send resource associations, fixed listener worker shutdown race, bounded no-follow SQLite snapshots including FIFO refusal and atime handling, downgraded unverified terminal completion, corrected normal context/pinned memory and fixture origin. Substantive changes have regressions; historical assertions were not loosened. No broad architecture redesign or historical reboot investigation.

Final release-r2: **{total} passed / {deselected} deselected / zero failed**, {warnings} existing warnings, full suite on ext4. **{n} new focused tests passed on ext4**. Last combined r1 focused run552 passed; final full suite includes all prior focused cases plus the new FIFO regression. Final stages match all606 files. Compile144 and dependency consistency pass. Intermediate failures and /tmp I/O-interrupted runs are retained and explicitly distinguished. Historical Golden12/20/eight failures unchanged, not rerun.

Evidence SHA256SUMS covers this packet; verified seal is recorded separately in sibling p7-b2-gate6i-protected-runtime-integration.seal and the final response, avoiding a self-referential manifest. It is an integrity seal, not operator authorization. Completion log is appended before sealing. No credentials/private keys/raw protected environments/real conversations are included.

## Production readback and next action

Final trusted readback {end['utc']}: {len(entry)-1} comparable fields, zero differences from entry. HEAD bd53dbc799fb9284a21fae8cce3f5d9539e31141; source/config/worktree unchanged. V2 inactive/dead, disabled, PID0, Restart=no. Historical epoch606a991a06b74fd79ed72b308417cc3f CLOSED_COMPLETE/input_complete1; attempts/submissions/D04 joins/refusals0. D06 current/lastNone; D04 namespace absent; Hermes false; admissions closed. No V3 installation/successor observed on canonical inspected surfaces. No task provider requests, established by restricted offline execution/action record rather than global AI-host telemetry. No commit/push/history rewrite.

Retain historical zero-use V2 permanently. OPERATOR_REPORTED_MAINTENANCE leaves original OPERATOR_STOP and its unattributed-shutdown limitation intact; no retirement authorization is inferred. Production installation remains blocked pending OS/signer/witness/model/resource approvals and qualification.

Exact next operator action: review this sealed source/evidence and authorize a specific disposable multi-UID VM run with the supplied automated package. Independently review X1–X11 and authorize human-only infrastructure/model attestations. Production identities/bootstrap, signed V2 disposition, one successor, installation, new Gate5, real provider qualification, four permits and Gate7 remain separate future stages. No provisioning, real provider operation or pilot activation is authorized by Gate6I.

{status}
''')
print(json.dumps(dict(new_tests=n,full_passed=total,deselected=deselected,production_compared_fields=len(entry)-1,production_differences=0)))
