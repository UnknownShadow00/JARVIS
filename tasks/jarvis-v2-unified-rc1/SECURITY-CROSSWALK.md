# Security verification on actual merged source

All cases below passed in final source-bound runs. RESULTS.json and
TEST-OUTCOMES.json identify exact runs/node IDs; SECURITY-SELECTED-RESULTS.json
records overlapping selected replays without double counting.

| Required protection / negative case | Merged implementation | Direct current evidence |
|---|---|---|
| Anonymous/invalid Bearer authority access | api.require_authority_identity, including embedded /ready | test_authority_http_security; test_release_security::test_empty_token_authority_access_refused_even_embedded; real separate-process loopback socket fixture |
| Blank-token startup refusal | server.lifespan .strip() check | test_transport_lifespan_rejects_blank_identity_before_background_work (3 cases) |
| CLI/probe/reporter compatibility | cli ready/tasks/recovery; /health liveness; in-process reporter | test_ready_client (12); full-app CLI with actual readiness payload; test_operator_app; test_reporter; consumer static review |
| Hostile WebSocket frames and all-exit cleanup | bounded ConnectionManager/UE5ConnectionManager and endpoint finally | test_ue5_security; test_release_security; test_server_auth; real Starlette protocol state and TestClient sessions |
| Filesystem races/private creation | StorageAncestry no-follow descriptors, race refusal, post-create verify | test_storage_ancestry_security; parent-replacement and original SQLite-swap harness in test_release_security |
| Docker build-context exclusions | allowlist plus nested private exclusions | STATIC-CHECKS.json, independent rule/order and Dockerfile COPY review; no actual daemon build |
| Durable identity/receipts/duplicate execution | Authority transactions, phase_id, signed transport history | test_execution_pipeline; test_secure_transport duplicate concurrent submissions; actual API receipts and restart replay |
| Single-writer fencing | Authority ownership lock/retained ancestry/ledger guard | process actor tests; stale owner, lock contention, replaced ancestry, duplicate worker tests |
| Lost acknowledgments/forged receipts | UNKNOWN without redispatch; separately permitted reconciliation/publication | signed transport fault/crash stages; protocol forgery; CLI explicit reconciliation; 15 SIGKILL cases with zero redispatch |
| Witness/checkpoint integrity | LedgerGuard/RecoveryRegistry trusted references and continuity | rollover, witness renewal, stale substitution, signed proposal rebinding and registry corruption tests |
| Safe archive restoration | authenticated immutable export, inert branch/proposal approval | test_audit_disaster; test_recovery_decisions; restore races/tampering/path refusal; full-app disaster demonstration |
| Real-executor bypass refusal | exact allowlisted synthetic types/destinations, closed legacy effects | test_disabled_by_default_sealed_types_and_independent_keys; test_no_arbitrary_or_real_destination; test_audit_integration_fixes |
| Startup/shutdown fail closed | explicit authority enrollment; stop releases worker/scheduler/store | test_stock_startup_still_requires_real_admission_context; full-app lifespan/restart/shutdown; readiness corruption refusals |

This proves the stated offline fixture behavior. Installed identities, independent
custody, different principals, TLS/ingress, native filesystem/power-loss semantics,
actual VM/broker facts and current dependency advisory status remain BLOCKED / NOT
VERIFIED. They are not recast as protections proved by synthetic tests. See
AUTHORIZATION-REQUIREMENTS.md and INDEPENDENT-SECURITY-REVIEW.md.
