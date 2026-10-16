# Provider bounding results (G6E-LP-1 qualification)

Gate 6F isolated qualification. No real Ollama contact. All proposed legacy limits remain **unapproved for live use**.

## Request-size fit (16,384 B cap), real source prompts and the pinned procedural-memory snapshot (1,877 B)

Measured from serialized request bodies in `test_four_inputs_with_source_memory_fit_bounds_and_record_sizes` (artifact `request-size-fit.json`):

| Input | Transport | Router bytes | Responder (model, ctx/out, bytes) | Granite bytes (history msgs) |
|---|---|---|---|---|
| 1 | REST | 1,159 | gemma3:4b 4096/80, 4,673 | 687 (0) |
| 2 | REST | — (rule) | qwen3-nothink 32768/150, 4,679 | 800 (2) |
| 3 | WS | 1,162 | qwen3-nothink 32768/150, 4,682 | 690 (0) |
| 4 | WS | 1,176 | qwen3-nothink 32768/150, 4,696 | 820 (2) |

**All four inputs and all 11 conditional operations fit**, maximum 4,696 B (29% of cap). Headroom (`message-headroom.json`): any plain 8 KiB message fits every operation; worst-case JSON escaping (6×) leaves 1,954 B of user text for the responder-with-memory request. Oversize payloads are refused before any possible-send record (`test_oversize_responder_request_refused_without_truncation`); the accepted attempt is burned, never refunded. Memory over 8 KiB is refused, not truncated.

## Per-row findings

| Row | Values | Finding |
|---|---|---|
| Legacy classifier | gemma3:4b, 4096/64, temp 0.1, 20 s, 16 KiB/16 KiB, keep-alive 60 | Options equal the original except `keep_alive` (original sends none). Digest UNVERIFIED. |
| Legacy trivial | gemma3:4b, 4096/80, 180 s, keep-alive 60 | Original sends no `num_ctx`; 4096 matches only if the server default is 4096 (UNVERIFIED). |
| Legacy normal | qwen3-nothink, 32768/150, 180 s, keep-alive 60 | **Not source-faithful**: source Modelfile sets `num_ctx 8192` and the original never overrides it. 32768 also raises KV-cache residency on a GPU that Granite (64k context) may share. **Proposal G6F-LP-2: 8192**, subject to attesting the installed Modelfile. |
| Granite observer | frozen profile `jarvis.p7.ollama.granite41.b1r2.v1`, 64000/128, 180 s, keep-alive 60, 16 KiB, think/stream false, no retry | Unchanged. `observation.py` is byte-identical to 6E; changed-limit/resource tests still refuse. |

## Native option support

| Field | Basis | Status |
|---|---|---|
| `model`, `messages`, `stream:false` | Ollama `/api/chat` contract, used by original code | Supported (historical use) |
| `think:false` | Original router already sends it to gemma3:4b; original responder sends it to both | Historical use; behaviour on the **installed** Ollama version UNVERIFIED |
| `options.num_ctx`, `num_predict`, `temperature` | Documented Modelfile parameters; original uses all three | Supported; effect on residency UNVERIFIED |
| `keep_alive` (integer seconds) | Documented request field; **never sent by original code** | Accepted per API docs; overrides server env for that model; effect on co-resident models UNVERIFIED |

Keep-alive is a request hint, not a lease: it neither proves residency nor provides exclusivity.

## Operation accounting

Successful four-input path: 3 classifier + 4 responder + 4 Granite = **11 operations for 4 accepted attempts** (TEST). Truthful early-failure counts (`test_operation_counts_decrease_truthfully`):

| Variant | Recorded possible-sends = transmissions |
|---|---|
| Rules refusal (`run bash`) | 0 |
| Classifier refusal | 1 (router) |
| Responder failure (rule path) | 1 (responder, REMOTE_UNKNOWN) |
| Delivery failure | 2 (router, responder); Granite never runs |
| Granite failure | 3; legacy delivery stays `LOCAL_SEND_COMPLETED` |
| Success, rule path | 2 |
| Success, classifier path | 3 |

In every variant the attempt count stays 1 and no next permit is grantable after a failure. A model operation needs an accepted attempt (`test_no_model_operation_without_accepted_attempt`), a durable possible-send, a D06 lease (`TRANSPORT_OWNERSHIP_REQUIRED`) and a clear domain. No retries, speculative calls or discovery: across all 11 operations the only URL path is `/api/chat`.

New in 6F: known D06/domain conflicts are refused **before** a possible-send is recorded (`OwnedProvider.precheck`), so a refused operation is no longer counted as `REMOTE_UNKNOWN`. Races after the precheck stay conservatively unknown.

## Conservative time envelope (`time-envelope.json`)

Per-operation deadlines only: router 3 × 20 s + responders 4 × 180 s + Granite 4 × 180 s = **1,500 s of provider time** (per input: 380 / 360 / 380 / 380 s). Excluded and additive: the unapproved delivery deadline, human permit latency between attempts, and checkpoint cost (offline, the whole turn including coordinated checkpoint took 0.44–0.76 s on ext4). No hidden overall deadline exists. The 30 s local drain closes the local transport only; it does not guarantee remote completion, and remote-unknown holds survive it (`test_remote_unknown_is_never_released_automatically`).
