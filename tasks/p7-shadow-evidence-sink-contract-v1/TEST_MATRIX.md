# Future sink implementation test matrix

46 normative future cases; no sink exists and none of these runtime cases are executed in this documentation task. Use isolated temporary backend fixtures, injected clocks and failure injection only. Backend-specific barriers/restart/concurrency tests must be exact once selected. Existing application test assertions/consumer budgets require their own D10 authorization. Current full regression does not establish running-sink compliance.

| ID | Case | Required assertion |
|---|---|---|
| S01 | Durable accepted write | Complete barrier-satisfied write returns accepted=True with committed sequence, aware UTC and correct digest; queue/buffer alone cannot return success |
| S02 | UTC helper ownership | Only P1 utc_now chronology helper invoked during acceptance, no dispatcher/audit/producer clock ownership |
| S03 | Timezone awareness | Naive or non-UTC injected source rejected with CLOCK_INVALID; no host-locale inference |
| S04 | UTC ISO representation | Persist aware UTC as exact isoformat +00:00, preserve precision, no latency arithmetic |
| S05 | Record version preservation | Persist explicit sink_schema_version=1 and observation_schema_version=1 without changing D03 fields |
| S06 | Immutable record and receipt | Frozen/slotted receipt and record; input unchanged; no mutable source refs retained |
| S07 | Restart persistence | Previously acknowledged entries recover unchanged after process/Core restart; sequence/history not reset |
| S08 | Stable durable ordering | Concurrent commit/restart establishes unique evidence sequence; no timestamp/object/filesystem order inference |
| S09 | Duplicate attempt ambiguity | Same turn/equivalent observations not counted automatically as distinct valid samples; no guessed retry key; D02/D07 dependency explicit |
| S10 | Storage-position collision | Reject conflicting committed sequence/integrity rather than overwrite retained evidence |
| S11 | Malformed record | Wrong shape/extra fields/inert semantic contradiction rejected; no repair or evaluation |
| S12 | Unsupported version | V2/bool version and unknown literals rejected; no silent conversion or migration |
| S13 | Partial interrupted write | Partial entry remains excluded from committed set; preserved diagnostic material, incomplete coverage, no hidden truncation |
| S14 | Integrity failure | Changed observation/sequence/time/version fails digest verification and cannot enter complete measurement set |
| S15 | Permission denied | EACCES creates truthful nonaccepted STORAGE_FAILURE and incomplete affected coverage; no policy/audit fallback |
| S16 | Disk full | Injected ENOSPC produces failure/uncertainty as appropriate; no deletion, pruning, live request failure or fabricated success |
| S17 | Inode/quota exhaustion | Simulated inode/quota creation failure handled as evidence failure without consuming real disk or altering quotas |
| S18 | Storage unavailable | Missing/inaccessible device/root rejects; no remote, audit/P2 or arbitrary-path fallback |
| S19 | Sink failure receipt | accepted=False metadata fields None and fixed failure code; no request/path/exception content |
| S20 | Uncertain commit | Failure after possible write yields COMMIT_UNCERTAIN; not proved absent/durable, no blind retry or count inflation |
| S21 | Acknowledgment lost | Recovered durable entry can exist without caller receipt; require external reconciliation; do not rewrite/retry as success |
| S22 | Legacy isolation | Future isolated caller sink errors/receipt failures/cancellation preserve exact legacy response and streaming; no real traffic |
| S23 | Raw user text excluded | Sink cannot enrich 18-field record with request/target/headers/P2 or failed-input dump |
| S24 | Raw model text excluded | No model/candidate/proposal prose or exception string added to serialized evidence/logging |
| S25 | No audit fallback | Audit imports/writer calls patched to fail; both success and persistence error remain separate |
| S26 | No provenance fallback | P2 store construction/mutations forbidden for success and failure |
| S27 | No network | Socket/http/provider telemetry calls forbidden; only confined local evidence operations |
| S28 | No registry/handler | registry.call/get/discovery and handlers forbidden; no live registry access |
| S29 | No dispatcher/executor | No dispatch or executor import/call in acceptance/recovery/errors |
| S30 | No model/provider/Ollama | No adapter/model/provider query/process or fallback on write error |
| S31 | Reconciled submission coverage | For independent recoverable B with B=C, D=0 and no unknowns/duplicates, sink coverage can reconcile; still no global CT/pass claim |
| S32 | Known loss invalidates | Missing/failed submission marks affected window INCOMPLETE; scored subset cannot hide it |
| S33 | Persisted count insufficient | C alone or max(sequence), no-gap sequences and absent error logs cannot establish B or A |
| S34 | Upstream attempt dependency | No eligible-attempt/turn equality or fake ID for pre-context/no-terminal failure; D02/D07 accounting required |
| S35 | Open window after restart | Without recoverable upstream start/end/submission proof, restarted measurement cannot claim complete |
| S36 | P7 retention gates | No TTL/destructive rotation/prune on window end/restart/rollback/disk full; explicit cleanup only after all gates |
| S37 | Clock rollback/repetition | Repeated/backward UTC values retained without synthesized correction; durable order authoritative only for evidence |
| S38 | Clock excludes authority/latency | No monotonic/perf_counter measurement; timestamp affects no permission/confirmation/CT threshold or IDs |
| S39 | Serialization allowlist | Exactly six outer fields/18 observation fields, enums .value, correlation initial IDs, explicit nullable keys; no generic object conversion |
| S40 | Canonical integrity | Canonical UTF8 sorted compact JSON/digest invariant to map key order; content/time/order/version change alters digest |
| S41 | Confined private storage | Client ID/path/traversal/symlink cannot escape approved namespace; no public mount; verify local access and backup/export scope |
| S42 | Import/passive boundary | Module import performs no filesystem/clock/worker side effect; future code/test importer budget separately authorized |
| S43 | No upstream reevaluation | Classifier/router/binder/proposal/permission/response builders forbidden during persistence |
| S44 | Cross-session and trace distinction | Original correlation copied intact with separate trace; valid record for different session never silently reassociated |
| S45 | Exact evaluated-set seal | Ordered committed set/digests/versions reconciled with independent submissions; missing or duplicated set cannot hide behind equal counts; SHA256SUMS excludes itself |
| S46 | No real exhaustion or destructive recovery | Fault injection only in isolated future tests; never fill live disk, remove evidence, invoke recovery on production or change nightly job |
