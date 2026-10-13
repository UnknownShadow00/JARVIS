"""Generate review documents; source artifacts remain in the isolated archive."""
from pathlib import Path
import json
R=Path(__file__).parent
m=json.loads((R/'candidate-manifest.json').read_text());p=json.loads((R/'preservation.json').read_text())
rev=m['revision'];original=m['original_revision']
docs={}
docs['CANDIDATE-PROVENANCE-AND-PRESERVATION.md']=f'''# Candidate provenance and preservation

Gate6C identity `{original}` is SHA256 of its **13-file source-and-qualification checksum manifest**, not a Git commit, Git tree object, or digest of every file in `/tmp`. Verified against the actual files, the preserved Gate6C manifest, and evidence seal `dca9b64c69a4f290582f2f75a99d0655ae76048622fc6b9d54d42b28b8da1d8e`. Candidate has no `.git`. Its base is canonical V2 commit `bd53dbc799fb9284a21fae8cce3f5d9539e31141`.

Original source archive: `{p['original']}`. Separate revised artifact: `{m['path']}`. Both are nonproduction, outside `/home/jarvis/JARVIS`, with private exclusive parent directories. Original `/tmp/jarvis-gate6c-candidate-thseen50/repo` was not modified. Further tests used `/tmp/jarvis-gate6d-tests-WCbozC3X`; the archive itself was never imported by a running application. Local engineering mirror is `/home/nexus/.local/share/jarvis-gate6d-review/engineering-r1`.

Full original source: 580 files, manifest SHA256 `{p['full_source_manifest_sha256']}`. Revised source: 581 files, full manifest `{m['full_source_manifest_sha256']}`. Revised 14-file source/qualification identity: `{rev}`. Patch against Gate6C: `{m['patch_sha256']}`. No Git commit, merge, install or push. Full manifests and patch are in the new evidence directory; revised source is in its separate `revised-candidate/` member.

The complete original tree inventory records names, file types, modes, sizes and link counts. No symlinks or hard-linked regular files were found. Source preservation uses Gate6C's original source allowlist and exact hashes, with the committed baseline config deliberately distinguished from the deployed SHADOW config. Compared with approved V2 Git content, additions are seven `candidate_v3` modules and its test; `tasks/loop-log.md` is the sole other content difference. All 119 canonical app files and 208 original test files remain unchanged. Qualification harness files were separately bound in Gate6C.

Ten generated files were present in the original repository: an agent-task fixture, trace and audit logs, a bytecode cache and six three-byte temporary audio fixtures. They were inventoried, excluded from preservation, and left in place. The original revision's 13 bound files are preserved in full. An initial archival guard stopped on unexpected audio files before any archive was created; the explicit exclusion list was then reviewed. No generated log/audio content was copied into the release archive.

No runtime D06/D09/controller namespace, real environment file, credential file, runtime cache or generated log belongs to the source allowlist. Every preserved baseline file matches reviewed V2/Gate6C source; a private-key-marker check found none. `.env.example` is a tracked source template. This is source provenance and structural exclusion evidence, not comparison against unknown secret values. Real secrets and process environments were not opened or hashed, and no categorical secret-value scanner claim is made.

Running-service cwd/executable remain canonical; reviewed production app source contains no candidate import or candidate-directory reference, and the venv contains no `.pth` files. No import path or unit was installed/changed. The service was already running before the candidate existed. These facts exclude an accidental import through reviewed application wiring; uninspected environment overrides and arbitrary same-UID code replacement are not claimed impossible.

Files and directories were fsynced and contents rehashed after preservation, and the original manifest was reverified after engineering. Storage is private and checksum-verifiable, **not immutable or privileged-tamper-resistant**. Its owner can change it. No root-owned archive, filesystem snapshot or off-host disaster recovery is claimed. Actual power-loss qualification remains outstanding.
'''
docs['SECURITY-FINDINGS.md']='''# Independent security findings

Verdict: **V3 CANDIDATE NEEDS FURTHER HARDENING**. No observed production breach or mutation. No critical finding established. The following severities describe impact if these isolated components were used as a release; they do not imply an exploitable live V3 listener.

| ID | Severity | Finding / evidence | Disposition |
|---|---|---|---|
| F01 | High | Store.begin accepted arbitrary operation names and new substeps on already settled attempts | Fixed: only three named generation steps; active accepted attempt and router/responder/Granite ordering required. No lifecycle kind permitted |
| F02 | High | Intermediate symlink ancestors bypassed lexical storage exclusions; backup could follow a receipt symlink | Fixed static path checks and receipt type validation. Race-free dirfd publication under protected ancestors remains unqualified |
| F03 | High | FORENSIC backup used zip(lines,joins), silently overlooking missing joined receipt lines | Fixed: fewer receipt records than durable joins always refuses, even after an attacker recomputes manifest checksums; extra orphan bytes remain forensic evidence |
| F04 | Medium | Terminal-stop approval committed before terminal closure, leaving a crash gap | Fixed: signed control record and terminal state share one transaction; local stop latch precedes storage; before/after commit tests |
| F05 | Medium | A stop or timeout concurrent with completed local send erased delivery truth | Fixed: completion callback records actual local success, including late success; unknown can advance to known local completion without reopening; history remains legacy-only |
| F06 | Medium | Peer tuple parser accepted list/bool UID equality and raised unhandled errors on malformed tuples | Fixed exact tuple/length/integer checks, bounded signature and hexadecimal checkpoint digest |
| F07 | Medium | JSON exponent overflow accepted infinity despite rejecting NaN constants | Fixed finite parse_float; duplicate-key parser was already strict, including canonical continuation parser |
| F08 | Medium | Malformed ASGI events, mixed text/binary and Unicode surrogates could escape refusal handling | Fixed shape/type/UTF-8/more_body checks; terminal refusal before provider work |
| F09 | High | Canonical Granite bridge checked request body but not endpoint/profile and all frozen limits | Fixed exact resource/profile/limit check before named possible-send. Trusted fixture observer remains deliberately substitutable; production factory still refuses |
| F10 | Medium | SQLite integrity/schema checks did not validate all logical permit/ordinal/lease associations | Fixed shared ledger consistency validator for live fixture and backup inspection |
| F11 | Medium | Checkpoint quiescence check happened before acquiring writer lock | Fixed: quiescence check moved inside the shared lock |

55 new adversarial test cases added; original 94 candidate tests retained without alteration. Initial adversarial failures and all subsequent runs preserved. Some added tests document existing defenses, rather than a newly discovered bug. In particular duplicate WS continuation keys were already rejected; this was a tested nonfinding.

| Release blocker | Severity | Remaining requirement |
|---|---|---|
| R01 | High | Authority accepts a caller-supplied peer tuple and verifier result; no kernel peer extraction, protected human signer/helper, real process identity or independent OS identities. Same jarvis UID can replace source/state or supply fixture authority |
| R02 | High | Predecessor `archive` is a nonempty string, not independently read/validated V2 closure evidence. Reservation uniqueness is per caller-selected parent, not a protected global lineage authority. An older DB replacement or alternate root can evade meaningful high-water protection outside the fixture trust model |
| R03 | High | Injected provider asserts known_terminal; no real bounded response reader or authoritative D06 endpoint-wide coordinator. Local leases cannot fence external callers/lifecycle operations |
| R04 | High | Single responder selection, unconditional L1 routing, prompt/memory/parser/cleaner and L2 confidence differ from legacy source. Effective endpoint, exact model digest and live qualification unresolved |
| R05 | High | Production factory/adapters are absent; disconnected-client observation, origin policy, real D04/D09 association, supervised final checkpoint/drain and OS/filesystem failure behavior are not release-qualified |

These are explicit technical release blockers. They are not reasons to deploy experimental defaults or mutate the predecessor. The review completed useful isolated fixes and regression; resolving protected identity, actual provider selection and real deployment behavior crosses separate approval/implementation boundaries.
'''
docs['ATTACK-SURFACE-REVIEW.md']='''# Ingress, permissions and provider reachability

Reviewed all seven candidate modules and the new tests directly, with canonical `app/server.py`, `pilot_safety.py`, router/client/prompt/complexity/direct-response and passive observation dependencies. Original source is byte-bound to V2 and preserved Gate6C; prior authority documents were read with Gate6B's rejection of Granite-visible output retained.

Candidate path: Ingress Bearer comparison → exact REST body or WS continuation/text → Runtime.session + commitment + ARMED_ONE → Store.accept transaction (spent permit + accepted row + event) → canonical pre-turn capture → optional LEGACY_ROUTER → LEGACY_RESPONDER → local client delivery/history → GRANITE → passive parser/evaluator → minimized receipt append → D09-like join → SETTLED → coordinated fixture checkpoint → CHECKPOINT_HOLD. No next permit is automatic. Four accepted turns trigger terminal cap closure.

| Surface | Result |
|---|---|
| REST /chat POST | In-process ASGI implementation; constant-time exact single Bearer, exact message field, one continuation header, 16KiB body and 8KiB message limits; malformed/scope/auth/concurrent input cannot create provider authority |
| Other HTTP paths/methods | Candidate 404/405, never legacy fallback; no /open, /confirm, /tasks, /resource/wake or alternate model route |
| WS /ws | Auth before accept; no-message connect/disconnect generates nothing; bounded canonical continuation; exact text frames only; binary/mixed/unknown/surrogate frames terminally refused |
| WS controls | Continuation validates existing Core-owned session and transport, never opens/arms. Duplicate JSON keys already refused by canonical parser. Idle timeout closes; no reconnect replay |
| Direct Runtime.request | Explicit authenticated bool is a trusted internal seam, not real middleware proof. Requires permit/session/message binding; no endpoint/model/permit selector argument |
| Direct Store.begin | Hardened named generation kinds and ordering, accepted-unsettled owner, no active/unknown lease. Methods remain internal capabilities; malicious same-process code is not a separate principal |
| Provider completion callback | No retry/evaluation replay. Late result cannot clear unknown or reopen. Late delivery completion is now recorded truthfully; provider remote completion still needs an authoritative adapter |
| Factory/startup | build_production_runtime always refuses. Runtime starts CLOSED_INITIAL, CLOSED_RECOVERY_HOLD or retained terminal, never restores OPEN from audit |
| Operational imports | Candidate has no server/LLM client/voice/tool registry/subprocess/socket/HTTP client import. Canonical observer reaches pure passive context, request, parser, evaluator and observation projection |
| Tools/TTS/voice/lifecycle | No executor capability or tool schema in candidate request construction; tool calls/action-tag proposals refuse. Model lifecycle operation names now rejected even at Store boundary |

There is no candidate exception branch calling `_process`, `_process_stream`, the original router fallback, error speech or unrestricted LEGACY handlers. On provider/proposal/parse/delivery/receipt/checkpoint failure, acceptance remains consumed and subsequent admissions close. Existing production remains closed-only under its own unchanged full graph tests; candidate passing those tests does not qualify mounting it into that graph.

Unqualified integration: candidate does not implement canonical origin restrictions, production middleware/lifespan/route mounting, credentials or socket listener. Ingress awaits request work before receiving further ASGI events; prompt disconnect/concurrent-frame detection during a long provider operation needs a reviewed receiving task or adapter. Runtime concurrency/cancellation tests are not proof that a real disconnected client is promptly observed. No in-process mutable bool or user-supplied authentication flag can be used as a release auth boundary.

Control permits bind source/config/release/PID/invocation/epoch/boot/start/challenge, checkpoint, nonce/expiry and session/request/transport. Explicit ordinal/resource/unit/Gate5/lineage-root binding through an authenticated release manifest and actual process facts is incomplete. Fixture string equality does not attest a running service identity.
'''
docs['LEGACY-CONTRACT-COMPARISON.md']='''# Exact legacy behavior delta

Evidence: `legacy-behavior-matrix.json` generated from reviewed pure original source by `analyze_legacy.py`, plus candidate runtime. No model was queried and no model classification result was invented. All four original inputs are unchanged.

| Original input / transport | Direct response | Original intent route | Model/output if intent=respond | Gate6C/6D candidate delta |
|---|---|---|---|---|
| Hello. Reply briefly. / REST1 | None | Model router required; classification/confidence unknown | trivial: gemma3:4b / 80, think=false | L1 calls a router; L2 asserts respond/.9. Both use the single configured responder, omitting complexity selection |
| What is two plus two? / REST2 | None: word arithmetic is not numeric expression | Deterministic respond/.9; no model classifier needed | normal: qwen3-nothink /150, think=false | L1 adds an unnecessary router transmission; L2 matches only this rule outcome, still no complexity contract |
| Name one primary colour. / WS1 | None | Model router required; result unknown | normal: qwen3-nothink /150, think=false | L2 substitutes asserted classification; fixed responder/prompt differ |
| Please give a brief friendly greeting. / WS2 | None | Model router required; result unknown | normal: qwen3-nothink /150, think=false | Same delta; substring “greeting” is not original trivial “hello/hi” rule |

The model/output column is a conditional pure-source result using configured model names. Real classifier results for three inputs and effective deployed endpoint/model metadata remain UNVERIFIED. A nonrespond original classification can select tools, memory, vision, confirmation or deep reasoning; candidate must refuse it without execution.

| Behavior | Original source | Candidate / qualification status |
|---|---|---|
| Router parser | Four output fields, permissive parsing and error→respond fallback, confidence threshold/confirmation | Strict two-field intent/confidence, respond-only, explicit threshold, no fallback. New prompt/parser/refusal contract needs approval |
| Complexity | Trivial/main/deep models;80/150/700 outputs | One responder StepContract for every input. Multi-contract selection remains new implementation after decision |
| Prompt | JARVIS_SYSTEM_PROMPT including action/emotion tags, procedural-memory prompt_context; optional context/project | Explicit injected system string, optional immutable snapshot; no approved text/hash or equivalence established |
| Memory | Procedural context read even with optional model memory clients off | NONE/SNAPSHOT selection required; no runtime memory writes or model-backed retrieval |
| Response processing | clean() plus emotion handling/broadcast; error narration | Raw bounded native content after proposal checks, no response_cleaner/emotion broadcast. Client text formatting can differ |
| REST | ChatResponse reply/intent/confidence/dry_run/active; background observation scheduling | Same tested envelope fields; entire isolated request waits through observation/checkpoint after sending body. Actual disconnect/background integration unqualified |
| WS | Legacy reply envelope; may stream and invoke TTS | One final reply only; no streaming, TTS or voice. Origin policy not wired |
| History | Pre-turn bounded user/delivered legacy capture for shadow; ordinary build_prompt does not replay this chat history | Same bounded pre-turn Granite history role; only delivered legacy assistant content. Candidate responder also receives current user + system, not historical conversation |
| Error behavior | Classifier fallback, up to4 client tries,600s client timeout, error speech | No retry/fallback/error speech; finite per-substep/delivery limits, failure consumes accepted budget |
| Ordering | Legacy/shadow scheduling not proven endpoint-serialized | Proposed router→responder→delivery→Granite→receipt→checkpoint, peak1 in fake tests |

A returned string is insufficient qualification. The adapter preserves client-response ownership but is not an equivalent implementation of the original experiment. Source/rules evidence cannot establish stochastic classification or byte-equivalent model output. Golden remains historical12/20 with eight known failures; no live rerun.
'''
docs['L1-L2-ROUTER-DECISION.md']='''# Proposed router decision — operator approval pending

Recommend **L1 with the audited original deterministic rules first, then one bounded model classifier only when the original rules return None**, followed by audited original complexity selection among separately qualified responder contracts. This is a recommendation, not an approved policy or implemented live default. The existing L1 candidate currently calls its router for every turn and has one responder contract; those limitations remain explicit.

L2 can be programmed to label the four strings respond, and deterministic complexity selection can reproduce configured model choice conditional on that label. It cannot establish that the original model classifier would choose respond with the same confidence for inputs1,3,4. Their original deterministic classifier returns None; only input2 is deterministically respond/.9. None has a deterministic direct reply. Exact-input membership plus invented .9 is a changed experiment. No approved strings were replaced and no canned replies were introduced.

| Option | What is preserved | Qualification/approval burden |
|---|---|---|
| L1 rules-first (recommended) | Original deterministic path on input2; model routing role for1,3,4; conditional gemma/qwen response selection | Pin actual endpoints/model digests, bounded router parser and approved prompt, confidence/no-fallback refusal policy, both responder contracts, endpoint ownership/actor control, request/response/time limits and serial timing |
| Existing candidate L1 | Model-backed route role, legacy visible output | Adds classifier call on input2, omits original four-field parser and complexity responder mapping; cannot be approved as equivalent unchanged behavior |
| L2 | Original strings, possible deterministic complexity rules, reduced transmission count | Requires explicit approval that classifier behavior/confidence is substituted. No evidence currently supports equivalence for three inputs |

With all four turns successfully classified respond: rules-first L1 would produce3 router +4 responder +4 Granite transmissions =11, versus candidate L1's12 and L2's8. All cases are still four accepted conversations and four observation submissions if all settle. Failed accepted turns consume budget; no replacement. Eleven is a proposed conditional accounting plan, not an authorization or observed provider count.

New qualification must exercise malformed/low-confidence/nonconversational/tool proposals, model-selection identity, exact prompts/memory/cleaner, bytes/timeouts/possible-send, cancellation, and shared-endpoint serialization. Real model tests require a later explicit real-provider authorization; this task authorizes none. The operator must choose L1 versus a deliberately revised L2 contract and explicitly accept each behavioral delta.
'''
docs['PROPOSED-LEGACY-PROVIDER-BINDINGS.md']='''# Provider contract proposal G6D-LP-1 — NOT APPROVED

No proposal below is encoded as a live default. JSON companion `provider-binding-proposal-v1.json` is a review artifact only. The current production factory remains unavailable. All legacy effective endpoints and exact model content/version digests are **UNVERIFIED**. Config YAML names localhost:11434; app/config.py supports protected JARVIS_OLLAMA_BASE_URL override. No environment or credential inspection was performed. Granite's .200 address is not substituted for legacy.

| Field | Legacy router | Legacy responder: trivial / normal | Granite observer |
|---|---|---|---|
| Configured endpoint | http://localhost:11434 | http://localhost:11434 | http://192.168.0.200:11434 |
| Proven effective endpoint | UNVERIFIED | UNVERIFIED | Approved pin; current host identity/reachability not probed |
| Model name | gemma3:4b configured; digest UNVERIFIED | gemma3:4b input1; qwen3-nothink inputs2–4 conditional respond; both digests UNVERIFIED | hermes-candidate-granite41-30b-q3km-64k |
| Profile/version | Proposed jarvis.p7.legacy.intent.gemma3.v1; unqualified | Proposed jarvis.p7.legacy.response.gemma3.v1 / jarvis.p7.legacy.response.qwen3-nothink.v1; unqualified | jarvis.p7.ollama.granite41.b1r2.v1, frozen |
| Context tokens | Propose4096; source router explicitly sends4096 | Propose4096 /32768. YAML names those contexts; original main client does not actually send num_ctx, so effective inherited limit UNVERIFIED |64000 frozen |
| Output tokens | Propose64, matches original classifier payload | Propose80 /150, matches conditional ComplexityRouter choices |128 frozen |
| Native response bytes | Propose16384 | Propose16384 each |16384 frozen |
| Serialized request bytes | Propose16384 | Propose16384 each |16384 frozen contract |
| Whole operation deadline | Propose20s; original router HTTP timeout20s is not proven whole-operation limit | Propose180s each, explicitly tighter than original600s/retries |180s frozen |
| Stream/think | Propose false/false | Propose false/false |false/false frozen |
| Retry/fallback |0 /none |0 /none |0 /none |
| Keep-alive | Propose60s, NEW approval; original router omitted value | Propose60s each, NEW approval; original client omitted value |60s frozen |
| Ownership | Exact endpoint/model/profile + shared endpoint lifecycle exclusion | Each operation leases selected exact model; same endpoint exclusion even if different model | Existing Granite identity only, never a legacy lease |
| Possible-send | Durable named intent before transport; no terminal inferred from cancel/timeout | Same, no refund or next conflicting step | Same frozen conservative uncertainty |
| Terminal evidence | Exact operation/resource/request association + transport proof + bounded complete native response; parser alone insufficient | Same plus independent generated/delivered facts | Canonical normalization/evaluation, D04 receipt join and coordinated checkpoint |
| Logging | No raw input/native text/headers/signatures/credentials; fixed codes and bounded IDs/hashes | Same; actual local delivery status separately recorded | Minimized canonical observation and join; no client/history text |

Rationale: preserve configured contexts and per-role output selections where source makes them explicit; retain existing router20s policy as a proposed whole-operation bound; cap legacy response duration at180s for a bounded sequential pilot; 16KiB byte caps and60s residency simplify conservative ownership but are **new legacy decisions**, not inherited Granite approval. Token-context truncation policy and exact prompt/memory request-size fit must be approved/tested; reject oversize, never silently truncate experimental inputs.

The current adapter always emits the same generic payload options; original router temperature0.1 and four-field classifier schema are not reproduced. Approve exact native options and parser profile, prompt bytes/hash, response cleaning, confidence threshold and memory policy before adapter changes become release bindings. Generic `qualification` strings in StepContract are labels, not signed qualification receipts.

To resolve effective values, authorize a reviewed nonsecret attestation exposing only resolved endpoint/model/immutable digest/profile and source binding from the protected runtime, or a human-attested source-bound manifest. Do not dump environment variables. Confirm hostname/IP alias equivalence and whether each legacy endpoint shares Ollama/GPU with Granite. Unknown topology cannot justify concurrent scheduling. Renew local-only backup host-loss acceptance explicitly for V3.
'''
docs['PROVIDER-OWNERSHIP-REVIEW.md']='''# Provider ownership and D06 coexistence

**Not ready for live D06/legacy coexistence.** Candidate schema5's `steps` and `leases` are an isolated extension prototype, not production ModelOwnershipCoordinatorV1. Each step stores attempt, named kind, endpoint, model, profile, request digest and possible-send/terminal/unknown. Lease associates that exact step and endpoint. Global clean() conservatively serializes even distinct endpoints; unique endpoint_exclusion also blocks ACTIVE/REMOTE_UNKNOWN conflicts.

One accepted conversation can own multiple provider transmissions. Existing L1 fixture:12 operations across4 attempts; L2:8 across4. D09 observation submissions/receipts are not all provider calls. Reproduced tests show peak concurrent provider count1; router failure prevents responder/Granite, responder failure prevents Granite, and uncertainty prevents any later model on the endpoint. No automatic retry, fallback, load/unload helper or executor capability exists in this package.

Gate6D restricts begin() to LEGACY_ROUTER, LEGACY_RESPONDER and GRANITE on an unsettled accepted attempt and enforces their order. Exact canonical Granite endpoint/model/profile and limits are now checked before possible-send in the real passive observer bridge. Fixture resources are deliberately documentation-only IP192.0.2.1 and fake profiles; no Granite lease is silently reused for a real gemma/qwen model.

The possible-send row commits before invoking the provider coroutine. It is conservative intent evidence, not packet proof. known_terminal currently trusts an injected ProviderResult; only an associated trusted transport may supply that fact in a release. Cancellation/timeout/late success does not resolve uncertain remote ownership. The stored ACTIVE state after a process exit continues to block clean(), even when the process is gone. Known terminal followed by parse/proposal failure stays known terminal while closing admissions.

Proposed resource extension `G6D-D06-2`:

| Contract element | Required versioned behavior |
|---|---|
| Scope | Fixed approved resource allowlist: legacy router gemma, legacy trivial responder gemma, legacy normal responder qwen, frozen Granite; profiles remain distinct even when model is the same |
| Exclusion identity | Canonical endpoint-wide lifecycle domain, plus model/profile generation identity; canonicalize hostname/IP aliases only from approved topology evidence |
| Durable operations | accepted attempt → named substep → exact resource lease → possible-send → authoritative terminal or unresolved unknown; no helper bypass |
| Legacy D06 compatibility | Validate V2 scope/marker/state unchanged through separate archive reader. No second coordinator root that ignores the first, no broad ownership-check weakening |
| Migration | Separately approved zero-use V2 retirement, quiescent transfer, protected active-root publication and independent old/new exclusion verification |
| External actors | Ollama supervisor/restart, other clients, schedules and privileged lifecycle callers require explicit endpoint reservation; local ledger cannot exclude them |

The fixture schema5 is a versioned prototype for these step/lease associations; Gate6D tests extend its operation whitelist, ordering, unknown exclusion and validation. It lacks a root-protected global D06 resource manifest, actual coordinator adapter, native transport proof and independent actor fence. These remain new implementation and approval requirements. No production D06 storage or ownership state was modified.
'''
docs['GLOBAL-LEDGER-DURABILITY.md']='''# Global ledger and filesystem durability

Logical cap/permit behavior is isolated-tested; protected lineage and actual filesystem durability are not release-qualified. Store uses SQLite schema5, FULL synchronous, DELETE journal, BEGIN IMMEDIATE, a lifetime flock writer and shared reentrant lock. Permit consumption and accepted LIVE/ineligible row commit together. Ordinals1–4 and REST/REST/WS/WS remain permanent across failures. Gate6D adds logical validation of contiguous ordinals, transport, spent-permit/acceptance association, step states and corresponding leases.

| Adversarial case | Observed result / limit |
|---|---|
| Same-parent duplicate successor; concurrent creators | O_EXCL reservation admits only one; competing name refused |
| Crash reservation/before initializer commit/after initializer commit | Reservation remains; replacement successor refused. No automated resume/repair |
| Partial reservation write | Partial artifact retained; second creation refused |
| Missing/corrupt actual predecessor archive | **UNIMPLEMENTED verifier**: current caller-supplied nonempty archive string is trusted. This is a high release blocker, not a passed archive test |
| Nonzero/unknown/incomplete/abort predecessor fields | Refused; now boolean/float count cannot masquerade as integer0 |
| Separate parent/root masking predecessor | **Not prevented globally** without protected root authority. Same-UID directories are not global lineage enforcement |
| Crash before acceptance commit | Rollback preserves zero accepted/spent |
| Crash after acceptance commit before send/ack | Accepted1/spent1 remains, even when no provider was invoked |
| Process exit at possible-send | Accepted1 and unresolved ACTIVE lease persist; no inferred completion |
| Process exit after known-terminal association | Accepted1 persists; remaining incomplete attempt prevents readiness |
| Duplicate REST/WS, cross-transport replay, invalid ordinal | Refused, no refund/additional provider call; matching authentic continuation alone grants nothing |
| Fifth attempt/restart existing accepted set | Cap enforced; restart is recovery hold, not automatic opening; old sessions/permits do not authorize Runtime.request |
| Terminal abort/stop then reopen | Refused. Signed stop audit and terminal state are now one transaction |
| Older backup | verify_checkpoint rejects when supplied newer event high-water; no restore writer exists. Independent monotonic high-water authority across arbitrary DB replacement is missing |

Five new child processes per run exited through os._exit at distinct acceptance/provider boundaries. Initial focused/full tests used tmpfs; all149 focused tests then passed again on Core root ext4 in exclusive disposable `/home/jarvis/gate6d-fs-test-vRWRQNW1`, outside production namespaces. They were not mocked exceptions. This proves process-exit behavior on both tmpfs and the actual Core ext4 filesystem using isolated files; it does not prove abrupt power-loss/disk-controller behavior. Other fixture fault tests inject before/after commit, short writes and backup interruptions. Canonical full suite additionally used its two pidfd-verified disposable writer crashes.

Backup protocol: private UUID directory and parent fsync; SQLite backup; file fsync; exclusively created receipt/lineage files; manifest written last and fsynced; directory fsync; full verifier; only then checkpoint association in live ledger. Publication is manifest-last, not a cross-file atomic rename/transaction. Interrupted directories remain distinguishable and unready. No separate candidate checksum sidecar exists: component digests are in the manifest; the external evidence SHA256SUMS is separately sealed. Partial manifest and missing manifest refuse. Final evidence creation is not a runtime backup writer.

Gate6D moved quiescence validation inside the writer lock, rejects static symlink ancestors/source receipt symlinks, and rejects missing joined receipts in forensic backups even when checksums are rewritten. Unjoined trailing/partial receipt bytes may be retained under FORENSIC_INCOMPLETE, never READY. Source and receipt snapshots share the writer lock; unknown ownership and unsettled attempts block READY. Arbitrary same-UID mutation/rename races are outside current protected-path enforcement.

No restore API writes over occupied state; existing/partial controller initialization refuses and original reservations persist. That is refusal, not a qualified restoration protocol. A caller can still replace older files outside these APIs if it owns them. Root-protected high-water/reservation/archive verification must prevent this before deployment.

Actual target filesystem qualification must cover power interruption, disk-full, fsync/rename/parent durability, journal recovery, simultaneous process writers/readers, disk stalls and backup association failure after manifest publication. SQLite assertions and mocked fsync cannot guarantee hardware durability. Synchronous filesystem calls can exceed30s or wedge the event loop; the current drain method does not provide a supervisor-enforced wall-clock guarantee or automatically complete a final terminal checkpoint. Keep both as explicit release blockers.
'''
docs['DELIVERY-AND-D04-ASSOCIATION.md']='''# Delivery and audit truth

| Fact | Candidate evidence | Does not prove |
|---|---|---|
| Attempt accepted | Durable attempt + spent permit in one transaction | Any provider transmission |
| Router/responder may have sent | Named POSSIBLE_SEND step + lease before coroutine | Bytes actually sent; a transport adapter must supply known-transmitted evidence |
| Native response produced | Associated ProviderResult and bounded parser return | Delivery to client or actual remote completion without trusted adapter proof |
| Legacy delivered locally | Delivery coroutine returned literal True after ASGI send completion; durable LOCAL_SEND_COMPLETED | Remote TCP acknowledgement, browser rendering or human receipt |
| Granite may have sent | Separate GRANITE operation/resource lease | A second pilot attempt or a legacy delivery |
| Granite terminal/observed | Trusted associated terminal result + canonical normalize/evaluate projection | Canonical production sink interoperability |
| D04-like receipt committed | Minimized append/fsync, sequence/hash and SQLite join | Real production D04 API submission; fixture join is a prototype |
| Coordinated checkpoint | Verified manifest3 members and association recorded | Power-loss guarantee or absence of external D06 actors |
| Next permit eligible | Current checkpoint, settled attempt, clean ownership, nonterminal runtime and fresh human action | Automatic authorization |

A generated response is never treated as delivered. Gate6D preserves completed send when stop races with it, and late send completion after cancellation may advance INTERRUPTED_UNKNOWN to LOCAL_SEND_COMPLETED. It records truthful late evidence without another provider request, next permit or terminal-state reopening. Persistence failures set a closed hold and suppress raw callback exceptions. Actual late completion after shutdown/DB closure still requires supervised writer lifetime and final checkpoint integration.

Granite failure after legacy delivery leaves the legacy response and in-memory delivered assistant history intact. Granite text never appears in client envelopes or continuation history. Only completed legacy delivery appends assistant text; user history is captured at acceptance and the observer receives pre-turn bounded history. No raw replies or provider exceptions are retained in new review evidence; synthetic test placeholders are clearly fixtures.

Receipt append precedes SQLite join, so a crash may leave an orphan. It is retained and prevents READY. Missing durable-joined lines can no longer pass a forensic verification through zip truncation. A forensic snapshot may preserve extra partial/orphan data but is never next-permit authority. The prototype has no explicit production D04 submission-intent/receipt resolution adapter; operational association remains a release blocker.

Current stop/cap closure occurs after the last ordinary attempt checkpoint and does not itself create a final post-terminal backup. A final stopped/drained checkpoint and handling of late facts must be integrated before release. No existing production store was used as a mutable test fixture.
'''
docs['INTEGRATION-MATURITY-MATRIX.md']='''# Integration maturity

Classification is for the candidate interface, not for the unchanged live V2 service.

| Interface | Classification | Evidence / remaining work |
|---|---|---|
| Strict JSON, authority schema and signed-body verification seam | IMPLEMENTED AND ISOLATED-TESTED | Dummy HMAC verifier and typed peer only; no production signer |
| Four-attempt ledger and one-parent successor reservation | IMPLEMENTED AND ISOLATED-TESTED | Transactions, crash/race/replay cases pass; protected global authority still missing |
| REST ASGI adapter/envelope | IMPLEMENTED AND ISOLATED-TESTED | Direct in-process ASGI calls; not mounted in FastAPI |
| WS ASGI adapter/envelope/continuation | IMPLEMENTED AND ISOLATED-TESTED | Malformed/control/binary/auth tested; actual origin middleware and disconnect receiver missing |
| API authentication integration | PROTOTYPED ONLY | Candidate injected bytes; no private loader or canonical app middleware connection |
| Legacy L1/L2 response adapter | PROTOTYPED ONLY | Fake providers; single responder differs from legacy complexity path |
| Canonical Granite capture/normalizer/evaluator | IMPLEMENTED AND ISOLATED-TESTED | Exact resource/frozen limits + request body verified; canonical passive projection tested |
| Real bounded native provider transport | DESIGNED BUT NOT IMPLEMENTED | Need response-size enforcement while reading, exact terminal/send proof, no redirects/retries/discovery |
| D06 durable ownership | PROTOTYPED ONLY | Isolated schema5 steps/leases; no production coordinator/exclusion/migration adapter |
| D04/D09 operational event association | PROTOTYPED ONLY | Minimized local receipt append/join; not production sink/controller API |
| Backup writer | IMPLEMENTED AND ISOLATED-TESTED | Fixture manifest3/checkpoint/forensic validation; target filesystem/ownership/restore integration missing |
| Stop/drain | PROTOTYPED ONLY | Local cancellation bounded around await; synchronous I/O and final checkpoint/supervisor incomplete |
| Production startup/routing/factory | DESIGNED BUT NOT IMPLEMENTED | Factory deliberately refuses; new source-consumer graph must be reviewed |
| Operator control transport, kernel peers, signer | DESIGNED BUT NOT IMPLEMENTED | No Unix listener/helper/credential mechanism installed |
| Protected global predecessor validator and reservation publication | DESIGNED BUT NOT IMPLEMENTED | Strings/local reservation cannot attest V2 closure or global uniqueness |
| Dedicated identity, credentials, protected unit/release | REQUIRES NEW APPROVAL | Real users/units/permissions were not created; actual separate-UID tests pending |
| Provider/router/prompt/memory contract | REQUIRES NEW APPROVAL | G6D-LP-1 proposal; no defaults inferred |
| V2 retirement / V3 install / renewed Gate5 / pilot | REQUIRES NEW APPROVAL | Distinct authorities; no operational actions |

Canonical source/fixture separation is preserved: candidate_v3 is standalone; all canonical app and original test bytes unchanged. The full suite proves the isolated copy against its baseline configuration plus explicit pilot fixtures. It does not certify live adapter mounting, operating-system separation or the new release graph.
'''
docs['OS-PRIVILEGE-GAPS.md']='''# Operator authority: workflow, OS, cryptography and durability

| Question | Current evidence and required release answer |
|---|---|
| What prevents Codex producing a valid production permit? | Current V2 has no opening interface; candidate factory refuses. Candidate dummy verifier/peer injection cannot distinguish Codex from a human. Future external user-presence signer and protected service/helper required |
| Can normal jarvis open admissions? | Not in unchanged V2. In an isolated runtime the same UID can supply verifier/peer values or replace code/state; filesystem0700 is not human separation |
| Service privileges | Proposed dedicated non-login unprivileged UID; read protected release/public verification material and private runtime API credential; write only enumerated V3 data/receipt/checkpoint roots; no sudo, root signing key, unit management or lineage-root rewrite |
| Human privileges | Independently authenticated operator action through fixed protected helper, hardware-backed user-presence key or equally approved boundary; provisioning/retirement needs separately authorized administration |
| Replay | Persisted unique control nonces and permits, exact request/session/transport binding and short expiry; opening state refuses repetition. Same-UID DB rollback remains unprotected without independent high-water authority |
| Substitute epoch/PID/runtime | Exact fixture Bindings equality tested for every field. No fresh kernel PID/start/boot/invocation attestation or helper service-peer verification implemented |
| Malformed permit | Strict canonical JSON, finite values, bounded signature, exact payload keys; typed peer parser hardened. Store acceptance remains atomic; malformed request never partly consumes permit |
| Survive restart | Durable spend remains; Runtime starts recovery hold/terminal, sessions not restored. An old unspent permit cannot open the new Runtime. No approved resume path |
| Restart opens admissions? | No. Live V2 rejects epoch reuse; candidate never derives opening permission from stored audit |
| Helper arbitrary command/file abuse | No real helper exists. Proposed schema accepts no paths/URLs/commands. Future helper must use fixed manifests/dirfds and no shell/dynamic module/user path; cannot claim it reviewed before implementation |

Recommended operator action binds exact manifest hash including all source/config/unit/dependency/provider/profile/lineage/Gate5 evidence, action, expected accepted ordinal/high-water, exact kernel/runtime identity, challenge and expiry. Current Bindings covers only selected strings; named resources, unit/dependency inventory, lineage authority, expected ordinal and renewed Gate5 are not independently authenticated by that object. A signed arbitrary label is not a verified deployment.

Workflow restrictions, Unix privilege separation, cryptographic attribution and durable anti-replay are separate properties. Do not replace one with another. Root/kernel/hypervisor and protected interpreter/dependencies remain trusted. No OS users, sudo policy, root services, real keys or credential files were created. Actual separate-UID adversarial testing, protected parent/dirfd TOCTOU testing, credential loader tests with dummy files and supervisor identity tests require an approved disposable privilege environment. Passing current single-UID fixtures supplies none of those claims.
'''
docs['AI-HOST-TRUST-STATUS.md']='''# AI-host identity remains PENDING

No independently trusted current public SSH fingerprint for192.168.0.200 was established. Prior sealed Gate6A/6B trusted inventories and runbooks retain the unresolved status. No new guest login, keyscan, known_hosts write, host-key bypass, Ollama metadata/model call or Proxmox operation occurred. Historical Gate4 Ollama PID3405/restart0 and VM200 facts are historical only.

Human trusted-console comparison, prepared but not executed:

1. Through the operator's authenticated Proxmox management path at192.168.0.50, identify actual VMID200 hosting node. `.50` is not assumed to host the VM. Read-only shell equivalent: `pvesh get /cluster/resources --type vm --output-format json`; inspect the VM200 entry only. On the verified node: `qm config 200`.
2. Open that VM's authenticated console. Run `hostname` and `ip -br address` and verify the guest owns192.168.0.200.
3. In the guest console: `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256`. Record public algorithm/SHA256 fingerprint only. Never read the private host key.
4. Compare against an independently obtained public-key candidate for the intended client/host/port. Any future `ssh-keyscan` is untrusted network evidence until it exactly matches the console fingerprint. Do not append it automatically or change existing pins. Enrollment is separate authority.
5. After trust approval, authorize read-only provider identity/version/model-digest and actor inventory. No generation, warmup, load/unload or restart follows from metadata approval.

Proposed pilot-window exclusivity: inventory endpoint owner, system/user units/timers, cron/scheduled model clients, interactive services, JARVIS wake/unload callers, supervisor restart policy and privileged/hypervisor actors. Obtain a named endpoint reservation covering both generation and model lifecycle, with explicit disposition of any already-possible sends. Unknown topology/actors block opening. Any pause of a job/service, firewall change or restoration requires separate explicit operations authority; none was performed. Local D06 alone cannot fence remote root or other network clients.
'''
docs['IMPROVEMENT-REGISTER.md']=f'''# Gate6D improvement register

All fixes belong only to artifact `{rev}` at `{m['path']}`. Detailed changed-file list and patch are in candidate-manifest.json and evidence. No production source, policy, provider binding or dependency change.

| Problem/risk | Exact change | Verification | Remaining authority |
|---|---|---|---|
| Untyped peer/signature input | authority.py strict tuple/integer checks, signature length and checkpoint hex |7 malformed-peer cases; existing identity/replay cases | Real kernel peer and human signer |
| Exponent overflow | contracts.py finite float JSON parsing | ±1e999 rejected | None for isolated fix |
| ASGI malformed/mixed frames | ingress.py event-type, UTF-8 and more_body validation |7 malformed event cases, existing binary/control tests | Production middleware/disconnect integration |
| Wrong Granite transport/profile/limits | observation.py checks exact frozen resource and all6 limits |9 binding/limit cases plus canonical bridge | Actual transport qualification |
| Split stop record | storage.py stop transaction accepts verified approval; runtime sets stop latch first | Before/after commit crash fault cases | Real operator socket and supervisor |
| Lost local delivery / callback leakage | runtime.py completion callback, failure latch; storage.py monotonic delivery evidence | Immediate stop, late cancellation, persistence failure cases | Final checkpoint/writer lifecycle |
| Arbitrary/new operation on settled attempt | storage.py begin whitelist and ordering/unsettled checks | Arbitrary lifecycle kind and settled-step tests | Real D06 backend |
| Symlink ancestry/read-through | storage.py rejects existing symlink ancestors and source receipt links | Static symlink path and backup source tests | Protected ancestors + TOCTOU under OS separation |
| Semantic ledger corruption | storage.py shared validate_accounting for store/checkpoint | Tampered permit association, existing schema/cap/restart tests | Independent root/high-water authority |
| Forensic missing joined receipt | storage.py enforces len(lines)>=len(joins) | Rechecksummed deletion rejected | Real D04 association |
| Checkpoint race | Quiescence under same writer lock as snapshot | Existing checkpoint tests/full regression and source review | OS concurrent/power-loss qualification |
| Predecessor numeric ambiguity | exact integer0 validation | Boolean/float count cases | Real predecessor archive validator |
| Missing process-failure evidence | Five os._exit fixture children; duplicate reservation race/partial writes | Focused149/full7315 passing | Target filesystem power failure/disk stalls |
| Ambiguous resource recommendation | Pure original-source routing matrix, per-role proposed bindings | Deterministic source assertions | Operator chooses contract, no auto approval |

No historical test weakened or removed. Canonical119 app/208 original tests and94 existing candidate tests unchanged. New adversarial module adds55 cases. Read-only production observers and review generators are documentation/evidence tooling, separate from candidate source.
'''
docs['TEST-RESULTS.md']='''# Exact isolated qualification results

| Run | Result | Interpretation |
|---|---|---|
| security-before |18 failed /2 passed,0.27s | Initial adversarial reproductions. Stop fault hooks were introduced with the fix; their initial failure establishes missing tested transaction boundary, not an injected old crash |
| security-after |114 passed,1.56s | Initial fixes + unchanged94 candidate tests |
| security-expanded |137 passed,2.23s | Added process exits, binding and ledger tests |
| focused-final |**149 passed,0 failed**,2.29s | Final source:94 existing +55 new adversarial cases |
| full-final (invalid global-token fixture) |36 failed /7279 passed /11 deselected,27.79s | Launcher injected DUMMY_GATE6D_ONLY globally, conflicting with historical empty-token baseline. This was a harness invocation error; preserved evidence |
| full-corrected |**7315 passed /11 deselected /0 failed**,2 existing warnings,27.02s | Identical source/tests; removed global env override. Per-test dummy authentication remains. No assertions/exclusions weakened |
| focused-ext4 |**149 passed /0 failed**,17.24s | Exact final source repeated in private disposable directory on Core root ext4; includes all five actual process exits |

Full result equals7166 canonical +149 candidate tests, versus Gate6C7260. Golden remains historical12/20 and the same eight failures; no Golden generation/digest requalification.

Commands (Core, task-private existing environment; no package installs):

```sh
env -i PATH=/usr/bin:/bin \
  HOME=/tmp/jarvis-gate6d-tests-WCbozC3X/home \
  TMPDIR=/tmp/jarvis-gate6d-tests-WCbozC3X \
  P7_OFFLINE_STAGE=/tmp/jarvis-gate6d-tests-WCbozC3X \
  PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  /home/jarvis/JARVIS/.venv/bin/python -B \
  /tmp/jarvis-gate6d-tests-WCbozC3X/supervise_tests.py full-corrected tests
```

Focused command is the same launcher with `JARVIS_API_TOKEN=DUMMY_GATE6D_ONLY` and arguments `focused-final tests/execution/v3_security_test.py tests/execution/v3_candidate_test.py`. Initial full failure used that global dummy override and label full-final. Other focused labels selected the same modules except security-before selected only v3_security_test.py. Launcher adds `-q --capture=sys -p pytest_asyncio.plugin -p offline_fixtures -p no:cacheprovider --basetemp <stage>/fixtures-<label>`. Existing pytest.ini selects `not desktop and not manual and not hardware and not slow and not e2e and not stress and not perf`; same11 exclusions as Gate6C.

Landlock ABI8 denied production/credential file contents and outside writes, allowing only the candidate stage plus read-only interpreter/system dependencies. Seccomp denied INET/PACKET sockets, connect, signals/ptrace/process_vm and other escape operations; existing canaries verify kernel denial. Python audit guard provided counters. No actual provider/model traffic occurred. Full run recorded15 blocked localhost DNS requests from existing error-path tests,17 approved fixture child launches,0 credential/production-content/external-write attempts,0 prohibited execution attempts. Five new os._exit children per crash-test run intentionally cannot emit atexit audit. The ext4 repeat used the same command with stage `/home/jarvis/gate6d-fs-test-vRWRQNW1`, label focused-ext4 and the two focused modules, no global token override;0 blocked DNS/credential/production-content attempts and5 approved children. Two canonical writer-crash children were independently verified and signalled through a narrow pidfd broker; no service signal.

No dependency installation, dependency upgrade or commit was performed, so no precommit package audit was triggered. Dependency security is not newly certified; the two existing deprecations remain. Tests ran against copied committed baseline config; separate entry/exit readbacks bind the deployed SHADOW config and untouched app source. Full test logs, kernel policy, broker output and audit counters are retained in qualification-results. Raw production replies/environments/credentials are absent.
'''
docs['NEXT-OPERATOR-DECISIONS.md']='''# Release decision packet

| Binding | Proven | Proposed / missing | Blocks |
|---|---|---|---|
| Original/revised source | Source hashes, archived original, separated revised artifact and regression | Independent follow-up review of revised patch | Release approval |
| Legacy behavior | Four exact inputs; no direct reply; original rules/model-selection matrix | Operator selects L1 rules-first versus revised L2, exact prompt/memory/cleaner/refusal/serialization contract | V3 deployment + pilot |
| Legacy providers | YAML names and source override mechanism | Nonsecret effective-endpoint/model-digest attestation and G6D-LP-1 budgets/profile decisions | Deployment + pilot |
| Operator authorization | Schema/replay/transaction fixtures | Kernel peers, protected signer/helper, source manifest, actual different UIDs and credential loader | Deployment + pilot |
| Lineage cap | Transactional local cap and one-parent reservation | Protected global root, real V2 archive validator, independent high-water/rollback defense | Deployment + pilot |
| D06/providers | Isolated named serial substeps/unknown hold | Real bounded transport, resource allowlist, endpoint-wide coordinator and lifecycle fencing | Deployment + pilot |
| Delivery/D04 | Local completion/late truth, passive observation, prototype receipt join | Actual ASGI middleware/disconnect/origin, D04/D09 operational adapters, terminal checkpoint | Deployment + pilot |
| Storage | Process-crash/short-write/partial-backup fixture tests | Real target filesystem power-loss/stall/TOCTOU tests; approved restore refusal/migration protocol | Deployment + pilot |
| OS boundary | No real privilege changes; gaps explicit | Approved disposable separate-UID tests, then separately approved actual identity/unit/credential provision | Deployment + pilot |
| AI identity | Prior trust gap verified in sealed inventory | Independent VM200 console public fingerprint; later enrollment and actor inventory/reservation | Live readiness/pilot; current freshness also blocks release readiness |
| V2 state | Unchanged healthy CLOSED zero-use predecessor | Separate retirement after release/identity readiness | V3 installation |
| Gate5 | Complete for unchanged V2 | New CLOSED startup and new positive-only human no-message verification after authorized V3 install | Pilot |

Smallest next decision: review **G6D-LP-1 plus L1 rules-first recommendation**, resolve exact legacy resource/prompt/behavior choices, and authorize only the remaining isolated implementation against that explicit contract. In parallel, the human can supply independently obtained public AI-host fingerprint evidence through the trusted-console procedure. No production change is necessary to make either decision.

Then keep these authorities distinct:

1. Isolated transport/authority/archive/D06/integration implementation and actual disposable OS/filesystem qualification; reviewed final release manifests.
2. Separate production identity/privilege/helper/private credential provisioning approval (no V2 stop implied).
3. Separate evidence-preserving zero-use V2 retirement approval; truthful terminal final checkpoint/archive, no counter rewrite.
4. Separate V3 installation/migration/exactly-one-successor/CLOSED startup approval, no automatic restart/autostart.
5. Separate renewed startup/Gate5 positive-only human auth verification and independent zero-state readback.
6. Separate Gate6 pilot opening/readiness approval, then each one-use supervised permit in approved order, then final stop/drain/Gate7 review.

Do not bundle release source review with retirement, opening or model traffic. The operator's final experimental-contract choice remains pending. Core-local host-loss acceptance must be explicitly renewed for the new layout. Formal measurement, Hermes enablement and P7 exit remain unapproved.
'''
for name,text in docs.items():(R/name).write_text(text)
print('wrote',len(docs),'review documents')
