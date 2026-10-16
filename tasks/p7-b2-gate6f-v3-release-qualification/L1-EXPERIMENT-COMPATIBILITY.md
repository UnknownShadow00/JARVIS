# L1 experiment compatibility (Gate 6F)

Gate 6F isolated qualification. No production change, real model request, credential use, deployment, V2 retirement or pilot opening. Nothing here approves the experiment.

Candidate `ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733`. Original legacy source compared byte-for-byte against production `/home/jarvis/JARVIS` at entry (read-only): `router.py dc285697…`, `complexity_router.py f3f3f753…`, `response_cleaner.py 882d7d21…`, `prompts.py fe51f5ab…`, `llm_client.py 39068dd1…`, `Modelfile.nothink a95f2319…`, `skills.md 3a61af60…` (tracked, unchanged vs HEAD). Production `config.yaml` (`00d7b460…`) nonsecret keys read: `models.router=gemma3:4b`, `models.main=qwen3-nothink`, `router_context=4096`, `main_context=32768`, `ollama_base_url=http://localhost:11434`, `safety.confidence_threshold=0.75`, `routing.embedding_enabled=false`.

Evidence levels: **SRC** proven by source, **TEST** proven by isolated test (`v3_release_qualification_test.py` / 6E suites), **RUNTIME** needs effective-runtime attestation, **HUMAN** needs operator decision.

## The four inputs (unchanged)

| # | Input | Original rule result (SRC+TEST) | Model classifier | Complexity → responder | Ops if all succeed |
|---|---|---|---|---|---|
| 1 | Hello. Reply briefly. | None | required | trivial → gemma3:4b, 80 | router, responder, Granite |
| 2 | What is two plus two? | respond 0.9 (rule) | **not called** (TEST: zero router calls) | normal → qwen3-nothink, 150 | responder, Granite |
| 3 | Name one primary colour. | None | required | normal → qwen3-nothink, 150 | router, responder, Granite |
| 4 | Please give a brief friendly greeting. | None | required | normal → qwen3-nothink, 150 | router, responder, Granite |

Classifier decisions in the tests are named synthetic fixtures; no real classification is predicted. None of the four selects the deep branch (TEST).

## Behaviour deltas

| Aspect | Original V2 (SRC) | Gate 6F candidate | Class |
|---|---|---|---|
| Deterministic classification | `_classify_by_rules` runs first | Same function, AST-extracted and hash-pinned | **PRESERVED ORIGINAL SEMANTICS** |
| Model-backed classification | Only when rules return None; `/api/chat`, router prompt, `think=false`, `stream=false`, `temperature 0.1`, `num_predict 64`, `num_ctx 4096` | Identical messages and options (TEST byte-level prompt equality); plus explicit `keep_alive` | **PRESERVED** (keep-alive row below) |
| Classifier confidence | `<0.75` rewritten to `confirm_action`; pipeline continues to a client-visible confirmation path | Attempt refused and burned; no reply | **SAFETY-RESTRICTED DELTA REQUIRING APPROVAL** |
| Parser refusal | Regex-extracts embedded JSON, unknown intent → `respond`, clamps confidence, parse/Ollama error → `respond 0.5` → `confirm_action` | Exact four-field schema, no extraction/clamp/fallback; error refuses | **SAFETY-RESTRICTED DELTA REQUIRING APPROVAL** |
| Complexity choice | `ComplexityRouter.decide` | Same code; settings reads replaced by constructor injection | **PRESERVED** |
| Deep branch | `qwen3:14b`, `think=true`, 700 | `DEEP_EXPERIMENT_UNAPPROVED` refusal; no call (TEST) | **SAFETY-RESTRICTED DELTA** — explicit restriction, not compatibility |
| Legacy model selection | trivial → `models.router`, normal → `models.main` | Same names, bound per contract | **PRESERVED** by name; installed model identity/digest **UNVERIFIED RUNTIME DEPENDENCY** |
| Prompt template | `build_prompt`: system prompt + `\n\n` + procedural memory; user message only | Byte-equal to `build_prompt()` for all four inputs (TEST) | **PRESERVED** |
| Memory snapshot | `skills.md` read live every turn, first 12 bullets (1,877 B today) | Pinned snapshot via `procedural_snapshot(sha256=3a61af60…)`; oversize refused, never truncated | **SAFETY-RESTRICTED DELTA** (frozen vs live). The 6E qualification default of an **empty** snapshot is a **CHANGED EXPERIMENT — NOT AUTHORIZED** |
| History capture | Legacy prompts contain no prior turns | Unchanged for legacy; bounded session history (≤8 msgs/8 KiB) used only as Granite's pre-turn context | **PRESERVED** for legacy; observation-only addition |
| Cleaner | `response_cleaner.clean` | Same code; empty cleaned reply refused; native `tool_calls` / `[ACTION:` refused before cleaning | **SAFETY-RESTRICTED DELTA** |
| Responder native options | Only `num_predict`; no `num_ctx` → context from the installed Modelfile (source `Modelfile.nothink`: 8192) or the server default (gemma3:4b) | `num_ctx` 32768 normal / 4096 trivial | normal 32768: **CHANGED EXPERIMENT — NOT AUTHORIZED** (differs from source 8192); trivial 4096: **UNVERIFIED RUNTIME DEPENDENCY** (equals original only if the server default is 4096) |
| Streaming | REST non-stream; WS `stream=true` into TTS, then one cleaned `reply` frame | `stream=false` for both; one envelope per transport | Client-visible shape **PRESERVED**; internal streaming **SAFETY-RESTRICTED DELTA** (voice/TTS are off in the pilot) |
| Retry | Router: none. Responder: 3 retries on connection errors (1, 2, 4 s) with spoken error | Zero retries anywhere | Router **PRESERVED**; responder **SAFETY-RESTRICTED DELTA** |
| Timeout | Router `httpx.Timeout(20)` per phase; responder `Timeout(600)` per phase × up to 4 tries | Whole-operation deadline 20 s / 180 s | **SAFETY-RESTRICTED DELTA** (stricter) |
| Keep-alive | Never sent → server policy (`OLLAMA_KEEP_ALIVE`; project standard `-1` = never unload) | Explicit `keep_alive: 60` | **SAFETY-RESTRICTED DELTA REQUIRING APPROVAL** + **UNVERIFIED RUNTIME DEPENDENCY** (effective server policy unknown) |
| Generated vs delivered | `reply = clean(generated)`, sent to client | Only cleaned legacy text is delivered/history-visible; `LOCAL_SEND_COMPLETED` = ASGI send returned, not proof a human saw it; Granite never delivered (TEST) | **PRESERVED** for content; evidence semantics added |
| Endpoint | Source `http://localhost:11434`; production may override via protected environment | Bound per contract | `LEGACY_EFFECTIVE_ENDPOINT=UNVERIFIED`. No Ollama process listens on Core at entry, so effective routing is not Core-local unless overridden |

"Exact equivalence" is not claimed. The proven equivalences are narrower: same rule function, same classifier request messages/options, same complexity decisions, and byte-equal legacy prompt construction given the pinned snapshot.

## Section 5 proof map

1. Rules first: `test_rules_first_integrated_four_turns`, `test_four_inputs_with_source_memory_fit_bounds_and_record_sizes` (input 2 → zero router calls).
2. Rule result → no classifier call: same, plus `test_operation_counts_decrease_truthfully[success_rule_path]`.
3. Only unresolved → one bounded router: four-turn op sequence; router `num_predict 64`, 20 s.
4. Four-field schema and 0.75 threshold: `test_classifier_strict_no_fallback` (7 variants).
5. Unsafe results refuse: `test_rules_reject_before_any_model` (6), classifier variants, deep branch.
6. Complexity: `test_exact_source_complexity` (5).
7. Prompt/cleaner/history: `test_prompt_construction_matches_original_build_prompt`, 6E cleaner tests.
8. Legacy-only delivery: four-turn tests assert no Granite text in replies or session history.
9. Granite independent and passive: canonical observer request equality; `granite_failure` variant keeps the legacy delivery.
10. No dispatcher: 6E import-boundary tests; `/api/chat` is the only URL path observed across all 11 operations.
