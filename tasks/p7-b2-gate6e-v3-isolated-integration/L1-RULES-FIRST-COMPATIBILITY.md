# Provisional rules-first L1 compatibility

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

`source_legacy.py` contains the exact reviewed deterministic rules, router/responder prompt values and pure response cleaner. Complexity code changes only configuration reads to required constructor injection. `source_profiles.json` pins original source and prompt hashes. `legacy.py` consumes those definitions; it never invokes original model clients, procedural-memory singletons, embeddings, `_process` or `_process_stream`.

| Unchanged pilot input | Deterministic intent | Conditional model classifier | Conditional complexity / responder |
|---|---|---|---|
| Hello. Reply briefly. | None | Required, actual output must pass schema | trivial / gemma3:4b /80 |
| What is two plus two? | respond,0.9, original rule | None | normal / qwen3-nothink /150 |
| Name one primary colour. | None | Required | normal / qwen3-nothink /150 |
| Please give a brief friendly greeting. | None | Required | normal / qwen3-nothink /150 |

All four lack a deterministic direct reply in original source. The source-backed classifier schema is exactly intent/confidence/suggested_tool/reasoning; temperature0.1, source confidence threshold0.75. The new parser rejects missing/extra/duplicate fields, bool confidence, nonfinite/out-of-range/low confidence, suggested tools, nonconversational intents and malformed JSON. It does not clamp unknown intent into respond, extract embedded JSON, synthesize low-confidence fallback, or invoke embeddings. These stricter refusals are experimental deltas requiring approval.

Deep regex/intent selection remains source-backed (qwen3:14b when main=qwen3-nothink, think=true,700 output) but execution is explicitly unavailable pending an additional binding/experiment decision. Exact alternative effective models and their no-think compatibility are not qualified. No unapproved deep contract is created.

Responder prompt includes original action-tag examples; native action/tool proposals are rejected before cleaning/delivery. Original markdown/opener/two-sentence cleaning is retained. Memory is an explicit bounded nonproduction snapshot (empty in qualification), never live procedural memory. Original legacy build_prompt uses system/current user without prior turns; this behavior is retained. Actual legacy send completion supplies bounded assistant history for observational continuation; Granite never does.

Historical two-field/L2 synthetic policies were moved into test-only HistoricalFakePolicy to preserve old state-machine tests. The isolated application factory requires RulesFirstL1; there is no product exact-input classification allowlist or canned response.

If all four classify successfully and all substeps settle: 3 classifier +4 responder +4 Granite =11 operations for4 accepted attempts. The successful fake fixture demonstrated this conditional path; it is neither a prediction of stochastic outputs nor an approved workload. Real transmissions:0.
