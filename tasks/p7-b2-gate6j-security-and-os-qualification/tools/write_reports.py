from pathlib import Path
import json
T=Path(__file__).resolve().parent.parent
I=json.loads((T/'evidence/candidate-identity.json').read_text())
assert not (T/'SHA256SUMS').exists()
docs={
'GATE6I-SOURCE-VERIFICATION.md':f'''# Gate 6I provenance

Verified before copying: candidate `/home/nexus/.local/share/jarvis-gate6i-runtime/release-r2/repo`; source manifest `c0aac0e6a33e0dbfcd00616651354ed42c70aa3be22774b83b3348d180a3f461`; evidence seal `09f6347a0bdd30e2153727b0a7ba5e6485ddd3d0705268b290ec7e989f5ebb22`. All235 evidence members and all606 source inventory members matched. Archive `1aacb61170c83630c5e162cc015d15e90ba1035350d5535c00e369b8f6f9d8a1` matched. Entry evidence is evidence/entry-provenance.json. Gate6H design and multi-UID reports were read as historical dependencies. Earlier seals are preserved.

Current shared workspace started with modified tasks/loop-log.md and untracked Gate6I packet/seal. These changes were retained. No branch assumption, checkout, reset, merge, commit or push occurred.

Final candidate: `{I['candidate']}`. Full source manifest `{I['source_manifest']}` covers612 source/test/harness/package files. Unlike Gate6I's39-member focused manifest, this is a complete source inventory. The archive additionally contains that manifest (613 total files); inventory digest `{I['inventory_digest']}`. Archive `{I['archive']}` SHA256 `{I['archive_sha256']}`. The SOURCE-SHA256SUMS file excludes itself. No repo/app module changed. Sixteen changed/new files include the manifest; the exact list and unified diff are in evidence/candidate-identity.json and evidence/gate6i-to-gate6j.patch.

Intermediate release-r1 and run archives remain separately retained. Use release-r2 only for future qualification. A later supplemental wire-probe archive adds one explicitly named test harness file outside the candidate; it does not change the release source.
''',
'SECURITY-BOUNDARY-AUDIT.md':'''# Independent source review scope

This is a new adversarial examination of the verified Gate6I implementation. It is not an external certification or a claim of separate human review. The review traced the actual configured protected graph and inspected the future privileged runner.

| Boundary | Source and trace | Finding / qualification |
|---|---|---|
| REST and WS | ingress.Ingress → monitored Runtime.request → ServiceAuthorityClient.before_accept → AuthorityService.CONSUME → Store.accept → BIND | Bearer/continuation checks precede admission. Bearer exposes no signed command route. Four global accepts remain nonrefundable. |
| Operator | OperatorCommandClient → real Unix listener → kernel identity → AuthorityService.SIGNED → Authority.check/Ed25519 → RuntimeJournal.signed | Signature and OS identity separate; signed approval does not itself apply local OPEN. |
| Administrative application | Runtime.apply_protected_command → remote approved command → CLAIM → local control/open/arm | Local direct control also consumes the same protected approval; no service SIGN verb. |
| Provider | Runtime._generate → local possible-send → protected SEND → OwnedProvider/D06 → NativeTransport → new protected DISPATCH → fake native HTTP | Confirmed direct dispatch bypass repaired at the native seam. One-use dispatch is another event for the same accepted substep, not another attempt counter. |
| Settlement | correlated native result → local terminal record → protected SETTLE with installer-side witness | No witness means refusal; cancellation/socket closure cannot create terminal evidence. Real independent witness remains absent. |
| Evidence/checkpoint | D04 EvidenceBridge → D09 receipt join → CheckpointWriter → protected fixed ControllerReader | Captured bounded file bytes replace privileged repeated/path-based reads; schemas and bounded SQLite work checked. |
| Stop/restart | close local admissions → drain/account → protected TERMINATE → reconcile actual terminal status | Found and fixed false local COMPLETE after unbound protected acceptance. Restart cannot rebind/reopen. |
| Runner privilege boundary | root parent ↔ distinct role processes | Fork descriptor inheritance and pickle reception replaced by spawn and bounded fixed-type JSON. |

Secondary constructors and old HighWater/build_isolated_app paths remain explicit OFFLINE_EVALUATION_ONLY baseline fixtures. They are not production startup entrypoints. No module import installs a listener, starts inference or imports operational dispatch. contracts.build_production_runtime always refuses. The protected factory binds its native transport to the same authority client as admission/checkpoints. The new regression directly invokes both OwnedProvider and NativeTransport on that graph and requires refusal without SEND.

Limits: arbitrary code execution inside the service process could instantiate its own HTTP client or alter Python objects. This helper is not an egress proxy and Python object identity is not an OS capability boundary. A future production design must independently constrain provider reachability and writable imports/interpreter/dependencies. No claim is made that these isolated software checks contain arbitrary service-code execution. Root/host rollback, production signer custody/presence and independent completion witness remain outside the qualification obtained here. No demonstrated bypass remains in the tested configured graph; this does not establish absence of all defects.
''',
'AUTHORITY-BYPASS-TESTS.md':'''# Authority bypass experiments

Two failing tests on unchanged Gate6I runtime code reached the fake provider through direct OwnedProvider and NativeTransport invocation after a local possible-send row, without a protected SEND. Evidence: runs/redteam-before (2 failures). Both are repaired by a durable native-seam DISPATCH claim referencing the existing pending SEND, resource, accepted attempt and exact local substep. Reusing the claim, conflicting IDs/digest, stop approval and lost acknowledgment refuse; no new provider call is made.

A passed connection was also accepted from a different actual PID under the connector's SO_PEERCRED. runs/delegated-before preserves the failure. Per-message SCM_CREDENTIALS now checks each writer. Numeric client UID/PID fields remain rejected. Actual cross-UID execution is NOT RUN.

runs/terminal-before demonstrates protected INCOMPLETE while local/runtime claimed COMPLETE after protected consumption but before D09 join. Readback now propagates the conservative protected outcome. None of these tests used a real model or a production controller.

The protected journal now also rejects a classifier SEND on ordinal2 and more than11 total SENDs. This enforces the already proposed four original inputs/conditional-operation budget at the protected boundary; it does not approve X11. The real runtime's rules-first second turn already omitted classification.
''',
'AF-UNIX-ADVERSARIAL-RESULTS.md':'''# Actual accept-based transport

Tests use real pathname bind/listen/accept/connect and kernel credentials. Same kernel UID throughout current execution; separate processes are used for the delegated-writer attack. Neither simulated wrong allowlist UIDs nor these sockets prove cross-UID DAC security.

Existing focused tests cover wrong peer allowlist, stale start/PID identity, expiry/signature/replay, duplicate JSON keys, unknown versions/verbs, forged UID fields, bounded/partial/trickling/oversized input, SCM_RIGHTS rejection/closure, socket replacement, unsafe directory modes, concurrency, shutdown during partial input and nonreaders. Supplemental final-bundle probes exercise malformed UTF-8, symlink substitution and client disconnect after signed command submission. Counts and exact run sources are in TEST-RESULTS.md.

Confirmed delegated-writer flaw: SO_PEERCRED identifies connection-time credentials. SO_PASSCRED/SCM_CREDENTIALS supplies credentials of the actual sender; the listener now requires one matching credential record per received segment and still rejects passed descriptors. This uses documented Linux behavior: [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html). It is not a new cryptographic protocol.

ProcessPin checks UID/PID plus /proc start ticks and boot ID before/after framing. These are freshness checks under a trusted kernel/proc filesystem, not executable-image measurement, hardware attestation or root resistance. PID/start checks cannot detect injected code in a still-running process. Privileged credential forgery/root compromise is outside this guarantee. Fixed operator/service listener paths are root-owned0750 directories and0660 sockets in distinct private groups. Clients may connect but cannot replace directory entries. Existing endpoints are not blindly unlinked at startup.
''',
'TRANSACTION-AND-CRASH-RESULTS.md':'''# Durable transitions and interruptions

Sequence: signed singleton succession → signed OPEN/permit approvals → durable administrative CLAIM → protected CONSUME → local D09 acceptance → BIND exact attempt ID → local possible-send → protected SEND → new one-use DISPATCH → provider → correlated native terminal → protected SETTLE with independent witness → D04 append → D09 receipt association → coordinated CHECKPOINT. TERMINATE never grants succession or reopening.

SQLite BEGIN IMMEDIATE/FULL transactions commit before acknowledgment. Nonces and attempts remain spent after failure. The new DISPATCH event is consumed against the existing pending SEND under the journal lock; it is never refunded. A claim without observed transmission remains uncertain, not proof of inference.

New tests exercise exception before/after DISPATCH commit, real child os._exit before/after commit, simultaneous dispatch claims, stop before dispatch and mismatched attempts/substeps/digests. Exactly one durable disposition remains and no crash manufactures provider work. Existing regressions cover successor/claim/permit acceptance/BIND/SEND/SETTLE crash windows, local possible-send and provider-terminal writes, D04 append-before-join, receipt join, checkpoint publication and bounded stop/drain. Supplemental socket test disconnects without reading OPEN acknowledgment, observes durable approval, rejects replay and proves admissions did not automatically open.

The false COMPLETE repair independently compares helper terminal status after TERMINATE. Inability to verify also downgrades completion. A later clean local database cannot refund an unbound accepted ordinal.

Not tested: VM power loss, hardware cache failure, hypervisor rollback, true multi-UID crash workflow or real remote-completion witness. Provider/model activity was fake throughout.
''',
'ANTIROLLBACK-ATTACK-RESULTS.md':'''# Rollback outcomes

The full applicable suite retains Gate6G/6H/6I rollback cases: controller/accepted rows, older checkpoint/backup, signed root/commitment substitution, source/config/process identity drift, missing/corrupt authority and all service-writable directories replaced together. Protected history retains accepted ordinal/claim/send associations and rejects disagreement; backups never initialize or restore authority.

Protected ControllerReader checks exact schema, signed claims, permit associations, accepted IDs and every protected SEND. CHECKPOINT requires a current authority sequence/seal plus coordinated D04/D09/D06 joins. New snapshot handling captures each file once with bounded no-follow component-by-component opens. It rejects FIFO, hardlink, symlink parent and oversized data; untrusted SQLite evaluation has a finite VM-instruction budget. This addresses denial-of-service and inconsistent repeated reads without claiming a coherent cross-file live snapshot when the service races changes: inconsistent data must refuse.

The negative control test_complete_authority_rollback_still_possible_to_owner is deliberately retained and run. Replacing the authority owner's complete checkpoint can restore old valid-looking history. Its test PASS means the attack succeeds as expected, not that host rollback is defeated.

Security depends on a genuinely protected authoritative state remaining outside service write control. Same-host authority does not independently resist root, physical-host or hypervisor rollback. Additional hashes cannot fix that boundary. Stronger guarantees need a separately trusted anchor and reviewed recovery protocol; none was implemented or contacted.
''',
'D06-PROVIDER-ISOLATION-RESULTS.md':'''# Provider and resource isolation

All execution used fake httpx transports and disposable stores under the existing Landlock/seccomp offline harness. Non-AF_UNIX socket creation is kernel-denied; production state/credentials are excluded from test access. No generation, model lifecycle or operational-tool endpoint was contacted.

Existing and new tests cover CLOSED/no permit/no protected SEND → zero calls; four nonrefundable global attempts; REST/REST/WS/WS order; classifier/responder/Granite separate substeps; same endpoint/GPU conflict domains; cancellation/disconnect/timeouts preserving unknown; no retry/fallback; strict classifier refusal; legacy-only delivery and history; invisible Granite; no tool/confirmation/TTS execution; no startup inference or automatic next permit.

New native DISPATCH consumes one pending SEND before possible HTTP activity. Uncertain acknowledgments and process crashes do not authorize another claim. The authority blocks classifier use on original ordinal2, preserving the proposed11-operation/1500-second envelope with the fixed20/180-second profiles. The user-facing semantics are unchanged; no approval is inferred.

D06 local ownership does not control independent clients/lifecycle actors that ignore it. Effective Gemma/Qwen/Granite digests, endpoints, GPU sharing, server policy/keep-alive and other actors remain unattested. A true external completion witness and independent production egress/actor controls remain release prerequisites. Local lease closure and a fixture response do not independently establish real remote completion.
''',
'CONFIRMED-DEFECTS-AND-FIXES.md':'''# Findings and fixes

| ID | Severity / violated property | Reproduction and repair |
|---|---|---|
| J1 | High: direct dispatch bypassed protected SEND | Two pre-fix failures in redteam-before. Bind native seam to same authority client; atomically consume one DISPATCH for exact pending association. Replay, mismatch, race and crash regressions pass. |
| J2 | High: delegated socket writer retained connector identity | delegated-before actual second-PID write accepted. Add Linux per-message credentials, retaining signature and process-pin checks. |
| J3 | High: misleading terminal completion | terminal-before protected acceptance with no D09 join produced local COMPLETE. Read/reconcile protected status and downgrade on mismatch/unavailability. |
| J4 | High in future privileged runner: inherited operator pipes | Unprivileged fork negative control inherits unrelated descriptors. Spawn fresh role interpreters; positive exclusion test uses a real child process. |
| J5 | High in future privileged runner: lower-privilege pickle input | Negative control selects an executable callable through Connection.recv. Replace with bounded JSON, fixed types, explicit tag allowlist and whole-transfer deadlines; malicious pickle/tag and partial-frame tests refuse. |
| J6 | Medium: privileged snapshot reads unbounded/repeated | Source inspection showed Path.read_bytes before/after digest checks. Capture bounded bytes once, no-follow every component, verify owner/mode/link/inode changes, validate schema before queries, cap SQLite work. FIFO/size/link/capture/budget regressions pass. |
| J7 | Medium: protected envelope allowed an extra second-turn classifier | Protected SEND role policy originally allowed router for every ordinal. Root now enforces ordinal2 omission and total11; dedicated attack refuses. Existing runtime semantics already omitted this call. |
| J8 | Runner correctness: overbroad denial classification and incomplete failure records | Only PermissionError counts as DAC denial. Missing path errors fail. Suite timeout now900 seconds with retained FAIL report/log, replacing180 seconds and lost timeout evidence. Source/VM/environment/dependency preflight and report sealing are explicit. |

Fixes are confined to the new candidate. No production app module changed. evidence/gate6i-to-gate6j.patch and evidence/source preserve exact reviewable changes. Runtime bugs have failing pre-fix artifacts; runner inheritance/pickle use explicit negative controls. Snapshot and operation-budget findings arose from source inspection and have targeted adversarial regression tests; they are not falsely described as captured pre-fix end-to-end exploits.

An intermediate import-path defect introduced while separating runner modules failed one focused test; fixed package-relative import setup, retained failure and reran. An initial manifest positive fixture was legitimately rejected for group-writable NEW Gate6J directories; only those isolated directories were tightened, never production or historical trees. Dependency capture initially selected duplicate system metadata versions; corrected to effective import-precedence versions and verified all127 pins.
''',
'DISPOSABLE-RUNNER-REVIEW.md':'''# Existing package review and scope

Reviewed the actual Gate6I disposable/qualify_all.py and qualify_multi_uid.py before extending them. The future root entrypoint remains qualify_all.py; it runs cross-UID orchestration followed by an unprivileged candidate regression subset. Gate6J paths/accounts intentionally use g6j to prevent reuse of an earlier occupied destination.

Four principals: root AUTHORITY, non-login g6j-operator, g6j-service and g6j-agent, with distinct nonzero UID/private GID values for the three children and no supplementary groups. Root is the authority identity in this fixture, not a claim that a separate nonroot helper deployment has been qualified. Root can inspect any same-host key; the boundary under test excludes service/agent access.

New spawn avoids inherited sibling channels. Parent/role messages use SafePipe bounded JSON and only fixed Bindings/Resource/Limits/StepContract structures, not pickle from untrusted roles. The signing key is generated only inside the operator child and stored0600 beneath its0700 directory. Parent receives only public key and signatures. Root helper has no signing verb, generic command, path/SQL/import or provider-proxy API.

Preflight requires an exact root0600 approval marker, machine ID, external VM identity declaration, no NIC beyond loopback, a private ext4 root, no additional/shared filesystem mounts, no known credential/host paths, exact source manifest and effective dependency pins. These checks supplement an independent human console/mount/network/credential review; no program can prove that arbitrary undisclosed credentials do not exist on a host.

The cross-UID phase tests permitted actual client operations and denials, operator direct-write denial, a DAC-accessible socket with intentionally wrong peer pin, signature/replay, successor race, concurrent permit consumption at actual runtime acceptance, deliberately dropped OPEN acknowledgment, fake-provider uncertainty, whole app/controller/backup rollback, and authority reopen/replay. The following service-UID pytest phase covers detailed crashes/corruption/source/backup cases and emits per-test JUnit. Reports label these latter logical tests as same-UID; they do not inflate cross-UID coverage.

Root-parent report cases record PASS/FAIL for exercised assertions. Preflight refusal is BLOCKED setup; unexecuted later cases remain NOT RUN, never counted as successful OS tests. Failure preserves report/logs; existing state is not reset. Cleanup terminates only its own role children and listeners; deleting the VM or fixture root needs separate human authorization.
''',
'DISPOSABLE-RUNNER-VALIDATION.md':'''# Package validation

Actual unprivileged checks:30 standard-library runner tests pass, including fresh-process descriptor exclusion, fork/pickle negative controls, fixed JSON IPC roundtrip/type allowlist/partial-frame deadline, source inventory tamper/unlisted file checks, hostname/NIC/container/shared-mount/credential-path refusal, UID/GID/shell/group rules, exact PermissionError classification, fixed suite selection, timeout/failure persistence and nonsecret evidence sealing. These are not root/DAC qualification. A separate real child-process probe exercised the unchanged runner network_guard: UID1000 stayed unchanged, no_new_privs became true, AF_INET/AF_INET6/AF_PACKET socket creation refused and AF_UNIX remained usable. This is actual unprivileged per-process confinement, not a host policy change or distinct-UID proof. Evidence: kernel-runner-probe.json.

The nonroot executable preflight refuses before provisioning. This is the expected setup boundary, not a PASS for cross-UID protection. Final candidate Python syntax is checked without bytecode; no shell provisioning script is hidden in the runner. Existing test discovery and full applicable regression results are recorded separately. Exact Python3.14.4, SQLite3.46.1, cryptography46.0.5 and127 effective package versions were read from the tested environment and independently checked: zero version mismatches. No package installation occurred. Versions are not wheel-content attestations; the operator must supply reviewed offline artifacts and their hashes.

SOURCE-SHA256SUMS and the archive are independently verified. Future execution refuses an unlisted source file, changed source hash, symlink/hardlink, unsafe owner/mode, reused state root or mismatched dependency version. The package uses an operator-provisioned interpreter, not the mutable Core interpreter path. Current isolated test harness reuse of Core's read-only venv is not a future runner dependency.

Readiness means the source bundle, prerequisites, explicit human provisioning, tests and evidence collection are reviewable/executable. It does not predict that the first privileged VM run will pass. Genuine multi-UID qualification: NOT RUN — AWAITING DISPOSABLE VM AUTHORIZATION.
''',
'X1-X11-DELTA-REVIEW.md':'''# Experimental contract delta review

No experiment decision was approved. Retain the Gate6H exact X1–X11 question packet and Gate6I proposed selections: strict classifier refusal, deep unavailable, pinned skills memory, proposed Qwen8192/Gemma4096, keep_alive60 pending policy/topology, zero retry/fallback with20/180-second deadlines, nonstream/no TTS, unsafe/empty reply refusal, human topology/actor attestation and four accepts/eleven conditional operations/1500-second provider budget.

The four inputs and transport order remain: REST “Hello. Reply briefly.”; REST “What is two plus two?”; WS “Name one primary colour.”; WS “Please give a brief friendly greeting.” Legacy is visible; Granite is only observation and never history. Frozen Granite profile remains unchanged.

Newly discovered enforcement delta: the previous protected journal permitted a classifier substep for ordinal2 even though rules classify that input deterministically. Gate6J makes the protected root enforce that existing omission and total11. DISPATCH claims and truthful terminal reconciliation change security/accounting only. No new model/profile/behavior selection is proposed.

All eleven approvals remain pending. Effective endpoints, immutable identities, Gemma defaults, Qwen installed Modelfile, keep-alive residency, physical host/GPU/runtime conflict domains and external lifecycle actors remain unattested. No real AI/Proxmox access or generation was performed.
''',
'CONTINUOUS-IMPROVEMENT-REGISTER.md':'''# Continuous improvement register

Implemented J1–J8 in the new isolated candidate: dispatch capability consumption, sender credentials, terminal truth, runner process/IPC isolation, bounded checkpoint snapshots/SQLite work, protected operation envelope, strict denial classification, source/VM/dependency preflight and retained failure evidence. Tests and source diff are attached. Security assertions were not weakened.

Corrected the new runner module import-path error after its focused regression failure. Tightened only newly created candidate test-directory permissions when immutable-manifest validation correctly rejected group write. Corrected effective dependency version capture where system and venv metadata names overlap. These were ordinary engineering fixes, not reasons to request production permissions.

No redesign, historical reboot investigation, Golden re-evaluation, model lifecycle work, production installation, Git commit or push occurred. Remaining work is actual operator-controlled OS qualification and separately approved infrastructure/release decisions, not another hash inside a service-writable trust domain.
''',
'REMAINING-RELEASE-BLOCKERS.md':'''# Remaining approvals and release blockers

1. Review the exact Gate6J archive/source/sealed evidence and approve one specifically identified throwaway VM, its offline dependencies and the explicit provisioning/run proposal. No VM is currently approved. Genuine multi-UID qualification is NOT RUN.
2. Execute and independently inspect actual UID/GID, filesystem/socket, signer and adversarial results. A prepared package or setup refusal is not OS qualification. Approve separate production identity/key custody/supervision/import protections only afterward.
3. Qualify a real independent provider terminal witness, protected source/interpreter/dependency identity, service egress and external lifecycle-actor isolation, authority backup/recovery and operator emergency-stop procedures. Same-host root rollback remains outside the guarantee; a stronger external anchor needs separate review/approval.
4. Approve the exact X1–X11 decisions and human-only AI VM/host-key/model/endpoint/GPU/keep-alive/shared-residency attestations. No fixture metadata is a real attestation.
5. Separately review historical zero-use V2 disposition under the existing unattributed OPERATOR_STOP exception; preserve OPERATOR_REPORTED_MAINTENANCE and real terminal history. No retirement or successor command is signed here.
6. Later separately authorize inert CLOSED bootstrap, exactly one protected successor, immutable V3 installation, new human-run Gate5, bounded real provider qualification, four individual permits, Gate7 and any formal exit/measurement. No current deployment/pilot authority exists.

The next concrete operator action is approval of the VM execution proposal for the exact sealed bundle, not permission to mutate Nexus/Core/AI/Proxmox. The prototype's software audit does not independently confine arbitrary code execution with direct provider network access; that remains a production infrastructure boundary.
'''
}
for name,body in docs.items():(T/name).write_text(body)
print('wrote',len(docs),'review documents')
