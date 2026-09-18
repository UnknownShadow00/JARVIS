# Contract Gap Analysis — Agent Execution Contract v1 vs production `2d7a2ec8`

**Legend:** IMPLEMENTED · PARTIAL · MISSING · CONFLICTING · N/A-YET (contract clause applies only
once a later capability exists).

Every row cites the production code that establishes the verdict. "Contract" cites
`JARVIS_AGENT_EXECUTION_CONTRACT.md` v1.

| # | Contract requirement | Clause | Status | Evidence / reason |
|---|---|---|---|---|
| G-01 | Deterministic request classification into the nine classes | §5.1 | **MISSING** | `app/brain/router.py` classifies six *intents* (`_VALID_INTENTS`, 32) partly by LLM (`_classify_with_ollama`, 89). No `VALUE_QUERY`/`DECLARATIVE_FACT`/`MISSING_CONTEXT_QUERY` concept, and classification is not fully deterministic. |
| G-02 | Operational vs conversational lane split | §4 | **MISSING** | No lane concept anywhere in `app/`. Every branch of `_process` (598) ends in model prose. |
| G-03 | Primary action routing | §5.2 | **PARTIAL/CONFLICTING** | Router emits `suggested_tool`, not a primary action; deterministic rules (163) map verbs straight to tools or to `confirm_action`. A compound request is never segmented, so the C3 failure mode (reporting clause displaces the action) is structurally present. |
| G-04 | Reporting intent as non-executable metadata | §7 | **MISSING** | No representation. |
| G-05 | Target extraction with resolution state | §5.2 | **PARTIAL** | `build_tool_params` (`app/brain/tool_params.py:33`) extracts app names/paths/queries by regex but has no notion of "unresolved"; `extract_app_name` (26) returns whatever remains after stripping verbs, so "open it" yields the literal target `it`. |
| G-06 | Multi-action detection and refusal | §8 | **MISSING** | No segmentation; one tool is selected and run. |
| G-07 | Canonical argument normalization, raw retained | §9.1 | **PARTIAL/CONFLICTING** | The only normalization is `"visual studio code" → "vscode"` inside `extract_app_name` (26), i.e. during extraction, and the pre-normalization value is not retained. Audit logs only the final `params` (`registry.call`, 176). |
| G-08 | Permission classes | §11.1 | **MISSING** | Safety is a single integer `SAFETY_LEVEL` 0-3 per module; there is no class taxonomy and no per-action mapping. |
| G-09 | Permission decision before dispatch, not overridable | §11.2 | **PARTIAL** | `registry.call` (153) does gate before `module.execute` and blocks level ≥ 3 — a real deny-before-dispatch. But the decision derives from a module-level constant, not from action + target + policy, and `approval_mode` can move the whole threshold at once (236). |
| G-10 | Confirmation state owned by JARVIS | §12.1 | **PARTIAL** | `_pending_confirmations` (`app/server.py:87`) is JARVIS-owned and `registry.call(..., confirmed=True)` is the only way to bypass the gate — but the state is an in-memory dict with no lifecycle. |
| G-11 | Confirmation bound to action, target, arguments, session | §12.3 | **MISSING** | The entry stores `{tool, params, trace_id}` (646); no user/session identity, and arguments are not re-validated at approval (792-810). |
| G-12 | Confirmation expiry / freshness | §12.3 | **MISSING** | No `expires_at`, no freshness check. A request id remains valid until the process exits. |
| G-13 | Dispatcher is the sole executor and trust boundary | §18.1 | **PARTIAL** | `registry.call` is the main path, but `app/computer/*` has its own gate (`safety.py:9`) and tools are importable directly (`TOOLS` map, 74), so "sole executor" is a convention rather than a structural property. |
| G-14 | Tool invocation identity | §18.2 | **MISSING** | No invocation id; `ToolResult` (41) carries `tool`, `output`, `dry_run` only. Trace ids exist but are per-request, not per-invocation. |
| G-15 | Trusted `TOOL_SUCCESS` with structured facts | §18.4 | **MISSING** | `output` is an arbitrary object stringified into the prompt (`str(result.output)[:1000]`, 640). No structured fact set, so "only the facts in the result" cannot be enforced. |
| G-16 | Trusted `TOOL_ERROR` scoped to the invocation | §18.3 | **MISSING** | Errors become `context = str(exc)` (700) and are re-narrated by the model. |
| G-17 | Provenance ledger | §9.3 | **MISSING** | No ledger. Memory components (`app/memory/*`) are semantic stores, not provenance. |
| G-18 | `USER_FACT` capture | §3.2 | **MISSING** | User-supplied operational values are not extracted or stored. |
| G-19 | `USER_REPORTED` distinct from tool-verified | §9.3 | **MISSING** | No source typing at all. |
| G-20 | Correction supersession | §10 | **MISSING** | No stored values, so nothing to supersede; the model is expected to remember corrections in the prompt window. |
| G-21 | Exactly one response obligation per operational turn | §14.1 | **MISSING** | No obligation concept. |
| G-22 | Deterministic operational response construction | §15 | **MISSING/CONFLICTING** | Operational replies are produced by `llm_client.chat` and only cosmetically cleaned (`clean`, `app/brain/response_cleaner.py:36`). Two deterministic exceptions exist: `try_direct_reply` (`app/brain/direct_responder.py`) and the fixed `confirm_action` sentence (711). |
| G-23 | Operational raw-model-prose lock | §3.1 / INV-001 | **MISSING** (the central gap) | Nothing distinguishes a model draft from an approved response; `finalize_reply` (602) returns model text for every operational branch. |
| G-24 | Capability-unavailable handling, no tool substitution | §13 | **MISSING/CONFLICTING** | An unsupported request is handed to the LLM with no tool result; the model may narrate it as done. Embedding tool selection (`_select_tool_with_embeddings`, 141, flag off) is *similarity-based substitution* — directly contrary to §13.2 if enabled. |
| G-25 | Ambiguity handling without invented targets | §17 | **MISSING** | `extract_app_name` yields a pseudo-target for "open it"; there is no `REQUEST_TARGET` path. |
| G-26 | Audit covering the 17 contract fields | §19.1 | **PARTIAL** | Good foundation: async JSONL audit (`app/logs/audit.py:46`) with `trace_id` correlation, `intent_classified` / `tool_call` / `tool_result` / `approval_gate_*` events. Missing: raw vs canonical arguments, permission decision as a first-class field, guard decision, provenance updates, response obligation, final response source, final user-visible response, safety outcome. |
| G-27 | No chain-of-thought in audit | §19.2 | **IMPLEMENTED** | Nothing logs model reasoning; `think` is suppressed for the main path (`llm_client._suppress_thinking`, 116). |
| G-28 | Feature flag for the new path | entry criteria | **PARTIAL** | `agent.hermes_enabled: false` exists (`app/config.py:177`, `config.yaml:168`) but nothing reads it; there is no mode model and no integration boundary behind it. |
| G-29 | Rollback path | entry criteria | **PARTIAL** | Git revert plus config edit is possible; there is no flag-driven rollback because there is no flag-driven path. |
| G-30 | Conformance tests CT-001…CT-018 | §23 | **MISSING** | `tests/` covers router rules, safety levels, pipeline smoke; `evals/` covers product behaviour. Neither asserts a contract invariant. |
| G-31 | Metric separation (model quality vs system safety) | §20 | **MISSING** | `evals/` grades product behaviour as a single quality number. |
| G-32 | Prompt-injection containment as policy | §21 | **PARTIAL** | Structurally, model text cannot call a tool directly — the router chooses the tool — but tool *output* is injected into the prompt (`context`) and the model's narration is returned verbatim, so injected content can shape the user-visible answer on an operational turn. |
| G-33 | Hermes adapter / structured proposals | §2.1, §18.1 | **N/A-YET** | No adapter exists; `agent.hermes_*` are configuration stubs only. |
| G-34 | Idempotency / duplicate-execution protection | §18.2 (implied) | **MISSING** | No invocation ids or idempotency keys; a repeated `/confirm/{id}` is protected only by `dict.pop` (793). |
| G-35 | Lifecycle-safe pending state | §12, §24 | **MISSING** | Deep sleep exits the process (`resource_auto_deep_sleep_exit`), silently discarding every pending confirmation. |
| G-36 | Shared-Ollama model ownership | contract §6.2 extension discipline | **CONFLICTING** | `unload_all_ollama_models` (`app/resource_manager.py:559`) unloads every model loaded in the shared server, including models this instance does not own. |

## Summary

| Status | Count | Rows |
|---|---|---|
| MISSING | 21 | G-01, G-02, G-04, G-06, G-08, G-11, G-12, G-14, G-15, G-16, G-17, G-18, G-19, G-20, G-21, G-23, G-25, G-30, G-31, G-34, G-35 |
| PARTIAL | 8 | G-05, G-09, G-10, G-13, G-26, G-28, G-29, G-32 |
| MISSING/CONFLICTING | 2 | G-22, G-24 |
| PARTIAL/CONFLICTING | 2 | G-03, G-07 |
| CONFLICTING | 1 | G-36 |
| IMPLEMENTED | 1 | G-27 |
| N/A-YET | 1 | G-33 |
| **total** | **36** | |

**Interpretation.** The production system today is a *model-authoritative* assistant with a
safety-level gate in front of tools. The contract requires a *control-plane-authoritative*
assistant. The gate (`registry.call`) and the audit/tracing foundation are genuinely reusable;
the classification, response construction and state layers are not — they must be added beside
the existing path, behind a flag, rather than retrofitted into `_process`.
