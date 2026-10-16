# End-to-end integration audit

Gate 6F isolated audit of candidate `ff2444df…`. Candidate code is never mounted into the running application; no production module imports `candidate_v3` (read-only grep at entry: 0 files).

## Consumer graph and mandatory boundaries

| Stage | Code path | Boundary enforced |
|---|---|---|
| Operator authorization | `LocalControl.handle` → `Authority.check` → `Runtime.control` | AF_UNIX only, `SO_PEERCRED` uid, ≤20 KB, 5 s whole-request deadline (6F), canonical JSON, fixed verbs, 9 process bindings, ≤60 s expiry, signature + presence, **durable nonce before any effect (6F)** |
| One-use permit | `Store.arm` | ready checkpoint for current count, no outstanding permit, ordinal transport REST,REST,WS,WS, **coordinated checkpoint + evidence + high-water re-validated (6F)** |
| Durable acceptance | `Ingress` → `Runtime.request` → `HighWater.before_accept` → `Store.accept` → `HighWater.after_accept` | auth before body; strict framing/MIME/length; one in flight, no queue; continuation token; HMAC commitment equals permit; global reservation before local acceptance; never refunded |
| Legacy routing | `RulesFirstL1.route` | rules first; one strict classifier; complexity binding; deep refused |
| Every model operation | `Runtime._generate` → `OwnedProvider.precheck` (6F) → `Store.begin` → `OwnedProvider.request` → `NativeTransport.request` | serialized size cap; known D06/domain conflict refused before possible-send; substep order; durable step row; domain hold; actual D06 lease; exact native schema/options; deadline; framing; correlated terminal envelope |
| Legacy reply | `legacy.clean` → `_deliver` | proposal/action refusal; cleaned legacy text only; `LOCAL_SEND_COMPLETED` only from a completed ASGI send |
| Granite observation | `_generate('GRANITE')` → `CanonicalObserver` | starts only after `LOCAL_SEND_COMPLETED`; canonical request equality; frozen profile; pre-turn history; output never delivered |
| D04/D09 join | `EvidenceBridge.commit`, `Store.receipt`, `Store.settle` | uncertain-before-join marking; exact sequence/digest/correlation; settle requires receipt and delivery |
| Coordinated backup | `CheckpointWriter` → `validate_coordinated` | no holds, high-water match, staged write + fsync + rename publish, independent revalidation |
| Next-permit eligibility | `Runtime.control` | **6F: coordinated bundle bound to the exact controller checkpoint, evidence and high-water revalidated** |
| Stop/drain | `Runtime.stop`, `drain` | monotonic terminal; 30 s bound; transport closed; remote unknown retained; final checkpoint or forensic/incomplete |
| Startup | `Runtime.__init__`, `build_isolated_app` | persisted bindings/epoch match; existing control rows or attempts → recovery hold; graph must be complete, **including qualified topology (6F)** |

## Bypass search

| Candidate bypass | Result |
|---|---|
| Next permit after a fault that occurs after the last good checkpoint | **Found and fixed (6F)** — previously only the local controller checkpoint was re-verified |
| Known D06 conflict recorded as a possible send | **Found and fixed (6F)** — truthful counts via precheck |
| Replayed signed `TERMINAL_STOP` changing in-memory state | **Found and fixed (6F)** |
| Unattributed V2 stop accepted as operator retirement | **Found and fixed (6F)**, see PROTECTED-LINEAGE |
| Shared host behind different ports treated as independent | **Found and fixed (6F)** via attested topology |
| Direct transport call | refused without a real lease (6E) |
| Direct `_generate` without an accepted attempt | refused, zero calls (6F test) |
| Lifecycle/load/unload | always refused; only `/api/chat` observed |
| Production factory | `build_production_runtime` refuses unconditionally |

Residual notes: a WebSocket without an `Origin` header (non-browser client) is accepted subject to bearer auth; browser clients always send `Origin`. Session tokens are created by the core owner (`new_session`), not by a public endpoint; delivery of the token to the client is a release-procedure item.
