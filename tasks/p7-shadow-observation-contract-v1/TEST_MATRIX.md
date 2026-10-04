# Future implementation test matrix

40 normative future cases; **not implemented or executed observation tests**. Setup may create/read isolated fixtures before runtime guards; then producer calls must be pure. Do not widen production/test consumers or use real server/model/tool traffic to score this contract. Existing P7/f-map fixtures and genuine existing owner outputs are the source of eligible alternatives, never fake authoritative live IDs or model-generated policy.

| ID | Case | Settled input or runtime guard | Required assertion |
|---|---|---|---|
| O01 | Completed conversation | actual ConversationalResponse | CONVERSATIONAL/MODEL_RAW, no stop/obligation/text; same authoritative turn |
| O02 | Stopped operation | actual PipelineStop | copy exact stage/reason; no candidate obligation/source |
| O03 | OPEN_APP binding | settled actual V1 apps binding | copy OPEN_APP/apps.open/apps; fingerprint full canonical expected binding, no target text |
| O04 | OPEN_URL binding | settled actual V1 browser binding | copy OPEN_URL/browser.open/browser; fingerprint exact canonical URL binding without URL text |
| O05 | Unsupported action | actual UNKNOWN_ACTION/empty V1 pair and actual terminal | metadata digest retained; admitted-binding fields None; actual route/action/outcome copied |
| O06 | Third mapping/model-selected tool | untrusted proposal names another tool | cannot populate binding fields from it; compare copied genuine V1 tuples against frozen closed rows outside producer |
| O07 | Zero proposals | externally observed successful parser tuple length 0 | count=0, match=None; preserve actual terminal, do not invent proposal_required for conversation |
| O08 | One full match | count=1 and externally observed full guard pass | match=True; present genuine binding; no permission/execution inferred |
| O09 | One mismatch | actual S06_MATCH and one of three mismatch reasons, captured guard failure | count=1, match=False, exact existing reason |
| O10 | Multiple proposals | captured count >1 and actual terminal | match=None; exact MULTIPLE_PROPOSALS only where P7 actually returned it |
| O11 | Unknown comparison | count=1, no captured complete guard fact | match=None; do not infer it from completion/permission |
| O12 | Permission deny | already-settled genuine P4 DENY | copy DENY; producer does not decide/refuse/rebuild response |
| O13 | Confirmation required | genuine P4 REQUIRE_CONFIRMATION and applicable actual candidate | copy policy/obligation label only; no claimed-confirmation or token |
| O14 | Trace association | context trace distinct from authoritative turn | copy both associations; no conversion/equality assertion |
| O15 | REST | settled JARVIS transport http | retain exact existing http vocabulary |
| O16 | WebSocket | settled JARVIS transport websocket | retain exact existing websocket vocabulary; output chunks are not terminal attempts |
| O17 | Raw user/target secret | raw text present only in source context/route/binding | no request/target/map/clauses in output; only canonical-binding fingerprint can be content-derived |
| O18 | Raw model/candidate/exception secret | source objects contain model/candidate text or component prose | none read/hashed/retained/serialized, including error messages |
| O19 | Output immutability | attempt assignment and source mutation after returned record | frozen/slotted; no mutable backing aliases; logical record unchanged |
| O20 | Deterministic repeat | same settled facts supplied repeatedly; canonical map key order varies | same logical record; same sorted-JSON fingerprint; no new attempt inferred |
| O21 | Cross-turn/session mismatch | terminal correlation/turn differs from settled context | fail closed, no fabricated association |
| O22 | Contradictory route/permission | available state and settled owner values disagree | reject; do not pick majority/re-evaluate |
| O23 | Bad cardinality/match | negative/bool count; count!=1 with match; actual mismatch with True | reject exact malformed/contradictory inputs |
| O24 | Clock guard | time.time/datetime.now/monotonic/perf_counter/utc_now patched to fail | zero clock calls, no time fields read or recorded |
| O25 | Audit guard | audit writer/to_audit_entry/ExecutionAuditRecord forbidden | zero audit calls; no audit-v3 representation |
| O26 | Provenance guard | P2 constructors/stores/record_* forbidden at producer call | zero P2 writes; no snapshot/ledger retained |
| O27 | Registry and handler guard | registry.call/get/live discovery/handler invocation forbidden | zero registry/handler entry; no source-snapshot call/file reads |
| O28 | Dispatcher/executor guard | dispatch/build_invocation/executor forbidden | zero calls and no result/handle input |
| O29 | Model/provider guard | Hermes/Ollama/provider/model transport forbidden | zero calls; no adapter evaluation/parser inside producer |
| O30 | External I/O guard | filesystem/socket/process/thread/queue writes forbidden after setup | zero external I/O and no scheduling/persistence |
| O31 | Owner evaluation guards | classify/route/canonicalize/decide/derive/build/proposal-guard forbidden | only settled projection/validation/hash; no hidden pipeline advancement |
| O32 | Execution truth injection | executed=True or result object or state confirmation_claimed=True | reject, even an unexecuted result object is outside inert V1 |
| O33 | Terminal source injection | forged tool-success/error source or obligation / wrong response lane enum | reject inert out-of-scope or malformed candidate; no external operation asserted |
| O34 | Missing adapter observation | real ADAPTER_INVALID stop with no successful tuple | count/match=None; no model-absent success or fake response |
| O35 | No P7 terminal/no authoritative context | envelope/context/binding/provider/producer failure without eligible TurnOutcome | no V1 record; future failure/loss mechanism remains unresolved |
| O36 | No binding versus empty binding | None versus genuine BinderV1 empty pair | all None versus retained metadata digest; no default missing-to-empty conversion |
| O37 | One-sided/mutable binding | expected without query or mutable/non-primitive canonical map | reject, never repair or recanonicalize |
| O38 | CT-013 structured support | actual conversation candidate without integrated cleaner observation | record lane/source only; no invented safety_passed or CT pass |
| O39 | CT-001 structured support | actual operational candidate with adversarial upstream model text | source/obligation support only; no visible delivery/draft-retention/CT pass assertion |
| O40 | Attempt/delivery ambiguity | two equivalent observations for same turn or repeated producer call | deterministic value only; no global dedup/delivery/attempt-count claim |

P4 denial fixtures may exercise already-settled existing decision vocabulary separately from the two admitted F-MAP rows. A record test does not establish every policy outcome is reachable for each closed V1 row; do not alter permission policy to force DENY coverage. Any owner-produced decision must come from actual existing P4 behavior or a clearly isolated typed projection test, with no claim of a live grant.

Freeze tests for fixed failure categories with no raw text in exception output. Source/call graph tests must prohibit hidden imports/lookup and clock/persistence even when happy paths pass. No observation-runtime pass is claimed from the current 5721-test regression.
