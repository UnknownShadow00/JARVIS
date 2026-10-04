# JARVIS P7 SHADOW EVIDENCE SINK CONTRACT V1 FROZEN

D04 semantic/security choices are resolved: future app/execution/shadow_observation_sink.py; pure D03 producer remains unchanged; sink consumes ShadowObservationRecordV1 and returns immutable ShadowObservationSinkReceiptV1. No runtime module, consumer, test, dependency, policy or infrastructure change.

Clock: reuse existing P1 utc_now, aware UTC isoformat +00:00 for sink acceptance chronology only. No latency calculation, clock-derived authority or producer clock. Evidence: explicit sink/observation V1 versions, immutable 18-field payload, durable sequence and SHA256; no raw user/model text enrichment, operational audit/P2 truth or execution claims.

Retention: append-only through applicable P7 window completion, exit-bundle sealing and explicit operator acknowledgement/cleanup authorization; no numeric TTL, automatic pruning or destructive rotation. Durable success requires a committed recoverable local entry, not queue/task/buffer. Failures/unknown commit/recovery/integrity issues cannot become success; affected measurement coverage is incomplete and legacy must remain unaffected.

Storage root: existing Core PROJECT_ROOT/data (/home/jarvis/JARVIS/data), with a private confined future namespace; backend/leaf/barrier/framing/access mechanics are implementation details. No existing writer satisfies the required guarantees unchanged. No remote sink/dependency/export, deployment command or filesystem permission change. Existing backup interaction must be verified before future writes without inheriting off-Core authority.

Loss accounting: B=C for independently reconciled submissions is necessary only; eligible attempt coverage, retries/duplicate key, recoverable upstream intent/submission accounting and window scope remain D02/D07/controller dependencies. No fake IDs, retry ordinals, dropped-record defaults, complete-window or CT pass fabricated. Schema/code is not implemented.

Verification: canonical pytest **5721 passed, 11 deselected, 0 failed**, two existing warnings, 9.29s. Deterministic golden **12/20**, exact same eight failures, registry.call/network prohibited and trace persistence disabled in golden harness. Legacy uses prior sealed digest fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291 plus unchanged critical bytes, no fresh probe that might invoke Ollama. Static contract/source verification: **35 checks passed**, zero failed. The 46-case future matrix is not sink runtime testing. pip_audit is unavailable (No module named pip_audit); no vulnerability-audit pass claimed and no dependency installation.

Core remains clean at d3f44e01e7c63b0c2ba6f52f2dc93c48af34b69c, zero production changes; all 361 tracked hashes checked. Hermes remains clean at 2237be355906fbe6065ce1815711eee52b2d646e, disabled, zero processes; Ollama zero observed. No providers/models/tools/dispatch or live shadow traffic. Eight prior bundles: 770 checks, zero failures, historical seals unchanged.

Capacity: non-destructive df -h/-i and targeted usage checks; original local filesystem now has 2.9G free and Core 64G free. The original workspace safely holds this documentation branch docs/p7-shadow-evidence-sink-v1, based on verified D03 commit 28bfd59bc75a176d9804c0aa748f550cb5357390. Local main was not advanced; that archived D03 commit was fetched locally and checked out on the new docs branch. No isolated-only commit location is claimed and no cleanup/snapshot modification/manual push occurred.

New sealed evidence: /home/jarvis/.hermes-poc/evidence/p7-shadow-evidence-sink-contract-v1/. SHA256SUMS excludes itself and must verify with zero failures. The focused documentation SHA, complete git bundle/patch and final seal receipt identify the exact commit outside this report's self-reference. tasks/loop-log.md is appended before completion.

Formal P7 exit and P8 entry remain BLOCKED. Next smallest decision: **D05 — authentic current-turn adapter input / model-free scope**, before D06 provider/model/resource selection; D07 scheduler/accounting remains required in parallel. Original operator packet is re-read, unchanged. STOP; no next contract or runtime started.
