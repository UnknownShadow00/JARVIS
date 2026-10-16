# Release and retirement plan (unexecuted)

Nothing here is authorized. Every step needs its own operator approval.

## Current production fact that changes this plan

V2 is **stopped** since 2026-10-15T03:42:17Z (host power-off), epoch `606a991a…` is `CLOSED_COMPLETE` with an unattributed `OPERATOR_STOP` and zero use. Source and an existing V2 test (`shadow_pilot_test.py:223`) show a V2 restart against this controller refuses to start the pilot (`PILOT_EPOCH_ALREADY_EXISTS`); whole-application startup behaviour in that case is unverified. So "restart V2 SHADOW" is itself a production decision, not a neutral reset.

## Release contract

| Element | Proposed content |
|---|---|
| Candidate identity | manifest digest `ff2444df…` (29 members), full inventory `d31191bc…` (596 files); rebuild must reproduce both |
| Dependency pinning | the current `/home/jarvis/JARVIS/.venv` package set frozen to a hashed lock file; no install during release |
| Protected release directory | `/opt/jarvis-v3/<digest>/`, `root:root`, read-only to the service |
| Runtime identity | dedicated `jarvis-v3` uid (OS-IDENTITY-QUALIFICATION) |
| Operator authority | separate `jarvis-op` signer identity with presence proof; control socket group |
| Credentials | provisioned by the operator into a root-owned `0600` drop-in readable by `jarvis-v3` only; never by Codex/Claude |
| Unit | new `jarvis-v3.service`, `Restart=no`, not enabled, hardening per OS-IDENTITY; V2 unit untouched |
| D06/controller storage | new versioned roots (schema 5 + domain ledger); V2 namespaces read-only |
| Protected predecessor archive and successor root | per PROTECTED-LINEAGE proposed authority |
| Provider bindings | approved L1/LP contract + human attestations (endpoint, digests, topology) |

## Ordered procedure

1. **V2 zero-use archive** — with V2 stopped, take V2's own coordinated bundle (`shadow_backup.create_bundle`) read-only into the protected archive; run `validate_v2_archive`; the operator records the stop circumstances (power event) and signs the successor payload that states `stop_attribution=UNATTRIBUTED_V2_SHUTDOWN_HOOK`, `retirement=EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT`. No fabricated terminal archive.
2. **Protected root** — create the one-successor root and reserve exactly one V3 epoch.
3. **Install** — release directory, unit, identities, credentials (operator).
4. **Closed V3 startup** — start `jarvis-v3`, verify `CLOSED_INITIAL`, zero attempts, D06 empty, topology attested.
5. **Renewed Gate 5** — fresh authentication readback for V3; V2's Gate 5 does not transfer.
6. **Pilot opening** — separate human `OPEN_HOLD`; then one `AUTHORIZE_ONE` per attempt (REST, REST, WS, WS), each after a verified coordinated checkpoint.
7. **Terminal** — final truthful checkpoint (complete or forensic/incomplete), then Gate 7 review.

Rollback before step 4: delete nothing; leave V2 stopped or follow the operator's V2 decision. After step 4: stop V3 (`Restart=no`), keep all roots for review; there is no automatic V2 re-entry.
