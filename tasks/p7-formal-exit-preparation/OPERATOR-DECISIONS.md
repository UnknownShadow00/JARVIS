# Remaining operator decisions — one packet

No answer is required during this away session. Nothing below is silently approved. Existing permission/confirmation/browser policies, audit-v3 and P8 order remain unchanged.

## D01 — Continuation transport and binding
- QUESTION: How will a JARVIS-issued opaque continuation handle be conveyed and bound to the caller across REST and WS?
- WHY IT IS NEEDED: Neither path currently resolves a session; possession of client-authored IDs cannot grant access to another ledger.
- OPTION A: Specify one shared JARVIS-issued handle protocol with explicit authentication/origin binding and transport representations.
- OPTION B: Keep transport wiring blocked and implement only separately reviewed passive ownership primitives.
- RECOMMENDATION: A before wiring; retain B's passive scope until fully specified. No cookie/header/payload choice inferred.
- WHAT IT BLOCKS: Live context ownership, REST/WS continuation and API/UI changes.
- SECURITY EFFECT: Prevents session fixation, client authority injection and cross-session state disclosure.

## D02 — Admission, retries and bounded lifecycle
- QUESTION: What makes a retransmission the same accepted turn, and what ends/bounds an active conversation?
- WHY IT IS NEEDED: One-turn-per-input is frozen; reconnect, retry identity, capacity, expiry and concurrent admission are not.
- OPTION A: Explicitly treat every newly accepted delivery as a new turn, with bounded owner lifecycle and documented retry behavior.
- OPTION B: Specify a JARVIS-validated idempotency/continuation protocol plus bounded deduplication and session lifecycle.
- RECOMMENDATION: Decide from required client semantics before fixtures; neither text equality nor trace reuse is sufficient. Freeze limits only with resource evidence.
- WHAT IT BLOCKS: Final owner/server integration and overload/rollback tests.
- SECURITY EFFECT: Controls duplicates, memory/DoS and stale/cross-session state without granting execution.

## D03 — Shadow observation producer and record scope
- QUESTION: Should V1 be outcome-only with explicit coverage gaps, or a full stage observation contract supporting formal P7 metrics?
- WHY IT IS NEEDED: TurnOutcome lacks uniform match/permission/zero-call/legacy comparison facts; inventing them would falsify evidence.
- OPTION A: Freeze a narrow outcome record and keep missing formal metrics explicitly blocked.
- OPTION B: First freeze the JARVIS observation producer, field sources and failure coverage, then the complete measurement record.
- RECOMMENDATION: B. C1's separate-record principle is already approved; audit-v3 must remain unchanged.
- WHAT IT BLOCKS: ShadowMeasurementRecordV1 freeze and formal measurement collection.
- SECURITY EFFECT: Prevents operational truth fabrication and treating unobserved execution as zero calls.

## D04 — Measurement retention, clock and failure accounting
- QUESTION: What separate evidence sink, redaction/retention, interval clocks and loss semantics are required?
- WHY IT IS NEEDED: Existing audit-v3 and fixture-only proof do not define production shadow evidence; caller timestamps are not measured latency.
- OPTION A: Approve a bounded separate sink with explicitly sourced facts, drop/error counts and evidence retention.
- OPTION B: Retain offline sealed evidence only and keep formal live measurement blocked.
- RECOMMENDATION: A as a contract after D03; retain all sealed evidence and omit request/model text unless justified.
- WHAT IT BLOCKS: Writer/schema completion, timing metrics and rollback accounting.
- SECURITY EFFECT: Avoids sensitive-content leakage, silent evidence loss and fabricated audit claims.

## D05 — Adapter input and model-free scope
- QUESTION: How will authentic current-turn adapter output be obtained for formal inert shadow?
- WHY IT IS NEEDED: RecordedTurn requires AdapterRequest and canonical recording; no model-absent state exists.
- OPTION A: Separately authorize a live proposal transport/normalizer contract after provider/resource decisions.
- OPTION B: Keep recorded-output replay only and explicitly leave formal live P7 exit blocked.
- OPTION C: Request a new model-absent adapter and phase-acceptance contract; this changes current authority and is not permitted by V1.
- RECOMMENDATION: B for present safety; A for eventual unchanged formal exit. Never manufacture an empty recording.
- WHAT IT BLOCKS: Evaluator input on real traffic and unchanged live-model P7 requirement.
- SECURITY EFFECT: Preserves proposal origin/turn association; no fake model or execution authority.

## D06 — Provider/model and shared resource ownership
- QUESTION: Which established architecture path is authorized, with what exact identity and resource ownership?
- WHY IT IS NEEDED: Historical candidates do not authorize calls; shared-model unload conflicts are a canonical prerequisite.
- OPTION A: Previously measured Hermes/Granite candidate, after separately authorized availability/wire/resource review.
- OPTION B: Existing configured legacy model behind the same untrusted adapter, after schema/quality/resource review.
- RECOMMENDATION: Use historical Granite evidence as the comparison starting point, not a final selection; decide jointly with D05 and in-flight ownership.
- WHAT IT BLOCKS: Any provider/model activation and scored live shadow window.
- SECURITY EFFECT: Prevents unauthorized provider access and interference with legacy model lifecycle.

## D07 — Evaluator scheduling and overload behavior
- QUESTION: Which isolation mechanism meets unchanged legacy behavior with bounded cost and explicit losses?
- WHY IT IS NEEDED: Async server code and the phrase runs in parallel do not freeze task/thread/worker scheduling.
- OPTION A: Specify response-completion-triggered in-process work with bounded admission and cancellation.
- OPTION B: Specify bounded background worker/queue ownership and lifecycle.
- OPTION C: Bounded synchronous pure evaluation, only with explicit latency acceptance and proof.
- RECOMMENDATION: Compare A/B using authorized cost evidence; C directly burdens legacy latency. No infrastructure or scheduler selected now.
- WHAT IT BLOCKS: Evaluator/server implementation, DoS bounds, rollback drain/cancel proof.
- SECURITY EFFECT: Protects response, cancellation, resources and session isolation under load.

## D08 — CT-001 / CT-013 phase acceptance
- QUESTION: How is CT-001's final-user-visible requirement reconciled with required legacy-visible inert shadow, and what integrated CT-013 evidence is accepted?
- WHY IT IS NEEDED: Candidate safety is not the final visible response; CT-013 still needs ordinary safety/leakage coverage.
- OPTION A: Preserve literal CT-001 phase gate and remain blocked until an explicit compatible acceptance plan exists.
- OPTION B: Approve a phase-scoped candidate-isolation criterion for P7 while retaining full visible-path CT-001 later, plus an isolated conversational/safety proof for CT-013.
- RECOMMENDATION: Explicit B decision without editing original CT definitions or switching visible response. Until approved, A remains the status.
- WHAT IT BLOCKS: Formal P7 acceptance and therefore P8 entry.
- SECURITY EFFECT: Prevents false conformance claims and accidental early control-plane rendering.

## D09 — Measured window and thresholds
- QUESTION: What duration, live sample/coverage counts, comparison tolerances and latency limits define the scored period?
- WHY IT IS NEEDED: Canonical exit says measured period; no numbers or traffic-rate evidence define sufficiency.
- OPTION A: Approve duration-plus-coverage criteria after baseline measurements for both transports.
- OPTION B: Remain offline-only and leave measured formal exit incomplete.
- RECOMMENDATION: A later; **RECOMMENDATION — OPERATOR APPROVAL REQUIRED:** retain all 116 frozen + 53 unseen cases as the offline floor, not a live sample claim. No proposed live numbers are frozen.
- WHAT IT BLOCKS: Scored shadow activation and exit verdict.
- SECURITY EFFECT: Preserves zero-side-effect/zero-visible-change hard requirements and avoids misleading denominators.

## D10 — Exact future implementation/test exceptions
- QUESTION: Which narrowly scoped passive implementation and exact non-activation assertion transitions are authorized next?
- WHY IT IS NEEDED: Context construction hits LedgerStore ban; evaluator/server have separate consumer and mode gates; no implementation was authorized in this session.
- OPTION A: Approve one passive owner unit with a named LedgerStore constructor exception and all provenance write bans retained; review later units separately.
- OPTION B: First approve an exact combined context/ingress implementation specification and complete source-derived test budget, still without consumers or activation.
- RECOMMENDATION: A is smaller; use the 26-site inventory as evidence, not blanket permission. Never authorize confirmation/dispatcher/registry or audit-v3 exceptions for inert capture.
- WHAT IT BLOCKS: Production implementation of new modules and all later consumer work.
- SECURITY EFFECT: Preserves execution barriers and makes test weakening reviewable in advance.

This packet covers decisions for remaining P7 shadow work. Existing live-execution-only follow-ups (result authenticity, lost-result recovery, mutation consent/TTL), browser D-01 and external-agent bridge remain deferred; they are not reopened by this session. Voice remains out of scope.
