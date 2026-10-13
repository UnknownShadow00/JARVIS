# Security findings and fixes

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

Additional r2 hardening validates rehashed D06 state/scope/marker, global lineage and domain-operation joins independently; drain closes its transport without clearing remote unknown. Five further tests cover these corrections.

No new critical source finding remains open in the qualified isolated graph. Material corrected findings:

|ID|Severity|Defect / fix|Regression evidence|
|---|---|---|---|
|E01|High|Always-model/two-field/single-responder L1 replaced by source rules-first, exact schema and conditional responder selection|four-turn, unsafe rules, schema and complexity tests|
|E02|High|Native provider had no bounded transport/D06 consumer; added ownership-required bounded HTTP and durable domains|transport phase/framing/correlation/lease tests|
|E03|High|Released operation could replay internally; persistent operation tombstone now survives release|completed-domain-operation replay test|
|E04|High|Ingress did not receive disconnects during work; concurrent receive aborts without queue/fallback|disconnect during classifier, malformed WS/HTTP|
|E05|High|Global root did not bind controller predecessor archive; exact association now required|root mismatch and validated-archive full graph|
|E06|High|Terminal COMPLETE could survive failed final checkpoint; monotonic durable downgrade added|final-checkpoint-failure test|
|E07|Medium|Shared HTTP transport closed after first operation; borrowed wrapper plus explicit close|transport reusable test|
|E08|Medium|Historical product L2 fabricated exact-input intent; moved synthetic policy into test fixtures|application requires RulesFirstL1, historical assertions retained|
|E09|Medium|Delivery, operational D04 and backup consumers were disconnected; added bridge, uncertain joins and coordinated snapshots|D04 fault/duplicate, final forensic, checkpoint crash tests|
|E10|Medium|Stop during backup could report CHECKPOINT_HOLD; latch checked after publication|stop-during-checkpoint test|

Open release risks (high): no real separated signer/runtime attestation; no protected global root/rollback authority; no approved/effective legacy endpoint/model digests; no verified AI host or external lifecycle exclusivity; no installed production multi-resource D06/D09 migration/supervisor integration. These are blocked release boundaries, not silently approved defaults. Medium qualification limits: filesystem ancestor races under same UID, power-loss tolerance, real wire parser/cancellation and client delivery evidence.

Native schemas/tool proposals cannot dispatch operations: no operational registry/LLM client/voice/server import. The only permitted network-library import is bounded transport.py and only socket import is local_control.py; test rules enforce those exact locations and prohibit default network transports. build_production_runtime continues to refuse unconditionally.
