# Target Component Map — where contract v1 would live in this repository

**Status:** plan only. No file was created. Locations follow existing repo conventions
(`app/<area>/<module>.py`, one responsibility per module, `SAFETY_LEVEL` declared by tools,
pydantic config sections, JSONL audit).

**Naming decision.** The contract's conceptual names are mapped onto a new package
`app/execution/` rather than scattered through `app/brain/`, because these components are
control-plane, not model, concerns — and because a single package makes the trust boundary
reviewable in one place. `app/brain/` keeps model-facing code (prompts, llm_client, router).

---

## 1. Proposed modules

| Component | Proposed location | Responsibility | Inputs | Outputs | Must never |
|---|---|---|---|---|---|
| Execution types | `app/execution/types.py` | the typed vocabulary of the contract (§17 of this plan set) | — | frozen dataclasses | contain behaviour or I/O |
| Request classifier | `app/execution/classifier.py` | deterministic request class + reason (§5.1) | user text, ledger snapshot | `RequestClass` | call a model |
| Action router | `app/execution/router.py` | clause segmentation, primary action, reporting intent, target, multi-action, capability (§5.2) | user text, action lexicon, capability registry | `RouteResult` | produce user-facing prose |
| Canonicalizer | `app/execution/canonicalize.py` | exact, versioned argument normalization (§9.1) | tool name, raw args | `(canonical_args, applied_rules)` | fuzzy-match or guess |
| Permission engine | `app/execution/permissions.py` | action+target → permission class → allow / deny / confirm (§11) | `RouteResult`, tool metadata, policy table | `PermissionDecision` | read model text |
| Confirmation manager | `app/execution/confirmation.py` | pending-confirmation lifecycle and binding (§12) | `PermissionDecision`, session id | `Confirmation` records | execute anything |
| Tool dispatcher boundary | `app/execution/dispatch.py` wrapping `app/tools/registry.py` | the only executor; produces bound `TrustedToolResult` (§18) | `ToolInvocation` | `TrustedToolResult` | be bypassable by importing a tool module |
| Provenance ledger | `app/execution/provenance.py` | trusted operational state with sources and supersession (§9.3, §10) | user facts, tool results, confirmation state | `LedgerSnapshot` | accept model-authored facts |
| Obligation engine | `app/execution/obligations.py` | exactly one obligation per operational turn, frozen priority (§14) | classifier, route, ledger, results, confirmation | `ResponseObligation` | contain per-scenario branches |
| Operational response builder | `app/execution/response.py` | deterministic text per obligation (§15, §16) | `ResponseObligation`, ledger, results | `ApprovedOperationalResponse` | re-extract values or call a model |
| Lane policy | `app/execution/lane.py` | deterministic OPERATIONAL/CONVERSATIONAL decision (§4) | classifier output, route, ledger, events | `Lane` | be influenced by model output |
| Audit pipeline | extend `app/logs/audit.py` + `app/execution/audit_events.py` | the 17 contract fields with correlation ids (§19) | every stage above | JSONL events | store chain-of-thought |
| Hermes adapter | `app/brain/hermes_adapter.py` | build the model request, parse structured proposals as untrusted data (§2.1) | prompt inputs, tool schemas | `ModelDraft`, `ToolProposal[]` | decide anything |
| Integration boundary | `app/execution/pipeline.py` | orchestrates the above for one turn; the only entry the server calls | user message, session | `TurnOutcome` | be entered when the flag is off |
| Feature flag | new `execution:` section in `config.yaml` + `ExecutionConfig` in `app/config.py` | selects legacy vs new path (§19 of this plan set) | config | mode enum | default to anything but legacy |

## 2. Where the existing code is reused as-is

| Existing | Reused for | Change needed |
|---|---|---|
| `app/tools/registry.py` `call()` gate | remains the last-mile safety check | called only through `app/execution/dispatch.py` in the new path; unchanged for legacy |
| `app/logs/audit.py` | audit transport | add event types and fields; no rewrite |
| `app/observability/tracing.py` | correlation ids, spans | reuse `trace_id` as the turn correlation id |
| `app/brain/llm_client.py` | model transport | unchanged |
| `app/brain/prompts.py` | conversational-lane prompt | unchanged for legacy; the new path adds a tool-schema prompt built by the adapter |
| `app/brain/direct_responder.py` | deterministic trivial answers | conceptual precedent for deterministic replies; may be folded into the response builder later |
| `app/config.py` | flag and policy configuration | add `ExecutionConfig`; keep `StrictModel` discipline |
| `evals/` | product regression | unchanged; stays the golden gate |

## 3. Mapping from validated test-only artifacts to production modules

Per contract §7 of the task specification, none of the C3/C4/C5 harness files are copied. The
concept moves; the code does not.

| Validated concept (test-only artifact) | Production module | What actually transfers |
|---|---|---|
| `provenance_lock.py` (operational source lock) | `app/execution/response.py` + `types.py` | the rule that operational output is selected from a named source, and the allowed-source set |
| `lane.py`, `lane-policy.json` | `app/execution/lane.py` | the class→lane table and the additional operational conditions |
| `task13b10c2_classifier.py` | `app/execution/classifier.py` | the nine classes and their priority, re-implemented against production inputs |
| `task13b10c4_action_router.py`, `action-lexicon.json`, `connector-grammar.json` | `app/execution/router.py` + data files under `config/` | clause segmentation rules, clause-initial verb rule, negation and reporting-marker guards |
| `task13b10c_proposal_guard.py` | `app/execution/permissions.py` + `dispatch.py` | the rule that a proposal must match the deterministic route before dispatch |
| `task13b10c_provenance.py` (`Ledger`, `canonicalize`) | `app/execution/provenance.py`, `canonicalize.py` | record shape, source typing, supersession, exact alias canonicalization |
| `task13b10c5_response.py` | `app/execution/obligations.py` + `response.py` | the eleven obligations, the frozen priority, the template families, attribution rules |
| `task13b10a_control_plane.py` (inert dispatcher) | `app/execution/dispatch.py` | the invocation/result shape and the "dispatcher is the only door" property |
| harness per-turn record | `app/execution/audit_events.py` | the 17-field event set |

## 4. Prohibited responsibilities (explicit)

* `app/brain/*` must not decide permissions, confirmation, provenance or final operational text.
* `app/execution/response.py` must not import `llm_client` or any model transport.
* `app/execution/*` must not import `app/voice/*` or UI code; the pipeline returns data, and the
  server renders it.
* No module outside `app/execution/dispatch.py` may call `registry.call` in the new path.
