# JARVIS Agent Execution Contract v1 — Production Integration Plan

**Status:** PLANNING ONLY. No production source, configuration, service, model or database was
changed by the task that produced this document.

**Contract:** `jarvis.agent-execution-contract` v1, FROZEN_FOR_IMPLEMENTATION, workspace commit
`5dd853e22c43a84069b44a5dc80ae058ec55996c`.
**Production baseline:** JARVIS `2d7a2ec816500610eafdba4c1a3c0d73f5594c18` (clean),
Hermes `2237be355906fbe6065ce1815711eee52b2d646e` (clean), `agent.hermes_enabled: false`.

Companion documents: `CURRENT_ARCHITECTURE_MAP.md`, `CONTRACT_GAP_ANALYSIS.md`,
`TARGET_COMPONENT_MAP.md`, `IMPLEMENTATION_PHASES.md`, `DEPENDENCY_GRAPH.md`,
`PERMISSION_MATRIX_PLAN.md`, `CONFIRMATION_STATE_PLAN.md`, `PROVENANCE_PLAN.md`,
`TOOL_INVOCATION_CONTRACT.md`, `AUDIT_PLAN.md`, `FEATURE_FLAG_AND_ROLLBACK.md`,
`TEST_STRATEGY.md`, `RISK_REGISTER.md`, `TASK13C_RESCOPE.md`, `PRODUCTION_ENTRY_ROADMAP.md`.

---

## 1. The shape of the change

Today JARVIS is **model-authoritative**: `_process` (`app/server.py:598`) routes an intent, may
call a tool through a safety gate, then asks the model to write whatever the user sees. Contract
v1 requires a **control-plane-authoritative** system: the control plane decides, executes and
speaks on operational turns, and the model contributes understanding, proposals and conversation.

The migration is therefore **additive, not a refactor**. A new package `app/execution/` is built
alongside the existing path and entered from a single flag-guarded branch. Until phase P7 nothing
in the legacy path changes at all.

## 2. Hermes integration seam

Target flow:

```
user input (HTTP /chat or WS /ws)
  → resource_manager.ensure_awake_for_interaction          (existing, unchanged)
  → execution.pipeline.handle_turn(session, text)          (new, flag-guarded)
      1 provenance.snapshot()                              trusted state for this turn
      2 classifier.classify(text, snapshot)                request class + reason
      3 router.route(text)                                 primary action, reporting intent, target, multi-action, capability
      4 lane.decide(class, route, snapshot, events)        OPERATIONAL | CONVERSATIONAL
      5 hermes_adapter.ask(...)                            → ModelDraft + ToolProposal[]   [UNTRUSTED]
      6 guard: proposal must match the route               mismatch → no dispatch
      7 permissions.decide(action, target, session)        ALLOW | CONFIRM | DENY
      8 confirmation.create/lookup                         binds approval to this exact action
      9 dispatch.invoke(ToolInvocation)                    → TrustedToolResult             [TRUSTED]
     10 provenance.record(...)                             user facts + tool facts
     11 obligations.derive(...)                            exactly one obligation
     12 response.build(obligation, snapshot, result)       ApprovedOperationalResponse
     13 audit: the 17 fields, correlated by trace/invocation/confirmation ids
  → server renders the approved response (or the conversational draft on the conversational lane)
```

Answers to the seam questions:

| Question | Answer |
|---|---|
| Who creates the system prompt? | JARVIS. `app/brain/prompts.py` for the conversational lane; the adapter adds tool schemas for proposal turns. The model never supplies its own instructions. |
| Who owns conversation history? | JARVIS. History is assembled per turn from JARVIS-held state; Hermes is stateless from the control plane's point of view. |
| Who gives Hermes tool schemas? | JARVIS, from the capability registry — the same source the router uses for `CAPABILITY`, so proposal and route cannot disagree about what exists. |
| Who receives structured proposals? | `app/execution/pipeline.py` via the adapter, as `ToolProposal` objects that carry no authority. |
| How are proposals prevented from executing directly? | Only `dispatch.invoke` can execute, and it requires a `ToolInvocation` carrying a `PermissionDecision` (and a `confirmation_id` when required). A proposal is not a `ToolInvocation`. |
| How are tool results returned to Hermes? | Only when a *conversational* continuation needs them, and only as already-trusted facts. Operational answers never round-trip through the model (§15 of the contract forbids a model rewrite pass). |
| When may Hermes produce user-visible prose? | Only on the CONVERSATIONAL lane, subject to the existing cleaning and safety checks. |
| When must final prose come from JARVIS? | Every OPERATIONAL turn, without exception (INV-001). |

Hermes is **not** enabled, installed into production, or configured by this plan. `hermes_enabled`
stays `false`; the new `execution.hermes_brain` flag is what would later select it, and it is
independent of the control-plane flag so the two can be reverted separately.

## 3. Tool-server seam

The dispatcher wraps the existing registry rather than replacing it: `registry.call`
(`app/tools/registry.py:153`) keeps its `SAFETY_LEVEL` gate, dry-run behaviour and audit, and
becomes the last mile behind `app/execution/dispatch.py`. Existing executors and their current
declared levels are inventoried in `CURRENT_ARCHITECTURE_MAP.md` §6, and their proposed permission
classes are in `PERMISSION_MATRIX_PLAN.md` §2 — including five places where the proposed class is
stricter than today's `SAFETY_LEVEL`, listed explicitly as mismatches requiring approval rather
than silent change.

Nothing in this task executed a tool or changed a classification.

## 4. Operational response engine

Per `TOOL_INVOCATION_CONTRACT.md` and contract §14-§16:

* **Input:** request class, route, lane, provenance snapshot, trusted results, confirmation state.
* **Selection:** the frozen eleven-obligation priority, first match wins, `MISSING_CONTEXT` last.
* **Output:** an `ApprovedOperationalResponse` carrying the text, the obligation, the source, and
  the provenance references that justify every value in the text.
* **Provenance attachment:** the response object holds the record ids it used, so an auditor can
  answer "where did this number come from?" without re-deriving anything.
* **Audit:** obligation, source and final text in `response.obligation` / `response.emitted`.
* **No model rewrite pass** over operational output, ever.

Template families mirror the validated C5 set (tool success, tool error, confirmation, ambiguity,
capability, ledger value, declarative acknowledgement, unverified status, multi-action limit,
intent-without-execution, missing context), re-implemented in production style — the harness file
is not copied.

## 5. Raw-prose lock — where it is enforced

Three independent enforcement points, so a single mistake cannot open the boundary:

1. **Type level.** `ModelDraft` and `ApprovedOperationalResponse` are distinct types. The server's
   render path accepts `ApprovedOperationalResponse | ConversationalResponse`; a `ModelDraft`
   cannot be returned from an operational turn because it does not type-check.
2. **Pipeline level.** `pipeline.handle_turn` returns a `TurnOutcome` whose operational branch is
   constructed only by `response.build`. There is no code path from the adapter's output to the
   operational branch.
3. **Audit level.** Every turn records `lane` and `final_response_source`; an operational turn with
   source `MODEL_RAW` is a hard assertion failure in tests and an alert-worthy audit anomaly in
   production.

The feature flag interacts with this deliberately: in `legacy` mode the lock is not in the path at
all (legacy behaviour is unchanged and is *not* claimed to conform); in `shadow` mode the lock runs
but its output is discarded; in `control_plane` mode the lock is the only way text reaches the user
on an operational turn.

## 6. Type and data-model plan

Recommended types — each one exists because it prevents a specific trust mistake, and no others:

| Type | Prevents |
|---|---|
| `ModelDraft` | model prose being mistaken for an answer (R-01) |
| `ToolProposal` | a proposal being mistaken for an authorized invocation (R-02) |
| `ToolInvocation` | dispatch without a permission decision / confirmation binding (R-02, R-05) |
| `TrustedToolResult` | model text being mistaken for a tool result (R-08); constructible only in `dispatch.py` |
| `ProvenanceRecord` | a supplied value being mistaken for a verified one (R-06) |
| `ResponseObligation` | ad-hoc response construction with no named reason (R-01) |
| `ApprovedOperationalResponse` | raw prose reaching the user (R-01) |
| `ConversationalResponse` | conversational text accidentally answering an operational turn |

Deliberately **not** introduced: a type per obligation family, a type per permission class, or a
generic `Trusted[T]` wrapper. They add ceremony without closing a distinct failure mode.

All are frozen dataclasses in `app/execution/types.py` with no behaviour, matching the existing
repo style (`RouterResult`, `ToolResult` are plain classes today).

## 7. Shadow mode

Purpose: compare legacy and new paths on real traffic with zero risk.

* The shadow pipeline is constructed with an **inert dispatcher** — a different object, not a flag
  inside the real one — so "execute" is not reachable, not merely not taken.
* The user always receives the legacy reply; the shadow result is written to audit only.
* No provenance record produced in shadow may be promoted into the live ledger.
* Comparison metrics: lane agreement, route agreement, obligation distribution, would-be dispatch
  count, and disagreement cases where legacy executed but the new path would have asked for
  confirmation (the interesting direction).
* A CPython audit-hook assertion in tests proves the inert dispatcher performs no side effects —
  the same technique that produced the "0 real side effects" evidence in C4/C5.

## 8. Database and migration impact

There is no database in production today (`CURRENT_ARCHITECTURE_MAP.md` §11). The plan keeps it
that way for v1:

| Need | v1 storage | Why |
|---|---|---|
| Provenance | in-memory per session + JSONL audit mirror | matches validated behaviour; no migration |
| Confirmations | append-only JSON under `data/`, same pattern as `data/agent_tasks.json` | survives restart without a schema |
| Audit | existing `logs/audit.jsonl` with additive event types | no format break |

Consequences: no migration to write, nothing to roll back at the data layer, and files that are
simply ignored in `legacy` mode. A real database becomes a question only when multi-device
confirmation or cross-session provenance is required — a later, separately approved step.

## 9. API and UI impact

Minimum additions, chosen to preserve the existing response shape:

* `ChatResponse` (`app/server.py:248`) gains **optional** fields: `response_source`,
  `obligation`, and `pending_confirmation` (id, action, target, expiry). Existing clients ignore
  unknown fields; no field is removed or renamed.
* A `GET /confirm/{id}` (status) alongside the existing `POST /confirm/{id}`, so a UI can show what
  is pending rather than parsing a Discord sentence.
* `POST /confirm/{id}/deny` so refusal is a first-class, audited transition instead of a timeout.
* WebSocket events for `confirmation.required` / `confirmation.resolved`.

No UI implementation is proposed here; the Electron HUD and PWA continue to work unchanged against
the legacy fields.

## 10. Lifecycle interaction

Current behaviour (unchanged by this plan): `ACTIVE → LIGHT_SLEEP` unloads models,
`LIGHT_SLEEP → DEEP_SLEEP` unloads and exits the process
(`app/resource_manager.py:199, 223, 314`).

| Question | Planned answer |
|---|---|
| Should pending confirmations survive deep sleep? | Yes as *records*, no as *authority*: they persist so the user can see what happened, and any record whose `expires_at` has passed becomes `EXPIRED` on load. A pending confirmation is never auto-executed on wake. |
| Should provenance survive deep sleep? | Not in v1. On resume the ledger is empty and the response layer answers "not available in the current context" — which is honest, and better than resurrecting stale state as if it were current. |
| What happens to an in-flight tool call? | It is bounded by the tool timeout and resolves to `SUCCESS`, `ERROR` or `TIMEOUT`. A `TIMEOUT` must never be narrated as success; the turn ends with an explicit uncertainty statement. |
| What if Ollama unloads the brain mid-turn? | The model call fails; the turn ends with a deterministic "not available" operational response. No fabricated continuation, and no retry that could double-execute a tool. |
| What must be persisted before exit? | Confirmation records and audit events. Nothing else is required for correctness in v1. |

No lifecycle timeout, transition or unload behaviour is modified.

## 11. Shared Ollama and model ownership

`unload_all_ollama_models()` (`app/resource_manager.py:559`) unloads **every model currently loaded
in the shared server**, taken from `list_loaded_ollama_models()` plus `configured_ollama_models()`
(502). This is what unloaded the Granite candidate mid-run in Task 13B10C4 and cost a full scored
run.

Proposed ownership policy (planning only; no code change):

1. JARVIS unloads only models it owns — the set in `configured_ollama_models()` — and stops
   unloading models it merely observed as loaded.
2. Ownership is explicit configuration, not discovery: an `ollama.owned_models` list, defaulting to
   today's configured set, so behaviour is unchanged unless someone opts in.
3. Non-owned models are left alone and their presence is logged, so a shared host is diagnosable.
4. If the brain model is owned by JARVIS, unloading it must be gated on "no in-flight turn"; that
   gate belongs with the pipeline, not with the resource manager, which has no turn concept today.

This is a behaviour change to production code and therefore requires its own approval; it is
listed here as a prerequisite for running a shared Ollama with an agent path, not as something the
integration may do quietly.

## 12. Granite production status

| Fact | Value | Source |
|---|---|---|
| Installed candidate | `hermes-candidate-granite41-30b-q3km-64k` (Granite 4.1 30B Q3_K_M) | C5 runtime summary |
| Context proven | 64000 on every request | C5 `runtime-summary.json` |
| GPU residency | 65/65 layers, `size == size_vram` (31,022,215,331 bytes), 0 CPU offload | C5 |
| Peak VRAM | 30,191 MiB of 32,607 MiB; min free 1,919 MiB | C5 |
| Host RAM | fits the ≤32 GB architecture; peak swap 260 MiB | C5 |
| Stability | no OOM, no Xid, no GSP fault, Ollama `NRestarts=0` | C5 |
| Model quality | still imperfect: 92 of 350 operational drafts manually unsafe | C5 manual review |
| System safety with this model | every hard safety metric zero | C5 |

**Granite is not declared permanently selected.** The contract's value is that model replacement
must not change the safety architecture: the model sits behind the adapter as untrusted input, and
`execution.hermes_brain` selects it independently of the control-plane flag. Any future model swap
re-runs model-quality metrics and re-runs the conformance suite, but does not reopen the safety
design.

## 13. Idempotency and duplicate execution

Mandatory before any real mutating tool is enabled (phase P10):

* `invocation_id` is generated **before** dispatch and written to audit before the call, so a
  crash mid-call is detectable.
* Approval transitions `PENDING → EXECUTING` under a per-record lock; a second `/confirm` on a
  record that is not `PENDING` is rejected and audited, replacing today's reliance on `dict.pop`
  (`app/server.py:793`).
* Retries are never automatic for mutating actions. A `TIMEOUT` ends the turn with an explicit
  "outcome unknown" response; only a user-initiated new request can try again, and it gets a new
  confirmation.
* Where a tool can support it, an idempotency key derived from `invocation_id` is passed through,
  so a retried external call is de-duplicated at the far end.

## 14. Concurrency

| Interaction | Rule |
|---|---|
| Two `/chat` turns in one session | serialize per session; the ledger is written by one turn at a time |
| `/chat` and `/confirm` concurrently | confirmation records are locked per record; a turn never mutates another turn's pending record |
| Two sessions | fully independent ledgers and confirmation scopes; no shared mutable state except audit (append-only) |
| Correction during an in-flight action | the correction supersedes the *supplied value*; it does not retroactively change a pending confirmation, whose binding is to the arguments as confirmed — a mismatch is surfaced, not silently applied |
| Tool call and lifecycle transition | see §10: transition must not unload the brain during an in-flight turn |

Minimum locking: one asyncio lock per session for ledger writes, one per confirmation record for
state transitions. Nothing global.

## 15. Security review — injection paths

| Path | Reaches | Why it cannot alter policy |
|---|---|---|
| User prompt | classifier, router, adapter | classification is deterministic; authority claims in text are not parsed as authority; permission comes from the action table, not the text |
| Retrieved memory (`app/memory/*`) | prompt context | memory content is untrusted content; it never writes the ledger and never creates confirmation |
| Web content (`web_search`, `browser`) | prompt context, tool output | tool *output* is data; only `facts` from a `TrustedToolResult` may be stated, and output text cannot change a permission decision |
| File content (`files`, `obsidian`) | prompt context | same as above; path scope is enforced by the tool and the permission class |
| Tool output text | prompt context, response construction | the response builder reads `facts`, not free text |
| Hermes output | proposals, conversational prose | a proposal is not an invocation; operational prose is never emitted |

Enforcement points: the guard (proposal vs route), the permission engine (action table, not text),
the confirmation binding (identity, not phrasing), the dispatcher (only constructor of trusted
results), and the response builder (only trusted values). This is contract §21 and INV-020 mapped
onto code locations.

## 16. Privacy and data retention

* Audit already avoids chain-of-thought, and the plan keeps that prohibition explicit.
* Store the minimum: provenance records hold a fact key and a small value, not the whole
  conversation; confirmations hold arguments, not free text.
* Blocked model drafts may be retained in truncated/hashed form for safety review; unselected
  drafts are not retained.
* Message bodies for `EXTERNAL_COMMUNICATION` actions are retained deliberately, so the user can
  audit what was sent in their name.
* Retention piggybacks on existing rotation (`settings.logging.max_log_size_mb`, 3 backups) until a
  dedicated policy is agreed.

## 17. Performance

Historical evidence only, from the C5 run: deterministic gate p50 **0.57 ms**, max **2.34 ms**,
against a turn p50 of **0.80 s** and p95 of **1.46 s** — the control plane was roughly three
orders of magnitude cheaper than the model call.

Expected additions per turn in production: classification and routing (regex over one message),
permission lookup (table), ledger snapshot (small dict), obligation selection (≤11 checks),
response rendering (string build), audit (async enqueue). All are sub-millisecond-class except
audit I/O, which is already asynchronous.

Instrumentation to add with the implementation: per-stage timing on the turn context, emitted in
`turn.summary`, so regressions are visible without a benchmark harness. No new benchmark run is
required by this plan.

## 18. Observability

Metrics to emit from `turn.summary` and the event stream: operational vs conversational turns;
tool proposals; guard blocks; permission denials; confirmations requested / confirmed / denied /
expired; tool successes and errors; unsafe operational drafts detected in shadow; operational raw
exposures (**must be zero**); provenance misses; obligation distribution; missing-context count;
audit failures; duplicate-execution preventions; per-stage latency.

No external telemetry service is proposed: the repository already writes JSONL traces
(`app/observability/tracing.py`) and the existing evals/report tooling can read them.

## 19. Fail-safe behaviour

| Component fails | Behaviour |
|---|---|
| Classifier raises | no execution; conversational lane is not assumed; respond with a missing-context operational answer and audit the failure |
| Router raises | no execution; ask for clarification |
| Permission engine unavailable | **deny**; no execution |
| Confirmation store unavailable | no execution for anything requiring confirmation |
| Dispatcher unavailable | no execution; capability-unavailable response |
| Provenance unavailable | do not assert any operational state; missing-context response |
| Response builder raises | a single fixed safe operational sentence, sourced as a control-plane fallback, never model prose |
| Audit unavailable | safety-critical events fail closed (no dispatch); informational events degrade |
| Model unavailable | conversational lane degrades to a deterministic apology; operational turns are unaffected where they need no model |

Every one of these ends in "no side effect", which is the only acceptable default.

## 20. Legacy action tags

Today the model is told to emit `[ACTION:*]`/`[EMOTION:*]` (`app/brain/prompts.py:30-50`), and
`clean()` strips them before display (`app/brain/response_cleaner.py:36`). Only `[ACTION:OBSIDIAN:…]`
affects behaviour, via a router rule (`app/brain/router.py:170`) and `_extract_note_target`
(`app/brain/tool_params.py:133`); `[EMOTION:*]` is read for UE5 (`app/comms/ue5_bridge.py:69`).

Migration plan:

1. The new path **never** parses action tags for execution; structured proposals are the only
   execution input (contract §18.1).
2. Legacy tags stay exactly as they are while the flag is `legacy` or `shadow` — no removal, no
   prompt change.
3. In `control_plane` mode, tags found in a model draft are ignored for execution and stripped for
   display, as today.
4. Retirement of the tag vocabulary from the prompt happens only after the control-plane path has
   proven itself in production for a period, and is its own small, reversible change.
5. `[EMOTION:*]` may outlive `[ACTION:*]`: it is a presentation hint, not an execution channel.

## 21. Compatibility — both paths coexisting

* **No double execution:** modes are exclusive; shadow uses an inert dispatcher instance.
* **No duplicated audit:** every event carries the mode; legacy event names are untouched and new
  names are additive.
* **No conflicting model unload:** the ownership policy (§11) is a prerequisite for running both.
* **No conflicting confirmation:** the legacy dict and the new store are separate; in `legacy` mode
  nothing reads the new store, and in `control_plane` mode `_process` is not entered, so the
  legacy dict is never populated.
* **No shared mutable state:** the only shared component is the audit logger, which is append-only.
* **Legacy stays the fallback:** `pytest` and `python -m evals.runner --mode deterministic` must
  keep producing 12/20 with the same eight failures at every phase.

## 22. First implementation task

Proposed: **Task 13B11B — execution contract types and feature flag (no behaviour change)**.

* Add `app/execution/types.py` with the frozen dataclasses from §6, no behaviour.
* Add `ExecutionConfig` to `app/config.py` and an `execution:` block to `config.yaml` defaulting to
  `mode: legacy`, plus `config.yaml.example`.
* Add `tests/execution/types_test.py` and `tests/execution/config_test.py` asserting: the default
  mode is legacy; a missing or malformed section still yields legacy; types are immutable; and no
  production code path reads the flag yet.
* Acceptance: `pytest` green, `python -m evals.runner --mode deterministic` still 12/20 with the
  same eight failures, `git diff` touches only the three files plus tests, and reverting the commit
  restores the tree exactly.

Why this one: it is the only phase with literally no runtime reachability (nothing reads the flag,
nothing constructs the types), it is a single revert to undo, and it unblocks P1-P6 which are all
pure modules that need the vocabulary. It also forces the trust-boundary type decisions to be made
and reviewed before any logic depends on them.

## 23. What this plan explicitly does not authorize

Implementing any phase; enabling Hermes; adding tools or MCP servers; changing a `SAFETY_LEVEL`;
changing lifecycle or unload behaviour; changing model assignments; touching the AI VM; starting
Task 13C.
