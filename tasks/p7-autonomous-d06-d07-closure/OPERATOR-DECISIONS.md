# Consolidated remaining decision packet

This file supersedes no prior contract; it consolidates unresolved choices after this session. Provider/model selection itself is now explicit. D03/D04/D05 remain frozen. Questions below are recorded while the operator is away, not permission inferred from silence.

## 1. D06 shared-model ownership and unload coordination
- QUESTION: Which exact owner/in-flight relationship protects the selected Granite candidate while legacy lifecycle runs?
- WHY: Current unload_all_ollama_models targets every loaded model; 13B11A §§11,21 require a separately approved no-conflicting-unload policy.
- OPTION A: Separately authorize an ownership-only contract specifying the exact owned set and an in-flight coordination boundary, followed by reviewed resource-manager implementation.
- OPTION B: Keep measured shadow blocked and preserve current resource behavior.
- RECOMMENDATION: A as contract first; do not change lifecycle during the passive implementation unit.
- BLOCKS: Full D06 freeze, D07 entry and provider activation.
- SECURITY EFFECT: Prevents resource interference, accidental unload and false one-generation isolation claims.

## 2. Ollama inactive-state scope
- QUESTION: Does required inactivity mean no session inference/no runner and zero Core process while retaining the existing AI listener?
- WHY: AI already has ollama serve PID 1370; literal global zero processes cannot be reported.
- OPTION A: Explicitly distinguish idle listener from model runner/session invocation in future acceptance.
- OPTION B: Require global service inactivity through separately authorized operator maintenance; this session does not stop it.
- RECOMMENDATION: A for read-only installed-inventory contracts; neither option authorizes model calls.
- BLOCKS: Literal D06 inactive acceptance wording.
- SECURITY EFFECT: Avoids false safety reports or unauthorized service shutdown.

## 3. D10 context constructor exception — smallest next supervised unit
- QUESTION: Approve exactly shadow_context.py's instance-owned LedgerStore construction in provenance_non_activation_test.py::test_there_are_zero_live_provenance_writes?
- WHY: The current writers==[] assertion rejects the mandatory frozen owner implementation.
- OPTION A: Authorize that single allocation exception and focused owner implementation, retaining every provenance write ban and zero live consumers.
- OPTION B: Leave context and dependent ingress unimplemented.
- RECOMMENDATION: A; freeze executable first-fail corpus before code. No transport/continuation wiring.
- BLOCKS: Passive context, then ingress.
- SECURITY EFFECT: Distinguishes passive state allocation from trusted provenance writes without weakening execution authority.

## 4. D10 observation passive type-import exceptions
- QUESTION: Approve only the exact seven listed gate sites/relationships in Unit C TEST_AUTHORIZATION.md?
- WHY: Frozen D03 consumes PipelineStop/TurnOutcome, BindingProjectionV1, RouteResult and PermissionDecision; current tests prohibit these consumers.
- OPTION A: Version explicit symbol/import budgets and PB04 structural transition, preserving all engine-call bans/public pipeline shape.
- OPTION B: Keep observation implementation blocked.
- RECOMMENDATION: A in a separate focused supervised unit after review; no blanket allowlist.
- BLOCKS: Passive observation implementation.
- SECURITY EFFECT: Prevents hidden evaluation, unauthorized consumers and silent sealed-corpus relaxation.

## 5. D07 bounded scheduling and remote completion
- QUESTION: Which response-independent mechanism, bounded queue capacity, finite timeout and cancellation/drain semantics are approved?
- WHY: Existing async/task primitives do not define shadow lifecycle; local cancellation may leave remote inference running.
- OPTION A: Specify bounded in-process scheduling with explicit lifecycle and one-generation ownership.
- OPTION B: Specify a separate bounded worker model, only after reviewing its additional ownership/storage/infrastructure implications.
- RECOMMENDATION: Compare A/B after D06; do not import legacy 600s/retry policy. Numeric bounds require explicit justification/approval.
- BLOCKS: D07 freeze, evaluator/scheduler and server integration.
- SECURITY EFFECT: Prevents legacy blocking, overload DoS, duplicate attempts and hidden loss.

## 6. D01/D02 session continuation/admission/lifecycle
- QUESTION: What authenticated opaque-handle protocol and retransmission/lifecycle rules apply equally to REST/WS?
- WHY: P1 IDs are not client authority; retry/reconnect cannot infer identity from trace/text.
- OPTION A: JARVIS-validated continuation plus explicit idempotency and bounded owner lifecycle.
- OPTION B: Treat each newly accepted delivery as a new turn with a specified continuation binding and bounded lifecycle.
- RECOMMENDATION: Decide from client semantics before wiring; passive primitives remain independently reviewable.
- BLOCKS: Live session ownership, cross-request identity, attempt accounting and rollback cleanup.
- SECURITY EFFECT: Prevents fixation, cross-session leakage, duplicate work and unbounded retention.

## 7. D05 native wire/prompt and authenticity collector contract
- QUESTION: Which exact JARVIS-owned prompt/history/tool-descriptor sources, native complete-response normalizer and receipt association are approved?
- WHY: Recorded adapter parses text/proposals only; D03/D04 have no authenticity/provider fields.
- OPTION A: Freeze faithful local Ollama wire mapping plus separate minimized controller evidence joined to D04 receipts.
- OPTION B: Retain offline recorded replay only, leaving measured live shadow blocked.
- RECOMMENDATION: A after ownership; preserve sole canonical parser and independent binding/proposal derivation.
- BLOCKS: Authentic live input and measurement eligibility.
- SECURITY EFFECT: Prevents synthetic/replay promotion, model authority and unnecessary raw-content persistence.

## 8. D08 CT-001/CT-013 acceptance
- QUESTION: Which explicit P7 acceptance interpretation resolves CT-001 visibility and retained-draft evidence while preserving CT-013 safety checks?
- WHY: Legacy-visible inert shadow cannot itself satisfy literal control-plane-visible response; raw draft/audit retention is separately constrained.
- OPTION A: Keep literal gates and remain blocked.
- OPTION B: Authorize a P7-scoped candidate/isolation criterion and privacy-safe evidence plan, retaining original CT definitions for later visible-path acceptance.
- RECOMMENDATION: Explicit B review; no reinterpretation before approval.
- BLOCKS: Formal P7/P8 entry.
- SECURITY EFFECT: Prevents false conformance and unauthorized response/audit changes.

## 9. D09 measurement/controller and storage completion
- QUESTION: What controller scope/attempt accounting, backend durability/recovery, live duration/coverage and acceptance thresholds are approved?
- WHY: Sink-only counts cannot prove upstream completeness; current numbers are proposals, not authority.
- OPTION A: Freeze controller/receipt joins and backend implementation plan, then approve window/thresholds from supervised evidence.
- OPTION B: Preserve offline-only evidence and leave live measurement blocked.
- RECOMMENDATION: A in dependency order; no sink implementation this session; known loss remains incomplete under D04.
- BLOCKS: Evidence collection, measured exit, rollout/rollback proof.
- SECURITY EFFECT: Prevents duplicate inflation, silent loss, raw-text expansion and arbitrary threshold claims.

Before future activation, independently prove the existing Core→AI restriction; no new firewall/credential policy is authorized here. Existing F-P7R1-01/F-REPLAY-01/F-AUDIT-01 and real-execution/confirmation/browser blockers remain as listed in LIVE_BINDING_BLOCKERS.md.
