"""Build review documents from recorded work. Final counts/identities added after runs."""
from pathlib import Path
P=Path(__file__).resolve().parent.parent
if (P/'SHA256SUMS').exists():raise RuntimeError('sealed packet')
def put(name,text):(P/name).write_text(text.strip()+'\n')
put('PROTECTED-RUNTIME-INTEGRATION.md','''# Protected runtime integration

Gate6I integrates the Gate6H journal with the existing Runtime, Store/D09, OwnedProvider/D06, EvidenceBridge/D04, Ingress and CheckpointWriter. `build_protected_isolated_app` requires the exact ServiceAuthorityClient and a shared writer/client/store graph. It validates the pinned source memory snapshot and proposed legacy limits. The historical builder remains solely for baseline fixtures; it is not the protected release entry point. Production factory still refuses.

The protected operator endpoint verifies signatures and peer identity. Runtime.apply_protected_command explicitly retrieves that already verified approval through the service client, checks existing state/coordinated prerequisites, and consumes a protected CLAIM before local OPEN/permit effects. No caller-supplied operator UID/PID or signing material is needed on this owner path; it is not exposed by Bearer routes. Approval alone never opens admissions. The historical signed control API remains covered and cannot bypass the same protected claim. The service cannot create APPROVE events. Before Store.accept, CONSUME durably burns the approved ordinal. BIND associates the actual D09 attempt ID. Failure between these steps leaves a nonrefundable incomplete acceptance and prevents provider activity. This is one accepted-attempt identity projected into D09, not an independent controller or alternative pilot counter.

Before each provider request, Store.begin records the local substep; SEND verifies its actual attempt/kind/resource/request association and records protected possible-send intent. The provider is invoked only after acknowledgment. Missing acknowledgment cannot be retried as a fresh send. SETTLE requires a helper-configured independent terminal reader; service-supplied clean flags/native response bytes are not accepted proof. The integration fixture supplies a separate synthetic provider witness. A real terminal witness is NOT implemented or qualified. The future multi-UID runner deliberately uses an always-unknown witness.

CheckpointWriter exports a read-only projection of journal state into the old highwater snapshot schema, preserving existing coordinated D04/D06/D09 validators. It has no protected DB handle and no signing key. The projection is backup evidence only. A sequence/seal token accompanies it. The helper checks the full fixed-path bundle, controller bindings, signed claims, exact accepted IDs/commitments, all sends, clean D06 and receipt joins before accepting CHECKPOINT. An old bundle is never authorization or a recovery root.

Runtime starts CLOSED_INITIAL or CLOSED_RECOVERY_HOLD and cannot open itself. Source/config/process drift, missing/corrupt authority, missing acceptance or stale checkpoint refuse. Invocation rebinding and automatic restore are absent. Terminal closure first stops admissions locally; pending protected sends survive stop. Helper unavailability downgrades local completion to CLOSED_INCOMPLETE. No terminal operation grants succession or reopening.

Actual qualification uses copied source, real accept/connect AF_UNIX sockets, Ed25519 dummy keys and fake providers. It does not establish production OS isolation, real inference, human presence, external D06 exclusivity or model identity. Storage fixture origins are now OFFLINE_FIXTURE; canonical application files remain unchanged.
''')
put('AUTHORITY-CLIENT-CONTRACT.md','''# Service authority client — protocol version 1

One request per connection: unsigned 4-byte network-order length followed by strict UTF-8 JSON, maximum 65,536 bytes. Exact envelope: `version`, `operation`, `arguments`. Version must be integer 1 (not boolean); duplicate keys, nonfinite values, extra fields and ancillary descriptors refuse. Whole read/write is bounded (configured at most 5 seconds), with at most eight accepted workers and no retries. Error reply is a fixed nonsecret refusal. A failed/missing reply is uncertain, not a refund.

| Operation | Exact arguments | Effect |
|---|---|---|
| READ | empty | Read protected public state; no secrets/signing capability |
| CHECK | expected {seq,seal}, allow_terminal boolean | Compare fixed controller state to protected history |
| CLAIM | expected, nonce | Burn delivery of an already signed operator command before local effects |
| CONSUME | expected, permit | Burn one authorized ordinal, never refund |
| BIND | expected | Read exact actual D09 ID from pinned controller path and associate it once |
| SEND | expected, ordinal, role, request_digest | Record possible-send for exact approved resource and actual D09 substep |
| SETTLE | expected | Consult fixed independent terminal reader; no terminal proof on wire |
| CHECKPOINT | expected, bundle | Bundle is exactly 32 lowercase hexadecimal characters, not a path; consult fixed snapshot root |
| TERMINATE | empty | Preserve local terminal evidence; incomplete/unknown never becomes complete |

ServiceAuthorityClient exposes read/check/accept/send/settle/checkpoint/terminal methods and has no journal, protected path, protected DB or private key. The derived backup projection is not a second authority. Calls are synchronous and bounded; runtime serializes one attempt. Conflicting concurrent calls may refuse on stale sequence, safely burning already committed operations.

Unix transport independently validates kernel SO_PEERCRED against pinned UID/PID and Linux process start/boot identity, before and after frame receipt. The client also authenticates the helper process and protected socket inode. PID/UID JSON claims have no meaning. Fixed helper-side readers receive no executable wire callbacks, SQL, arbitrary paths or imports. The dependency-injected Python readers are installer/test construction only.

Bearer REST/WS authentication grants none of these administrative powers. A compromised service can request fail-stop or cause denial of service; it cannot grant a permit, sign a command, refund acceptance or resolve remote uncertainty. Enforcing all possible network access by a compromised UID also requires the separately reviewed production egress/service policy; this candidate does not install that policy.
''')
put('OPERATOR-COMMAND-CONTRACT.md','''# Operator command client

OperatorCommandClient submits only an externally signed body. It contains no signing API. Operator endpoint accepts only `SIGNED` with `body` and 128-hex-character Ed25519 signature. Application service endpoint rejects SIGNED. Cryptographic verification is independent of kernel peer checks.

Reuse the existing exact signed body fields: verb, nonce, expires, bindings, checkpoint, payload. Nonce is 32 lowercase hex; expiry is strictly future and at most 60 seconds ahead; checkpoint is 64 hex. Bindings retain source, config, release, pid, invocation, epoch, boot, start, challenge. Approved identity and exact canonical bytes must match. No keys or runtime tokens grant operator status by themselves.

| Signed verb | Protected effect |
|---|---|
| RETIRE_AND_RESERVE_SUCCESSOR | Re-read exact terminal zero-use predecessor proof before/after signature verification. Atomically reserve one exact successor and nonce. Payload retains source/config/controller/live-state/archive identities and explicit unattributed-stop exception. |
| OPEN_HOLD | Approve opening only after current clean protected checkpoint; local runtime must separately CLAIM before opening. |
| AUTHORIZE_ONE | Approve one exact transport/session/request commitment after checkpoint. Does not itself accept an attempt. Outstanding approvals cannot be replaced or auto-expired into another permit. |
| TERMINAL_STOP | Approve terminal closure even during pending/unknown work. Does not settle providers or reopen anything. |

Every signed command nonce, claim and consumed permit survives restart. A claim committed without its local effect is an incomplete transaction requiring review, never a replay opportunity. Same-host root rollback remains outside the guarantee. Valid signatures prove key possession, not physical human presence; a separately qualified human signer/broker and approved process lifetime are required.

No production command has been signed or submitted. All signatures in tests are disposable. The original V2 OPERATOR_STOP and CLOSED_COMPLETE epoch remain untouched; operator-reported maintenance is not retirement authority.
''')
put('AF-UNIX-TRANSPORT-QUALIFICATION.md','''# Real AF_UNIX transport qualification

Gate6I adds pathname bind/listen/accept serving and independently instantiated service/operator clients. These are genuine Linux sockets, not socketpairs. Actual kernel peer credentials are checked. Current runs use one kernel UID; they are NOT cross-UID qualification.

Coverage includes valid/partial frames, whole-operation trickle deadlines, oversized frames, malformed JSON, duplicate keys, boolean/unsupported versions, unknown verbs, forged UID arguments, SCM_RIGHTS descriptor rejection/closure, concurrent clients, nonreading peers, broken pipes, stale process pins, socket replacement, wrong peer UID, signed replay, shutdown during partial request, command persistence and reopened authority state. Worker-start/shutdown race was found and fixed by registering and starting workers under one lock. Replies have a bounded socket send buffer and deadline.

Proposed runtime paths replace the ambiguous Gate6H ownership arrangement:

| Path | Owner/group/mode | Reason |
|---|---|---|
| /run/g6i | root:root 0755 | Traversal only for clients |
| /run/g6i/operator | root:approved-operator-group 0750 | Root helper can bind/restart; operator can traverse but cannot replace socket |
| /run/g6i/operator/control.sock | root:approved-operator-group 0660 | Operator may connect; service/agent excluded |
| /run/g6i/service | root:approved-service-group 0750 | Separate service endpoint, no directory mutation |
| /run/g6i/service/control.sock | root:approved-service-group 0660 | Service may connect; agent excluded |
| Protected journal root | root:root 0700; DB0600 | Service cannot read/write/replace authority |

No client gets group write to a directory. A root helper avoids giving an unrelated authority UID broad read access to service-private 0700/0600 state. Its implementation has fixed readers and no shell/admin/provider proxy verbs. Stronger dedicated nonroot authority deployment would need a separately qualified snapshot handoff; it is not silently assumed workable. The helper receives only a public verifier key. Root can read any same-host key; separation is from service UID, not from root.

Listener never unlinks an existing socket at startup. Graceful close unlinks only its own inode; stale crash sockets require human-supervised cleanup. New operator/service/helper PID or start identity requires reviewed provisioning/rebinding; no automatic restart authorization. Socket paths and every ancestor are checked for symlinks and writable ownership.

Implementation references: Linux documents pathname permissions and SO_PEERCRED in [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html). Descriptor reception/flags use [Python socket APIs](https://docs.python.org/3/library/socket.html). These API references do not establish the unrun OS qualification.
''')
put('MULTI-UID-DISPOSABLE-RUNNER.md','''# Disposable multi-UID qualification — NOT RUN

No separately approved disposable VM was located in the local task/qualification records. No new sudo, Docker/LXD, user mapping, account, helper, Proxmox or network operation was attempted. Gate6H's EPERM/unprivileged mapping limitations remain unresolved. Real distinct-UID status: NOT QUALIFIED.

Automated package is in the versioned candidate `disposable/qualify_multi_uid.py` and `disposable/qualify_all.py`. Syntax and nonroot refusal are tested here; privileged execution is not. It requires root as the authority identity plus preprovisioned g6i-operator, g6i-service and g6i-agent processes with three different nonzero kernel UIDs. It does not create accounts or install packages.

Future human provisioning, only after separate approval:

1. Create a throwaway Linux VM through the trusted human console, never Nexus/Core/AI/Proxmox itself. Record VM/machine identity and disposal approval. Remove/disconnect every NIC before execution; no shared production filesystem, credentials, SSH agent, secrets, mounted homes or host sockets. The runner refuses any interface beyond lo and known production home paths/hostnames.
2. Provision the three named non-login identities with distinct private primary groups. No sudo or shared supplementary groups. Root is the narrow authority process for this fixture. Prepare a reviewed Python environment with the candidate's tested dependencies, pytest/pytest-asyncio and Ed25519 cryptography; obtain packages before disconnection through the approved build process. No package install occurs in the runner.
3. Copy the reviewed release archive to `/opt/g6i-release`; verify FULL-SOURCE-SHA256SUMS independently. Make all source files root-owned/readable, directories traversable and no group/other write; no symlinks. The archive must extract `repo/`, harness and `disposable/` directly under that path. Preserve its reviewed digest outside the VM.
4. Privately create root-owned mode0600 `/etc/g6i-disposable-approved.json` with exactly machine_id (actual /etc/machine-id), scope `GATE6I_DISPOSABLE_ONLY`, network `NO_NIC`, release `/opt/g6i-release`. This marker is an operator declaration, not independent evidence of an approved VM. Keep approval and VM identity in the external operator record. `/var/lib/g6i-disposable` must not exist: occupied destinations refuse, never reset.
5. From that VM's trusted root console only, run the reviewed interpreter with `-B /opt/g6i-release/disposable/qualify_all.py`. No shell text or executable callbacks arrive over the authority socket. The runner drops the three client identities, sets no_new_privs and kernel-denies all socket families except AF_UNIX. No generation/network path exists. Keys are new disposable fixtures generated inside the operator child; no private key is printed or exported.
6. Review `/var/lib/g6i-disposable/qualification.json`, report.json and suite-stdout.txt. PASS requires all assertions and process-crash/transport suite exit zero. Export only minimized results, approved public identities and hashes; never export signing.key. Retain failure evidence and dispose of the VM through a separate human operation. A failure is not permission to broaden host permissions.

The cross-UID phase checks actual UID/PID values, key/root/release/config access denial, real peer enforcement, concurrent successor refusal, signed replay, one-use claims and attempt consumption, pre-send/remote-unknown preservation, whole application/controller/backup replacement refusal, and authority reopen preservation. Root-owned release/config have an actual ReleaseIdentityReader. The subsequent unprivileged regression suite covers individual rollback variants, crash windows, malformed protocols, source substitution and replay. Reports must distinguish cross-UID results from same-UID logical cases. Whole-host/root rollback is intentionally not claimed.

Runner design intentionally leaves the independent provider terminal witness unavailable. It verifies safe UNKNOWN behavior; real model qualification is a different approval. No production helper, unit, account or trust enrollment has been installed.
''')
put('ANTIROLLBACK-RESULTS.md','''# Antirollback results and limits

| Attack | Isolated enforcement | Limit |
|---|---|---|
| Controller or accepted-attempt rollback | Exact protected accepted rows, D09 IDs, commitments, claimed commands and source bindings must match | Real write denial requires distinct-UID qualification |
| Local ledger/substep rollback | Protected SEND history must still join local attempt/kind/request; pending intent blocks progress | A possible-send is not evidence of inference |
| Older backup recovery | Bundle token, clean coordinated joins and protected high-water checked online; backup never restores authority | Offline checksum validation alone grants nothing |
| Replace every service-writable file | Separate protected journal retains acceptance, claims and possible-send; actual whole-directory fixture rollback refuses | Current filesystem owner is shared in tests |
| Source/config/manifest substitution | Installer-pinned file digests, owner/ancestor/link checks and process start/boot binding | Real installed inventory/supervision approval remains pending |
| Signed command/permit replay | Unique durable nonce, one-use CLAIM and CONSUME; max four derived accepted rows | No refund/rebind/recovery API |
| Concurrent successors/consumption | SQLite BEGIN IMMEDIATE plus unique sequence/nonces and exact expected token | SQLite/platform durable storage assumptions apply |
| Missing/corrupt root | mode=rw and strict schema/chain/inode checks; no automatic creation or restore | Availability loss requires human recovery design |
| Crash after commit before acknowledgment | Durable result remains burned; replay cannot be treated as a fresh operation | Process crashes tested; actual VM power cuts not run |
| Service PID/invocation reuse | Kernel UID/PID plus process start/boot pin; approved bindings checked on transactions | New process approval is deliberately unavailable automatically |
| Root/whole-host rollback | NOT DEFEATED | All on-host authority and apparent proofs can be rolled back together |

An on-host root-owned ledger can protect against ordinary service-UID modification only after actual OS separation is qualified. It cannot independently attest that a host administrator/hypervisor has not restored the whole host. A stronger guarantee needs a separately administered anchor and independently approved durable-before-ack/recovery design. No off-host/cloud export was implemented.

Journal uses standard Ed25519 verification and SQLite FULL/DELETE transactions. Hash chains detect inconsistency within the protected domain; hashes are not the OS boundary. [SQLite atomic commit documentation](https://www.sqlite.org/atomiccommit.html) describes the durability mechanism and storage assumptions; this task does not claim power-loss qualification.
''')
put('SUCCESSOR-AND-PERMIT-TRANSACTIONS.md','''# Successor, signed claims and accepted attempts

Succession: fixed terminal proof → signed canonical payload/expiry/identity → second proof read → single RUNTIME_SUCCESSOR append under BEGIN IMMEDIATE → commit → acknowledgment. The existing explicit zero-use retirement and unattributed-stop exception fields are preserved. All examples are fixture predecessor identities. No historical V2 retirement or actual V3 successor exists.

Opening/permit: signed APPROVE event → runtime validates current local/coordinated prerequisites → durable CLAIM → local control/permit commit. CLAIM cannot be repeated even after local controller rollback. Lost local effect after CLAIM is an incomplete transaction and blocks progress.

Acceptance: exact unspent local permit and protected signed approval → CHECK → CONSUME (protected ACCEPT event) → D09 Store.accept transaction → BIND exact actual D09 ID → provider eligibility. Accepted ordinal derives from the single protected history, maximum four globally, fixed REST/REST/WS/WS order and one session per transport. No refunded failed attempt, replaced expired permit, automatic next permit or retry.

The helper's independent fixed reader compares actual local signed control rows with protected claims, accepted IDs with BIND, commitments and expiry with signed permits, and every provider substep with SEND. Interrupted CONSUME/BIND cannot be repaired by reducing the counter or restoring an older backup. Future recovery is human-reviewed, not an implemented convenience API.

Coordinated snapshot contains a derived highwater SQLite projection solely to preserve existing backup validators. The protected append-only history is authoritative; the projection has no writeback or restore path. Service graph has no protected database handle.
''')
put('POSSIBLE-SEND-AND-D06-ACCOUNTING.md','''# Possible-send and D06 accounting

Runtime order: fixed request serialization/bounds → D06 precheck → local D09 POSSIBLE_SEND → protected SEND acknowledgment → OwnedProvider/D06/domain acquisition and fake transport. A conflict before local begin remains a refusal; races or lost acknowledgment after intent remain conservative uncertainty. Protected role maps to an installer-provided exact contract digest, and the actual local endpoint/model/profile/request/attempt must match before SEND.

Allowed per-attempt order is optional legacy_router, exactly one legacy_trivial or legacy_normal, then granite. Repeat/conflicting roles refuse. The original four requests permit at most three classifier, four responder and four observer operations. There is no retry, fallback, streaming, auto load/unload or next-permit action.

A SEND record proves intent may have reached transport; it does not prove inference. SETTLE accepts only the helper's configured independently associated terminal witness. Tests supply fake responses/witnesses. Socket closure, client cancellation, local timeout, service restart and an untrusted clean flag never establish remote completion. Missing witness leaves protected pending state even if a local component claims terminal completion.

The existing OwnedProvider preserves D06 remote unknown after cancellation/uncertain send. D04 joins remain actual observation commits, never inferred from delivery or provider completion. A D04 append/join fault prevents the next checkpoint/permit; legacy delivery truth remains separate. Terminal closure retains pending intent and incomplete state.

No real endpoint/GPU topology or external actor exclusivity was verified. D06 only coordinates participants that honor its lease. Other clients, unloaders, alias writers, provider restarts and shared GPU actors require independent inventory/isolation and an approved exclusive qualification window. No live model was contacted or changed.
''')
put('CRASH-RECOVERY-TESTS.md','''# Crash and concurrency qualification

New runtime tests inject failures before/after protected CLAIM, ACCEPT, BIND, SEND, SETTLE and CHECKPOINT commits. Fresh child processes terminate with os._exit at CONSUME/BIND/SEND/SETTLE before/after commit; reopened reads prove zero or one durable event, never manufactured success. Gate6H subprocess successor/permit/send/settle tests remain in the full suite.

Controller faults cover local possible-send commit, provider terminal commit, receipt append before join and receipt join. Coordinated publication faults cover before/after directory publication. These failures retain accepted ordinals and block a next permit. Lost SEND acknowledgment leaves pending intent before any provider call. Missing terminal witness refuses settlement. Stop during a blocked provider preserves both protected pending intent and D06 remote unknown.

Concurrency covers operator permit races, service consumption races, concurrent reads, bounded worker admission and inherited successor races. The listener shutdown race found during testing was fixed without weakening its assertion. Actual partial-read/nonreading shutdown, broken pipes, process identity drift and journal reopen/replay are covered.

Reopen is not authority to reopen an epoch. New service/helper/operator process identities need explicit provisioning; terminal state is monotonic, COMPLETE may downgrade to INCOMPLETE, never the reverse. No process crash or timeout refunds an attempt. Whole-host power-cut tests and genuine UID separation were not run.

Initial test-authoring and later engineering/environment failures are retained in evidence/runs with their source identities. No failing assertion was removed or marked skipped. TEST-RESULTS.md distinguishes intermediate revisions and the final suite.
''')
put('REST-WS-INTEGRATION.md','''# Existing REST/WS graph with protected authority

The new tests run build_protected_isolated_app over the existing FastAPI/Ingress/Runtime/OwnedProvider/D04/D06 graph. They exercise REST authentication before request body access, WS authentication and actual handshake/continuation/reply, CLOSED refusal, signed future permits, global four-attempt cap and fixed REST/REST/WS/WS order. A valid app Bearer cannot submit operator commands or manufacture approvals.

Four-turn fake-provider execution verifies eleven conditional operations, legacy-only client replies, no Granite text in client output or history, receipt joins and clean completed ownership. Source-backed deterministic rules precede Gemma classification. Malformed/low-confidence/tool/deep results fail without fallback. No operational dispatcher/confirmation execution/TTS is imported into the graph; existing boundary tests are preserved. No startup inference or automatic next permit occurs.

Protected factory enforces pinned source skills.md snapshot (raw SHA256 3a61af6054795cad154b5de00e4185063d32e08e592aba315bc8ef1560e6d4a2, derived snapshot e4fc564a6b52728736b50165a78467a383be82dadfeebcb7fade43cdd8489c29), proposed legacy contexts/deadlines and exact protected client wiring. These are offline proposal requirements, not operator approvals.

Requests remain exactly: REST “Hello. Reply briefly.”; REST “What is two plus two?”; WS “Name one primary colour.”; WS “Please give a brief friendly greeting.” These fixed pilot inputs are not real conversations. Fake responses are explicitly synthetic and not predictions of model behavior.
''')
put('MODEL-CONTRACT-DELTA-REGISTER.md','''# Proposed contract deltas — every X decision remains pending

The Gate6H exact original X1–X11 questions remain authoritative in its sealed decision packet. This table records Gate6I engineering against the operator-provided recommendations; it does not replace the original wording or grant live approval.

| ID | Recommended proposal / Gate6I treatment | Remaining condition |
|---|---|---|
| X1 | Strict malformed/low-confidence/failed classifier refusal; protected runtime regression coverage | Operator decision |
| X2 | Deep branch unavailable | Operator decision |
| X3 | Pinned source-backed skills.md snapshot; protected factory rejects empty memory | Operator approval of frozen snapshot and source identity |
| X4 | Normal qwen3-nothink context corrected from isolated32768 to proposed8192; output150, deadline180s | Installed Modelfile/effective context attestation and approval |
| X5 | Trivial Gemma4096/output80/deadline180s retained | Actual responder-default attestation and approval |
| X6 | Legacy keep_alive60 remains an explicit proposed profile | Effective policy, residency/topology and approval |
| X7 | Zero retries/fallback; classifier20s/responder180s; Gemma classifier4096/output64/temp0.1 | Operator decision and later provider behavior qualification |
| X8 | Nonstreaming REST/WS, no TTS | Operator decision |
| X9 | Refuse empty cleaned replies, action tags/native tool proposals | Operator decision |
| X10 | Require human-attested host/GPU/Ollama, lifecycle actors and shared-residency decision | Independent attestation plus operator decision |
| X11 | Four accepted attempts, up to11 conditional calls, aggregate1500s provider deadlines | Operator decision; excludes delivery/human/checkpoint/unknown time |

Granite unchanged: frozen alias hermes-candidate-granite41-30b-q3km-64k, profile jarvis.p7.ollama.granite41.b1r2.v1, context64000/output128/deadline180s/keep_alive60/nonstreaming/think:false; passive observer with no client output. No settings activated in production. All effective model manifests/endpoints remain UNVERIFIED; fake topology stays OFFLINE_FIXTURE.

Other genuine changes: fixture persistence origin LIVE→OFFLINE_FIXTURE; no production schema migration. Protected signed approval now precedes a separately consumed attempt; this closes an accounting gap without adding attempts or changing original transport order. Delivery deadline and independent witness/deployment choices remain separate approval/qualification items, not invented X identifiers.
''')
put('HUMAN-ATTESTATION-CHECKLIST.md','''# Human-only external readiness checklist — all pending

Use the already trusted Proxmox management console192.168.0.50 and the independently selected guest console. Expected AI address192.168.0.200 and historical VMID200 are hypotheses, not verified identity. No commands below were run by Gate6I against management/AI hosts. Export only allowlisted nonsecret results, identity/UTC/provenance and public fingerprints; never raw logs, full environments, credentials, private keys or model conversations.

| Required attestation | Exact human-only method / acceptable record |
|---|---|
| AI VM identity | Privately inspect `pvesh get /cluster/resources --type vm --output-format json`, then `qm config VERIFIED_VMID` on its real node. Match independently maintained VM/storage/MAC inventory; export only node/VM/name/MAC/hostpci mapping. |
| Guest/network relationship | Guest console `hostnamectl --static`, `ip -br address`, `ip -br link`; match guest NIC to VM inventory and trace proxy/NAT/network namespace to the serving endpoint. |
| Public SSH host key | Guest console `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`. Compare with an independently trusted expected fingerprint and record its source. No prior anchor means candidate expected fingerprint, not enrolled trust. No SSH bypass/accept-new/known_hosts edits. |
| Physical GPU and ownership | Proxmox `lspci -D -nn -s VERIFIED_BDF`, inspect its sysfs driver/IOMMU mapping; guest `nvidia-smi --query-gpu=uuid,pci.bus_id,name,memory.total --format=csv,noheader` if installed. Match pass-through/vGPU/MIG and other consumers. No resource changes. |
| Ollama service identity | `systemctl show ollama.service -p User -p Group -p MainPID -p ActiveState -p SubState -p NRestarts -p InvocationID -p FragmentPath -p DropInPaths`; privately correlate listener via `ss -ltnp`, executable/version/hash and protected model-store ownership. Do not print ExecStart/cmdline/environment. |
| Effective router endpoint | Source/config hash plus human private precedence trace of exact `JARVIS_OLLAMA_BASE_URL` override and config.yaml models.ollama_base_url. Emit only validated scheme/host/port/model and override-present boolean. Never dump environment. V2 stopped => CONFIGURED_LAUNCH_RECONSTRUCTION only. |
| Effective responder endpoint | Repeat loader/override/namespace mapping independently for responder. localhost in YAML alone is insufficient; no app import that initializes/logs unrelated settings. Future CLOSED accessor must precede provider access and emit only approved nonsecret fields. |
| Gemma immutable identity | On independently verified actual serving host: metadata-only `ollama list`, `ollama show --modelfile gemma3:4b` after verifying installed-version tool behavior. Verify full manifest SHA256 and all referenced blob digests in actual protected store; abbreviated ID/alias is insufficient. Export digest/parameter allowlist only. |
| Qwen immutable identity | Same for qwen3-nothink; compare installed Modelfile/no-think behavior and num_ctx8192 with reviewed source. No inference to discover identity. |
| Granite immutable identity | Same for frozen Granite alias/profile; immutable manifest/blob identity and exact runtime/store relationship remain required despite frozen request profile. |
| Effective contexts | Record classifier4096, proposed trivial4096, proposed normal8192 and frozen Granite64000 with explicit inherited/overridden defaults and installed policy version. Behavior requires later separately approved bounded provider qualification. |
| Keep-alive/server policy | Human privately read only approved values OLLAMA_KEEP_ALIVE, OLLAMA_CONTEXT_LENGTH, OLLAMA_MAX_LOADED_MODELS, OLLAMA_NUM_PARALLEL, OLLAMA_FLASH_ATTENTION, OLLAMA_KV_CACHE_TYPE. Record unset/precedence; no whole Environment output. |
| Shared resource domains | Map each endpoint/model to actual host/runtime/GPU/VRAM; different ports/aliases may share one GPU/Ollama service. Record explicit shared-residency choice and capacity qualification. |
| External lifecycle actors | Inventory relevant services/timers/cron/containers/supervisors/admin clients, legacy idle unloaders/wake and alias/store writers. Record owners/rights/schedules and proposed exclusive window. No connection observed is not proof of no actors. |

No chat/generate/run/pull/create/stop/load/unload requests. No trust enrollment or configuration/network/GPU change is authorized. Refresh attestations after migration, host key, model/store, service/runtime or GPU changes. These checks neither approve X1–X11 nor open a pilot.

Detailed frozen procedures remain in Gate6H HUMAN-ONLY-AI-HOST-ATTESTATION.md, HUMAN-ONLY-LEGACY-PROVIDER-ATTESTATION.md and D06-RESOURCE-TOPOLOGY-REQUIREMENTS.md; their exact hashes are recorded in SOURCE-AND-MANIFEST.md.
''')
put('CONTINUOUS-IMPROVEMENT-REGISTER.md','''# Continuous improvement register

| Finding | Implemented isolated correction | Regression evidence |
|---|---|---|
| Companion not on runtime acceptance/provider path | Typed service/operator transport; mandatory protected graph; CONSUME/BIND/SEND/SETTLE/checkpoint hooks | Four-turn graph, REST/WS, crash/unknown/refusal tests |
| Approval previously burned attempt immediately | Separate signed APPROVE, one-use CLAIM and actual CONSUME; exact D09 association | Approval≠acceptance, concurrent consumption, no refunds |
| Local rollback could replay opening | Protected CLAIM before local control effect; exact claimed-control reconciliation | Opening rollback/replay regression |
| No accept-based service transport | Bounded real listener and two independently instantiated clients with kernel identity pins | Partial/malformed/FD/concurrency/replay tests |
| Worker registered before start could race shutdown | Register and start under same lock; refuse late worker after stop | Shutdown-during-partial-request regression |
| Privileged reader could follow service SQLite paths | Bounded O_NOFOLLOW file read and query-only in-memory SQLite snapshots, ownership/link/digest checks | Symlink/hardlink/oversize/digest/atime tests |
| File-read access time changes looked like tampering | Compare only identity/content-relevant stat fields, retaining mtime/ctime/size checks | Dedicated atime regression; intermediate failure retained |
| Service-controlled FIFO could block a privileged snapshot read | Nonblocking no-follow open, then regular-file/size/owner validation | FIFO regression in separately preserved release-r2 |
| Helper failure could leave apparent complete stop | Downgrade local terminal to CLOSED_INCOMPLETE | Missing-authority stop regression |
| Model proposal mismatch | Normal context8192 in isolated profiles and protected factory; frozen Granite unchanged | Four-turn request assertions and source qualification tests |
| Empty-memory fixture could be accepted as recommended graph | Require exact pinned source procedural snapshot | Empty-memory protected factory refusal |
| Synthetic records labeled LIVE | Candidate attempts/receipts/backup validation require OFFLINE_FIXTURE | Explicit origin test plus full baseline |
| New distinct-UID environment not authorized | Automated guarded future runner and exact human provisioning instructions | Syntax/nonroot refusal tested; privileged execution pending |

No architecture-wide redesign, historical event rewrite, production source edit, package installation, commit or push. Earlier candidates remain sealed. Test-authoring, snapshot-reader and disposable filesystem failures are recorded rather than hidden; final tests must pass after fixes.
''')
put('REMAINING-APPROVALS.md','''# Remaining approvals and blockers

1. Separately approve/provision the disposable no-NIC VM and run the complete multi-UID package. Current status NOT RUN/NOT QUALIFIED. Review resulting DAC, socket ownership, signer isolation, process and crash results before production identity provisioning.
2. Approve or revise the original exact X1–X11 decision packet. Engineering uses the requested recommendations only. X4/X5/X6/X10 remain dependent on actual model/policy/topology attestation. No silence or continued engineering implies approval.
3. Human-only independently trusted AI VM/host-key/endpoint/model/GPU/lifecycle actor attestations. No effective model identity is VERIFIED. No new SSH trust enrollment without its separate approval.
4. Qualify the independent provider terminal witness, protected release/process supervision, dependency/environment identity, human signer/broker presence and key custody, durable authority backup/recovery and emergency-stop runbook. Dummy witness and same-UID fixtures do not substitute for these.
5. Review source/tests/manifest and approve release. Then separately authorize identity provisioning, inert CLOSED bootstrap needed for exact live-process binding, historical V2 disposition under the explicit unattributed-stop exception, exactly one signed durable successor and immutable V3 installation/attach. No automatic rollback to V2 or epoch reopen.
6. New Gate5 private human positive authentication plus zero-generation readback; separate bounded real provider/resource qualification; then, only with permits, original four-attempt Gate6 pilot; final Gate7 reconciliation. Measurement and formal P7 exit remain closed.

Exact next operator action: review the sealed Gate6I source/evidence and approve a specific disposable multi-UID VM qualification run using the supplied provisioning/runner package. X1–X11 and human-only infrastructure attestations can be reviewed independently. This is a future approval boundary, not a request to install or activate production now.

V2 historical epoch606a991a06b74fd79ed72b308417cc3f stays permanently retained. OPERATOR_REPORTED_MAINTENANCE does not rewrite OPERATOR_STOP or establish independent Proxmox attribution. Retirement and production succession remain NOT AUTHORIZED.
''')
