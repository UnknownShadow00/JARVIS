# JARVIS V2 — Task 13B11A Final Report
## Production integration plan against Agent Execution Contract v1 — planning only

## 1. Verdict

**JARVIS AGENT CONTRACT V1 PRODUCTION INTEGRATION PLAN READY**

Every READY prerequisite is satisfied: the frozen contract verified, the real production code
inspected and mapped, the current execution path traced, 36 contract gaps classified with
evidence, target components defined, permissions/confirmation/provenance/response-lock/audit/
Hermes-seam/rollback planned, twelve phases with entry and exit criteria defined, a dependency
graph with a critical path, a twenty-entry risk register, Task 13C re-scoped, EC-01…EC-14 mapped,
the first implementation task identified, production and Hermes unchanged, evidence sealed, the
planning commit created and the workspace clean.

No inference was run. No production file was opened for writing.

## 2. Task 13B10D verification

Contract commit `5dd853e22c43a84069b44a5dc80ae058ec55996c` present; workspace clean at the start
of planning. Evidence bundle `task13b10d-agent-contract`: **21 files, 20 manifest entries**,
`SHA256SUMS` sha256 `76f6410896485f8c512391482c81b783ea33ea2bf83fc967b43d0d472db126d0` — matches
expected — `sha256sum -c` **20 OK, 0 failures**, manifest excludes itself. All normative artifacts
were read: the canonical contract, the YAML, the conformance tests, the boundary map, the
traceability matrix, ADR-001, known limitations, the failure/security model and the entry criteria.
Nothing in the contract was reinterpreted.

## 3. Production and Hermes baseline

JARVIS `2d7a2ec816500610eafdba4c1a3c0d73f5594c18`, clean tree, no untracked files,
`hermes_enabled: false` (config.yaml line 168), `config.yaml` sha256 `0aef4931…`, `app/` python
tree digest `be1ede5f…`, 83 Python files. Hermes `2237be355906fbe6065ce1815711eee52b2d646e`,
clean. JARVIS was inactive throughout (normal deep-sleep exit at 08:40:11Z); no service was
started or stopped for this task.

Inspection was performed on a workspace copy proven byte-identical for the inspected paths: the
`app/` tree object (`7d6e31f4…`) and the `config.yaml` blob (`1e5d30f0…`) are the same at
`2d7a2ec8` and at the workspace HEAD.

## 4. Current production architecture

Recorded in `CURRENT_ARCHITECTURE_MAP.md` with file and line citations. Summary: entry
`app/main.py` → `app/server.py` (962 lines, 29 routes, bearer-token middleware, loopback binding);
brain layer `app/brain/*` (router, llm_client, prompts, response_cleaner, tool_params,
complexity_router, direct_responder); tool layer `app/tools/registry.py` (273 lines) with 17 tool
modules declaring `SAFETY_LEVEL` 0-2; a second computer-control gate `app/computer/safety.py`;
audit `app/logs/audit.py` (async JSONL, ~130 event types in use) over
`app/observability/tracing.py`; lifecycle `app/resource_manager.py` (835 lines, ACTIVE/
LIGHT_SLEEP/DEEP_SLEEP, global Ollama unload); configuration via pydantic `StrictModel` sections;
**no database** — state lives in `data/*.json`, `logs/audit.jsonl` and `data/traces`.

## 5. Current request-to-execution flow

Traced stage by stage in `call-chain.md`: `chat()` (`app/server.py:358`) → lifecycle gate →
`_process` (598) → `intent_router.classify` (`app/brain/router.py:57`, regex rules then an LLM
fallback) → `build_tool_params` (`app/brain/tool_params.py:33`) → `registry.call`
(`app/tools/registry.py:153`, the real side-effect boundary) → on confirmation-required, an
in-memory pending record (`app/server.py:87, 646`) and an out-of-band Discord/Telegram message →
`build_prompt(message, context=str(result.output)[:1000])` → `llm_client.chat` →
`clean()` → `finalize_reply` (602).

**Trust finding:** on every operational branch except two deterministic exceptions
(`try_direct_reply`, the fixed `confirm_action` sentence) the user-visible text is model prose that
has only been cosmetically cleaned. Tool results enter as a truncated string inside the prompt, and
nothing checks the model's sentence against them.

## 6. Contract gap analysis

`CONTRACT_GAP_ANALYSIS.md` plus machine-readable `gap-matrix.yaml`: 36 requirements classified —
**MISSING 21, PARTIAL 8, MISSING/CONFLICTING 2, PARTIAL/CONFLICTING 2, CONFLICTING 1,
IMPLEMENTED 1, N/A-YET 1.**

The central gap is G-23 (no operational raw-prose lock). Other conflicts worth naming: G-07
(normalization happens inside extraction and the pre-normalization value is lost), G-24 (embedding
tool selection is similarity-based substitution, contrary to §13.2 if enabled), G-36
(`unload_all_ollama_models` unloads models this instance does not own). The genuinely reusable
foundations are the tool gate (`registry.call`), the audit/tracing transport, and the
already-satisfied §19.2 rule that no chain-of-thought is stored (G-27).

## 7. Target component architecture

`TARGET_COMPONENT_MAP.md` proposes a new `app/execution/` package — types, classifier, router,
canonicalizer, lane, permissions, confirmation, dispatch, provenance, obligations, response,
audit_events, pipeline — plus `app/brain/hermes_adapter.py` and an `execution:` config section.
Each component has responsibility, inputs, outputs, dependencies, prohibited responsibilities and
a proposed location. The document also maps each validated C3/C4/C5 concept to its production
home and states explicitly that no harness file is copied.

## 8. Hermes integration seam

Defined in `PRODUCTION_INTEGRATION_PLAN.md` §2 with a thirteen-step turn flow and explicit answers:
JARVIS owns the system prompt, conversation history and tool schemas; proposals arrive as
`ToolProposal` objects with no authority; only `dispatch.invoke` can execute, and only with a
`ToolInvocation` carrying a permission decision and, where required, a confirmation binding; tool
results return to the model only for conversational continuation; Hermes prose is user-visible only
on the conversational lane. Hermes remains disabled, and the model flag is separate from the
control-plane flag so they can be reverted independently.

## 9. Tool-server integration seam

The dispatcher wraps `registry.call` rather than replacing it. All 17 installed tools plus the
computer-control modules are inventoried with their current `SAFETY_LEVEL`, and each is assigned a
proposed permission class. No tool was executed and no classification was changed.

## 10. Permission matrix plan

`PERMISSION_MATRIX_PLAN.md`: seven classes, a per-capability table for everything installed today
plus the not-yet-implemented capabilities (calendar mutation, file delete, messaging, power,
purchase), and the rule that the class is a property of action + target rather than of the module.
Five mismatches with current production policy are declared rather than silently applied:
`apps` close, `kasa` control, `browser_use`, `mcp_client`/`cli`, and the destructive-verb regex
that currently gates prose rather than execution. `approval_mode` is retained as a global
tightening control that may only raise a decision, never lower it.

## 11. Confirmation state-machine plan

`CONFIRMATION_STATE_PLAN.md`: a record with confirmation id, session, action, target, canonical and
raw arguments, permission class, timestamps, state, provenance and audit links; a six-state machine
(`PENDING → EXECUTING → SUCCEEDED|FAILED`, plus `DENIED`, `EXPIRED`, `CANCELLED`) with the
reasoning for dropping a resting `CONFIRMED` state (it invites double execution); a binding rule
requiring id, session, action, target, canonical arguments, `PENDING` state and unexpired freshness
to all match; append-only JSON persistence in the existing `data/` style; and per-class TTLs
(5 minutes normal, 2 minutes destructive/privileged/power).

## 12. Provenance ledger plan

`PROVENANCE_PLAN.md`: record shape with `source_type` *and* a separate `trust_class`
(SUPPLIED/VERIFIED/CONTROL) so the "may I state this as verified?" check is a single field;
supersession that never deletes and never lets a user statement overwrite a tool observation;
in-memory per session with a JSONL audit mirror for v1, with persistence deferred; and an explicit
rule that `app/memory/*` is semantic recall, not provenance.

## 13. Tool invocation / result contract

`TOOL_INVOCATION_CONTRACT.md`: minimum `ToolInvocation` (invocation id, turn/session, action, tool,
raw and canonical arguments, canonicalization version, permission decision, confirmation id,
timestamp) and `ToolResult` (invocation id, status including a distinct `TIMEOUT`, a `facts`
mapping of explicitly returned values, structured `error`, `executed` flag, timings, executor,
audit ref). `facts` is what makes the minimal-result principle enforceable. Only `dispatch.py` may
construct a trusted result, which also removes today's substring test
`_is_confirmation_required_error` (`app/server.py:788`).

## 14. Operational response engine plan

`PRODUCTION_INTEGRATION_PLAN.md` §4: exactly one obligation per operational turn from the eleven
frozen families, the frozen priority with `MISSING_CONTEXT` last, an `ApprovedOperationalResponse`
carrying text plus the provenance record ids that justify every value, audit of obligation and
source, and no model rewrite pass over operational output.

## 15. Raw-prose lock implementation plan

Three independent enforcement points (§5 of the plan): **type level** (`ModelDraft` vs
`ApprovedOperationalResponse`; the render path cannot accept a draft), **pipeline level** (the
operational branch is constructed only by `response.build`), and **audit level** (an operational
turn recording source `MODEL_RAW` is a test failure and a production anomaly). Flag interaction is
specified for all three modes.

## 16. Type and data-model plan

Eight types, each justified by a specific failure mode it prevents, and an explicit list of types
deliberately *not* introduced (per-obligation types, per-permission-class types, a generic
`Trusted[T]` wrapper) because they add ceremony without closing a distinct hole.

## 17. Audit plan

`AUDIT_PLAN.md`: field-by-field mapping of the 17 contract fields against what exists today
(five partial, one implemented, eleven missing), correlation by `trace_id` + `invocation_id` +
`confirmation_id`, a `turn.summary` event for review, fourteen new additive event types alongside
the untouched legacy names, `schema_version: 3` for new events, redaction guidance (store blocked
drafts truncated/hashed, keep message bodies only for external communication, never store
chain-of-thought), and fail-closed treatment for safety-critical events.

## 18. Feature-flag plan

`FEATURE_FLAG_AND_ROLLBACK.md`: one enum `execution.mode` with three values — `legacy` (default),
`shadow`, `control_plane` — plus a separate `hermes_brain` flag. Default is legacy, a malformed
config yields legacy, the flag is read once per turn and carried in context, the new path is
entered from exactly one branch, and every audit event records the mode.

## 19. Shadow-mode plan

The shadow pipeline is constructed with an **inert dispatcher instance** rather than a flag inside
the real one, so execution is unreachable rather than merely not taken; the user always receives
the legacy reply; shadow provenance may never be promoted; comparison metrics are lane/route
agreement, obligation distribution, would-be dispatches and the interesting disagreements where
legacy executed but the new path would have required confirmation; a CPython audit-hook assertion
proves zero side effects.

## 20. Rollback plan

Four levels, fastest first: flag to `legacy`; `hermes_brain` off; revert the feature commits;
restore `config.yaml` from git. Properties that keep level 1 sufficient: the change is additive
until P7, no migration is required, pending confirmations from the new path expire rather than
execute, and rollback never deletes evidence, contract artifacts or models. The plan states plainly
that rollback cannot undo an already-executed real side effect — which is why mutating tools come
last.

## 21. Database and migration impact

**None required for v1.** There is no database today; provenance stays in memory with a JSONL
mirror, confirmations use append-only JSON in the existing `data/` pattern, and audit gains
additive event types. Nothing to migrate, nothing to roll back at the data layer, and the files are
ignored in legacy mode.

## 22. API and UI impact

Minimum additive changes: optional `response_source`, `obligation` and `pending_confirmation`
fields on `ChatResponse`; `GET /confirm/{id}` for status; `POST /confirm/{id}/deny`; WebSocket
confirmation events. No field removed or renamed, so the Electron HUD and PWA keep working
unchanged. No UI implementation is proposed.

## 23. Lifecycle interaction

Answered in the plan §10: confirmations persist as records but never gain authority across sleep
(expired on load, never auto-executed); provenance does not survive a process exit in v1 and the
response layer must then say the detail is unavailable; an in-flight tool call resolves to
`SUCCESS`/`ERROR`/`TIMEOUT` and a timeout is never narrated as success; a mid-turn model unload
ends the turn with a deterministic unavailability response and no retry. No lifecycle behaviour is
modified.

## 24. Shared Ollama and model ownership

The conflict is documented with its code location: `unload_all_ollama_models`
(`app/resource_manager.py:559`) unloads every model loaded in the shared server, which is what
killed the candidate mid-run in Task 13B10C4. Proposed policy: unload only owned models, ownership
declared in configuration (defaulting to today's set so behaviour is unchanged), non-owned models
logged and left alone, and an in-flight-turn gate before unloading the brain. Flagged as requiring
its own approval, not as something integration may do quietly.

## 25. Granite production status

Documented with the C5 evidence: alias `hermes-candidate-granite41-30b-q3km-64k`, 64000 context on
every request, 65/65 GPU layers with `size == size_vram` (31,022,215,331 bytes) and zero CPU
offload, peak VRAM 30,191 MiB of 32,607 MiB, ≤32 GB host RAM compatible, no OOM/Xid/GSP, Ollama
`NRestarts=0` — **and** 92 of 350 operational drafts manually unsafe. Granite is explicitly **not**
declared permanently selected; the model sits behind the adapter as untrusted input and is
selected by its own flag so a swap re-runs quality metrics without reopening the safety design.

## 26. Test strategy

`TEST_STRATEGY.md`: unit → contract (CT-001…CT-018) → inert integration → shadow → read-only live →
confirmation-gated mutation → A/B, with the existing `pytest` suite and
`python -m evals.runner --mode deterministic` as the regression gate at every phase. It carries
over the six methodological rules that made C3/C4/C5 trustworthy (pre-registered expectations,
assert on user-visible output, containment tests need a real unsafe draft, no per-case branches,
abort-and-restart on mid-run change, separate quality from safety metrics), assigns each
conformance test to the phase where it first goes green, and names the three failure modes never
exercised in the diagnostics (timeouts, stale confirmation replay, adversarial injection corpora)
as first-class new tests.

## 27. Implementation phases

`IMPLEMENTATION_PHASES.md`: twelve phases P0-P11, each with deliverable, new modules,
dependencies, tests, entry criteria, exit criteria, rollback point and production impact. Two
orderings deliberately differ from the generic example: audit and types precede provenance, and the
dispatcher boundary precedes the response engine (so the response engine is tested against the real
trusted-result type). Phases P0-P8 have **no** production behaviour change; the first user-visible
effect is P9, read-only.

## 28. First implementation task

**Task 13B11B — execution contract types and feature flag (no behaviour change).** Add
`app/execution/types.py`, `ExecutionConfig` in `app/config.py`, an `execution:` block defaulting to
`mode: legacy`, and tests asserting legacy default, legacy on malformed config, immutable types and
no production reader of the flag. Acceptance: `pytest` green, golden still 12/20 with the same
eight failures, diff limited to three files plus tests, and a single revert restores the tree.
Chosen because it has literally no runtime reachability, is one revert to undo, unblocks the six
pure modules that follow, and forces the trust-boundary type decisions to be reviewed before any
logic depends on them.

## 29. Dependency graph

`DEPENDENCY_GRAPH.md`: full graph, critical path
`config/types → audit → provenance → classifier+router → permissions → confirmation → dispatcher →
obligations+response → pipeline/adapter → conformance`, and a table of which components can be
built and tested independently — eight of the eleven new components are pure functions or pure data
structures with no I/O. Three fan-in points are named for review: the single `_process` branch,
`registry.call`'s two callers, and the shared audit logger.

## 30. Risk register

`RISK_REGISTER.md`: twenty risks R-01…R-20 with severity, trigger, mitigation and the validation
that proves the mitigation — covering raw-prose bypass, execution before permission, confirmation
replay and staleness, wrong-action binding, provenance corruption, canonicalization mismatch,
tool-result spoofing, audit gaps, lifecycle state loss, shared-Ollama unload, flag leakage, legacy
regression, double execution across paths, migration, races, timeout ambiguity, rollback failure,
policy drift and over-templating.

## 31. Idempotency and duplicate execution

Invocation id generated and audited before dispatch; `PENDING → EXECUTING` under a per-record lock
so a second approval is rejected and audited rather than relying on `dict.pop`; no automatic
retries for mutating actions; `TIMEOUT` ends the turn with an explicit "outcome unknown"; an
idempotency key derived from the invocation id is passed to tools that support one. Mandatory
before phase P10.

## 32. Concurrency

Per-session serialization of turns, per-record locking of confirmations, fully independent state
per session, an explicit rule that a correction does not retroactively alter a pending
confirmation's binding, and the lifecycle rule that a transition must not unload the brain during
an in-flight turn. Minimum locking only — nothing global.

## 33. Security review

Six injection paths (user prompt, retrieved memory, web, files, tool output, Hermes output) are
mapped to what they can reach and why none can alter permission policy, confirmation requirements,
trusted provenance or dispatcher authorization, with the five enforcement points named as code
locations. This is contract §21 / INV-020 mapped onto the target architecture.

## 34. Privacy and data retention

Store the minimum; never store chain-of-thought; retain blocked drafts only in truncated/hashed
form and unselected drafts not at all; keep external-communication message bodies deliberately so
the user can audit what was sent in their name; reuse existing rotation until a dedicated retention
policy is agreed.

## 35. Performance

Historical evidence only: the C5 deterministic gate ran at p50 **0.57 ms** and max **2.34 ms**
against a turn p50 of **0.80 s** — three orders of magnitude below the model call. Added
production work per turn (classification, routing, permission lookup, ledger snapshot, ≤11
obligation checks, string rendering, async audit enqueue) is sub-millisecond-class. Per-stage
timing on the turn context, emitted in `turn.summary`, is the proposed instrumentation. No new
benchmark was run or is required.

## 36. Observability

Fifteen metric families defined, including the two that matter most — operational raw exposures
(must be zero) and confirmation outcomes — all derivable from the JSONL event stream the
repository already writes. No external telemetry service is proposed.

## 37. Fail-safe behaviour

Nine component failures are given explicit behaviour (classifier, router, permission store,
confirmation store, dispatcher, provenance, response builder, audit, model), and every one ends in
"no side effect". Audit failure is fail-closed for safety-critical events and degrades for
informational ones.

## 38. Legacy action-tag migration

Today `[ACTION:*]`/`[EMOTION:*]` are taught by the prompt, stripped by `clean()`, and only the
Obsidian tag affects behaviour (plus `[EMOTION:*]` for UE5). Plan: the new path never parses tags
for execution; tags stay untouched while the flag is `legacy`/`shadow`; in `control_plane` mode they
are ignored for execution and stripped for display; retirement from the prompt happens only after
the new path has proven itself, as its own reversible change; `[EMOTION:*]` may outlive
`[ACTION:*]` because it is a presentation hint, not an execution channel.

## 39. Compatibility

Modes are exclusive; shadow uses an inert dispatcher instance; audit event names are additive and
carry the mode; the legacy confirmation dict and the new store never both populate; the only shared
component is the append-only audit logger; and `pytest` plus the golden eval must keep their exact
current results at every phase.

## 40. Task 13C re-scope

`TASK13C_RESCOPE.md` proposes: **integrated conformance of the JARVIS control plane plus Hermes
against contract v1** — CT-001…CT-018 against the real control plane, the A–L families re-run for
*system-safety* metrics, model quality reported separately, plus the three never-exercised failure
modes (timeouts, stale confirmation replay, adversarial injection). Explicitly not a model bake-off,
not a utility-tuning exercise, and not an enablement task. Task 13C was **not** started.

## 41. EC-01…EC-14 roadmap

`PRODUCTION_ENTRY_ROADMAP.md`: five criteria met today (EC-01, EC-02, EC-11, EC-13, EC-14), one
partial (EC-08), eight remaining, each mapped to the phase that satisfies it and the test or task
that validates it. Hermes enablement stays gated on all fourteen, and meeting them authorizes
flag-gated work rather than shipping.

## 42. Production change proof

Production JARVIS is byte-for-byte unchanged: commit `2d7a2ec8…`, clean tree, zero untracked files,
`config.yaml` sha256 `0aef4931…` and `app/` python digest `be1ede5f…` identical before and after the
task. Hermes unchanged at `2237be35…`, clean. No service started or stopped, no unit or config
added, no migration, no database write, no inference, no tool executed.

## 43. Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11a-production-integration-plan/` — authorization,
contract verification, production and Hermes baselines before and after, inspected-file inventory,
call-chain evidence, gap matrix, all plan documents, repository diff and this report.
Bundle: **28 files, 27 manifest entries**, zero self-references, `sha256sum -c` **27 OK,
0 failures**. The manifest's own sha256 is recorded in `tasks/loop-log.md` rather than here,
because a manifest that covers this report cannot also be quoted inside it. The verification
scripts are included under `scripts/` so the baseline and final-state checks can be re-run
independently.

## 44. Planning commit

One workspace commit, `docs: plan JARVIS agent contract v1 integration`, containing only
`tasks/task13b11a/` and `tasks/loop-log.md`. The commit hash is reported in the session output; it
cannot be quoted inside the commit it identifies.

## 45. Recommendation

The plan is ready to execute, one phase at a time, starting with **Task 13B11B** (types + feature
flag, no behaviour change) as a separate approval. Do not enable Hermes; do not start Task 13C
until phases P0-P8 are complete; do not skip to real mutating tools. Each phase should end the way
this one does: verified baseline, sealed evidence, a single reversible commit, and a plain
statement of what is not yet true.
