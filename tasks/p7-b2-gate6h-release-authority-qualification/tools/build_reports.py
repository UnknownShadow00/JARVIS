"""Finalize factual reports from measured evidence, not predicted results."""
from pathlib import Path
from datetime import datetime,timezone
import json,re
P=Path(__file__).resolve().parent.parent
if (P/'SHA256SUMS').exists():raise RuntimeError('SEALED')
E=P/'evidence'
a=json.loads((E/'terminal-archive-final.json').read_text())
prod=json.loads((E/'production-final.json').read_text())
compare=json.loads((E/'production-nonmutation.json').read_text())
identity=json.loads((E/'candidate-identity.json').read_text())
def put(name,text):(P/name).write_text(text.strip()+'\n')

draft={
 'record_state':'DRAFT_UNSIGNED_NOT_EXECUTABLE','authorization_granted':False,
 'predecessor_epoch':'606a991a06b74fd79ed72b308417cc3f',
 'production_head':prod['source_head'],'config_sha256':prod['config_sha256'],
 'archive':a['bundle'],'archive_manifest_sha256':a['manifest_sha256'],
 'controller_logical_sha256':a['live_logical_sha256'],
 'source_implementation_sha256':a['source_implementation_sha256'],
 'verified_state':'CLOSED_COMPLETE','accepted':0,'submissions':0,'D04_receipts':0,
 'maintenance':'OPERATOR_REPORTED_MAINTENANCE',
 'operator_statement':'I performed the JARVIS Core reboot myself.',
 'independent_proxmox_audit_attribution':False,
 'original_event':'OPERATOR_STOP','stop_attribution':'UNATTRIBUTED_V2_SHUTDOWN_HOOK',
 'original_event_or_epoch_rewritten':False,'reopen_authority':'NONE',
 'recommendation':'Permanently retain historical zero-use epoch; separately approve at most one protected linked successor under explicit unattributed-stop exception.',
 'future_retirement_payload_value':'EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT',
 'future_successor_bindings':'UNRESOLVED_REQUIRES_NEW_APPROVAL_AND_FRESH_PROTECTED_READ',
 'production_signature':None,'production_succession_command_emitted':False}
(E/'v2-disposition-draft.json').write_text(json.dumps(draft,indent=2)+'\n')
put('V2-DISPOSITION-RECOMMENDATION.md',f"""
# V2 disposition — UNSIGNED, retirement NOT AUTHORIZED

Retain the historical zero-use V2 epoch permanently and, if separately authorized, qualify it for exactly one signed V3 successor under the reviewed unattributed-shutdown exception. Do not reopen V2. No retirement decision, signature or production succession command issued.

Maintenance context is recorded additively as **OPERATOR_REPORTED_MAINTENANCE**: operator states “I performed the JARVIS Core reboot myself.” Original Proxmox task/audit account was not independently established. INDEPENDENT_PROXMOX_ATTRIBUTION_VERIFIED is not asserted. No further historical reboot investigation requested. The actual OPERATOR_STOP event and terminal epoch remain unchanged. Maintenance is not signed retirement authority.

## Exact future review record

Machine-readable non-executable draft: evidence/v2-disposition-draft.json. It intentionally omits future nonce/signature/live successor bindings.

| Field | Actual verified or proposed value |
|---|---|
| Predecessor |606a991a06b74fd79ed72b308417cc3f|
| HEAD |{prod['source_head']}|
| Config SHA256 |{prod['config_sha256']}|
| Real preserved archive |{a['bundle']}|
| Archive manifest SHA256 |{a['manifest_sha256']}|
| Controller logical SHA256 |{a['live_logical_sha256']}|
| Archive validation |5 component hashes valid; exact live/archive logical equality at entry and final|
| Verified state |CLOSED_COMPLETE/input_complete1, attempts/submissions/receipt joins/refusals0; D06 current/lastNone; D04 absent|
| Original event |OPERATOR_STOP, stop_attribution=UNATTRIBUTED_V2_SHUTDOWN_HOOK|
| Maintenance |Operator-reported only; not independent audit-account proof|
| Reopen authority |NONE|
| Preservation |Real terminal controller, original baseline/startup/final archive, original implementation hashes retained permanently|
| Successor scope |At most one linked protected V3 successor; cap4/no reset or refund|
| Reviewed exception |Explicit acceptance that generic shutdown hook cannot prove operator retirement; future retirement intent solely from a new verified human signature|
| Future payload intent |retirement=EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT, preserving stop-attribution limitation|
| Required authority |Qualified separate OS root/writer, human signer/presence, durable one-use nonce, immutable source/config/process bindings|
| Future release/config/epoch/PID/invocation/checkpoint/nonce/expiry |UNRESOLVED; fill only after new approval and fresh protected readback|
| Signature/command |NONE|

Full original implementation hash map is in terminal-archive-final.json and draft JSON. H-1 freshly compares live/archive/controller/source/config/service/D06 before/after signature, H-2 binds all proof fields, H-3 atomically consumes nonce/reserves one successor and rejects ordinary runtime succession. They support the narrow reviewed exception logically in isolation. Same-UID coordinated rollback remains possible in the current application graph; protected client/readers/OS/signer integration is still required.

This exception explicitly departs from Gate6A/B planned-human-stop prerequisites; it does not rewrite history or claim old OPERATOR_STOP proved retirement. No new V2 stop signal/restart/terminal event is needed or authorized.

Refuse on any nonzero use; wrong epoch/status/input completeness; archive absent/corrupt/mismatch; source/config/controller/live drift; unacknowledged attribution; active/enabled V2/unexpected PID; D06 active/unknown/last state; D04 uncertainty; unexpected receipt/submission/refusal; duplicate root/successor; missing/inconsistent/rolled-back authority; stale identity/checkpoint/signature/expiry; peer/presence mismatch; replayed nonce; incomplete transaction; unapproved provider/model/resource contract; attempted restore/reopen. Reverify everything freshly at actual future signing/commit; this packet is not a standing authorization.
""")

runs=[]
for d in sorted((E/'runs').iterdir()):
 f=d/(d.name+'-result.json')
 if not f.is_file():continue
 v=json.loads(f.read_text());log=(d/(d.name+'.txt')).read_text()
 end=next((line for line in reversed(log.splitlines()) if re.search(r'(passed|failed|no tests ran)',line)),None)
 runs.append({'label':d.name,'exit':v['exit'],'seconds':v['seconds'],'summary':end})
(E/'test-summary.json').write_text(json.dumps(runs,indent=2)+'\n')
put('TEST-RESULTS.md',"""
# Actual tests and evidence

Final source: evidence/candidate-identity.json; manifests and three-file patch retained. Final run archives match all601 current source/harness files, zero mismatches. No source assertion weakened. Gate6G historical baseline preserved:7541 passed/11 deselected/zero failed.

| Run | Actual result | Filesystem/source |
|---|---|---|
| g6h-focused-r5 |458 passed, zero failed|Final source;375 baseline focused+83 new|
| g6h-full-r4 |7624 passed,11 deselected,zero failed,two existing warnings|Final source; tmpfs isolated stage|
| g6h-ext4-final |83 passed,zero failed|Final source, actual ext4 per findmnt|
| g6h-new-final |83 passed,zero failed|Final source, tmpfs|
| g6h-full-r3 |7623 passed,11 deselected,zero failed,two existing warnings|Earlier82-test revision, ext4; explicitly not final source|
| g6h-focused-r4 |457 passed|Earlier82-test revision|
| g6h-full-r2 /focused-r3 |7602 full/436 focused passed|Earlier61-test revision|

All runs, including unsuccessful ones, appear in evidence/test-summary.json and runs/. Initial new-1:18 failed/42 passed, checkpoint fixture recursively read same connection; fixed by separate fixture snapshot. New-2:1 failed/59 passed, fixture attempted to derive digest from absent checkpoint; corrected to exercise actual refusal. Focused-final launch: nonexistent test filename, no tests ran; corrected filename, not a skip. Focused-r2/full-final: original socket import-boundary assertion rejected new module; moved socket handler into existing local_control.py, kept assertion. Final counts above pass. No failing test silently discarded.

After final83-test addition (writable-parent guard regression), full applicable suite reran. New SEND/SETTLE cases test provider-ledger rollback within accepted ordinal, conservative unknowns, conditional roles, stale terminal/resource identity and actual child exits around commits. Other adversarial cases: Ed25519 wrong key/signature, stale nine-field identities, expiry drift, predecessor drift, nonce/permit replay, dual-connection succession/permit races, global cap/order/session, missing/corrupt/schema/chain authority, symlink/hardlink/owner/mode/ancestor drift, old/all app files rollback, restart/incomplete/older-backup refusal, real peercred/malformed/trickle socket. Owner whole-authority rollback is a required successful negative control.

Same-UID mount-confinement denies write/chmod/unlink/symlink/hardlink; no genuine distinct-UID DAC tests. Public-key crypto is real, private fixture keys ephemeral. Readers/model/resource evidence synthetic. Real process os._exit tests are not power-cut/host-loss qualification. No real provider calls.

Static compile140 app/candidate Python files passed, pip check clean, no dependencies installed. Core app venv lacks cryptography: test-only /usr/lib/python3/dist-packages exposes existing system46.0.5 to tests. This is an explicit production packaging blocker; pip check is not a vulnerability audit or dependency lock.

Final full sandbox uses Landlock ABI8 and seccomp, home/production state and credentials denied, no INET/PACKET sockets/connect/signals/ptrace/process-vm/mount/reboot/bpf/io_uring. Trusted supervisor signaled only verified disposable direct children for old crash tests. Full run encountered15 pre-existing network/DNS discovery attempts blocked before send; no provider traffic. Audit counters show zero credential/production/external-write/nonfixture-execution access attempts. Focused/ext4 had zero network attempts. Counters and minimized logs retained.

stat -f uses ext2/ext3 magic wording; findmnt proves actual ext4 for ext4 runs, tmpfs for final full. Golden historical12/20 with eight known failures remains unchanged, not rerun/fixed. No coverage/live-performance/production-root/model-behavior certification claimed.
""")

put('CONTINUOUS-IMPROVEMENT-REGISTER.md',"""
# Continuous improvement register

Only three candidate files differ from Gate6G: new protected_authority.py, appended AuthoritySocket in existing local_control.py, new v3_protected_authority_test.py. Application modules and experimental legacy/Granite profiles unchanged. Source changes/manifests/patch retained. No production commit/push.

| ID | Delivered isolated improvement/fix | Tests/limits |
|---|---|---|
| H01 | Public-key Ed25519 verification, no signing API/private key in engine | Real signature/wrong-key/schema/replay cases; human presence not proved |
| H02 | One append transaction for nonce/root/reservation; cap/order/session/checkpoint and fresh proof/identity | Concurrent real connections, actual pre/post-commit exits, stale fields/expiry; companion only |
| H03 | First prototype protected only attempt count; would miss rollback of ledger within accepted attempt. Added protected SEND/SETTLE and independently associated terminal requirement | Pending unknown survives restart, blocks checkpoint/send/permit; wrong/stale terminal/resources refuse; crash cases. Real trusted reader absent |
| H04 | Checked root file owner but attacker-writable ancestor could replace directory. Added parent-owner/writable/sticky-root policy | Writable-parent regression plus real lstat/symlink/hardlink/inode/mode tests; actual distinct UID pending |
| H05 | Bounded operator socket and reply deadline; preserved existing single socket-import boundary by placing handler in local_control | Real SO_PEERCRED, malformed/oversize/trickle/wrong-allowlist cases; actual second UID/listener pending |
| H06 | Corrected legacy attestation variable to source JARVIS_OLLAMA_BASE_URL; stopped importing whole settings loader for narrow attestation | Source inspection; documentation correction, no runtime environment read |
| H07 | Corrected production D04 collector path to p7-shadow-evidence-v1; corrected historical source inventory location to Gate4 archive; original sealed docs located under docs/ | Read-only collector retries retained; final D04 absent/installed baseline match. No production defect/drift implied |

Qualification-only fixture defects and launch error are documented in TEST-RESULTS, not represented as product fixes. No baseline security assertion loosened, no experimental approval activated. In particular no32768→8192 runtime/default change, no memory/keep_alive/Granite/source prompt change.

Remaining proposals: protected service client/export/runtime wiring; trusted fixed-path source/process and independent terminal/checkpoint evidence; actual multi-UID/helper/signer; immutable dependencies/config/source signature policy; credential loader; external witness/host-loss recovery; real model/endpoint/topology/actor attestations; approved bootstrap/attach and X decisions. No broad architecture rewrite or historical tracing/reboot investigation performed.
""")

put('EVIDENCE-MANIFEST.md',f"""
# Evidence manifest and seal procedure

Version: Gate6H release-r1. Candidate source {identity['source_manifest_sha256']} ({identity['source_members']} members), inventory {identity['inventory_sha256']} ({identity['inventory_members']} members), tar {identity['archive_sha256']}. Candidate at {identity['candidate_path']}; archive at its release-r1 parent as gate6h-release-r1.tar. These are same-UID integrity archives, not immutable protected authorities or Git commits. Review patch embeds changed module/test source. Gate6G archive untouched.

SHA256SUMS covers every regular file in this packet except itself. Its own SHA256 is stored separately in ../p7-b2-gate6h-release-authority-qualification.seal and final response, avoiding self-reference. Verify from packet directory: sha256sum -c SHA256SUMS, then sha256sum SHA256SUMS. Check source/full manifests against their documented candidate roots. No future write to a sealed packet; use new version.

Evidence groups: Gate6G local/Core entry and exit preservation; original Gate6F102-member seal and doc equality; exact original X1–X11 rows plus full source-document paths/hashes; final candidate34-source/601-inventory manifests and patch; run source verification, all successful/failed logs, sandbox counters, ext4/tmpfs evidence, compile/pip-check; real read-only production entry/final and terminal archive comparison; non-executable unsigned V2 draft; namespace limits/mount-denial proof; private infrastructure human-only procedures; all18 required outputs and task loop-log entry copy.

Collection corrections retained: initial D04 collector checked wrong absent path (collector-v1), then actual canonical namespace independently read; extra final historical inventory lookup initially used wrong Gate5 path then corrected to Gate4; Gate6F original docs top-level probe corrected to docs/ with exact equality. These are collector path errors, not altered historical evidence or production discrepancies.

Production inspector audit hook denies writes, credentials and network, SQLite mode=ro/query_only, no app imports. task logs contain fixed metadata/counters/digests, not raw environment/credentials/private keys/conversations. Existing .env.example in preserved source is template, no real credential copied. No signed production command included. The complete candidate is separately stored outside auto-synced task docs; minimized patch/test evidence is reviewable here.

Seal is integrity only, not operator authorization or trusted independent witness. Final verification record is stored outside the packet in .local/share/jarvis-gate6h-authority, and the sibling seal remains separate.
""")
print('Wrote V2 draft, measured tests, improvement register and manifest.')
