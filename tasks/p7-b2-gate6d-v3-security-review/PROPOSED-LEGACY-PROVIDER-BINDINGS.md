# Provider contract proposal G6D-LP-1 — NOT APPROVED

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
