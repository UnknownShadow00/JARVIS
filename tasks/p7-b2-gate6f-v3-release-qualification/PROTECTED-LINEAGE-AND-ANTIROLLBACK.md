# Protected lineage and antirollback

Gate 6F isolated review. No production epoch created, retired or modified.

## G6F-SEC-01 (High): V2 `OPERATOR_STOP` does not prove an operator stop

V2's FastAPI `lifespan` calls `stop_admissions()` with no argument on any shutdown; its default reason is `OPERATOR_STOP` (source-proof test `test_original_lifespan_writes_operator_stop_on_any_shutdown`). A host power-off, `systemctl stop` or SIGTERM all write the same row as a deliberate operator stop.

This happened in production: at **2026-10-15T03:42:17Z** Core logged `Power key pressed short` (an ACPI power-button event from the hypervisor), powered off and booted 26 s later. The V2 service stopped cleanly; D09 now reads `epoch 606a991a… CLOSED_COMPLETE`, `pilot_events=[OPERATOR_STOP]`, zero attempts/submissions/receipts. With `Restart=no` and autostart disabled it stayed stopped. That is exactly the shape the 6E `validate_v2_archive` accepted as "operator retired".

Fix in candidate `ff2444df…`:
- `validate_v2_archive` now proves only a **clean zero-use closed epoch** (`V2_NOT_CLEAN_ZERO_USE_STOP`), and every proof carries `stop_attribution='UNATTRIBUTED_V2_SHUTDOWN_HOOK'`.
- `HighWater.reserve_successor` puts `stop_attribution` and `retirement='EXPLICIT_OPERATOR_ZERO_USE_RETIREMENT'` into the payload the operator signs, so retirement intent comes only from that signature. A proof claiming another attribution is refused (`test_v2_archive_proves_zero_use_only_and_successor_payload_acknowledges`).
- Archive tampering now always yields a fixed refusal code instead of leaking historical exception types (`test_corrupt_predecessor_archive_refused_with_fixed_code`, 5 mutations).

## Source of truth (proposed)

| Item | Proposed authority |
|---|---|
| V2 predecessor identity | epoch id + archive manifest digest + V2 implementation hashes, inside the signed successor payload |
| Immutable predecessor archive | V2 bundle copied into the protected root, read-only, digest pinned |
| Exactly one V3 successor | singleton row in the protected high-water DB + `O_EXCL` reservation file |
| Global accepted cap and high-water | `accepted` table (ordinals 1–4, REST,REST,WS,WS) in the protected DB, written before local acceptance |
| Transport ordinal association | permit → ordinal → transport → session → commitment, joined to the controller row |
| One-use permit consumption | controller `permits.spent` + durable `control.nonce` |
| D09/D06 truth | versioned controller schema 5 + domain ledger; coordinated checkpoint joins all |
| Restores/backups | review-only export; no runtime restore path exists |
| Permanent abort | monotonic terminal value in controller and protected root |

## What the tests prove and what they do not

| Class | Status | Evidence |
|---|---|---|
| Local transactional correctness | PROVEN | SQLite `FULL` sync, single writer lock, triggers; competing successors and writers (6E) |
| Filesystem crash correctness (process level) | PROVEN at tested boundaries | real child-process exits, interrupted reservation/checkpoint, kernel `RLIMIT_FSIZE` short writes (6F) |
| Partial rollback (one component older) | DETECTED | `test_partial_rollback_of_highwater_or_controller_is_refused` |
| Full coordinated rollback (all same-UID state replaced together) | **NOT DETECTED** | `test_coordinated_full_rollback_is_not_detectable_locally` restores state, high-water, evidence and domains to before the attempt; every local check passes with 0 accepted. The only trace is a newer coordinated checkpoint the same attacker could delete. |
| Privilege-based protection | NOT QUALIFIED | needs OS separation |
| Host-loss tolerance | NOT PROVEN | no off-host copy |
| Privileged attacker | NOT PROTECTED | root or the owning uid can replace state and hashes together |

Hashing alone gives no antirollback against an actor who can replace both state and hashes.

## Proposed protected authority (needs separate approval)

An append-only high-water service on a different trust domain than the runtime: either (a) a root-owned helper on Core exposing only `reserve(successor)`, `accept(ordinal, permit, commitment)`, `terminal(value)` and `read()` over AF_UNIX, storing a hash-chained log in a root-only directory and mirroring each record off-host before acknowledging, or (b) an operator-controlled off-host log (signed by the human signer) that the runtime must read back before each acceptance. Access contract: service uid may call the four verbs only; nobody but root may write the store; the operator signs successor reservation and terminal acknowledgement.
