# IDEMPOTENCE — specified, not implemented

Normative: 13B11P-R1 `IDEMPOTENCE.md`. Nothing to measure; no module exists.

The guarantee is designed to rest on the type, not on a check. `RecordedTurn` holds no
callable, executor, dispatcher, registry handle, confirmation store, ledger store, session
object or clock, and both timestamps (`recorded_at`, `evaluated_at`) are admitted data. So
the pipeline performs no write, no mutation, no identifier mint and no executor call in any
mode, on any branch, including every failure branch — and re-running the same
`RecordedTurn` is byte-equal rather than merely equivalent.

Frozen execution-count invariants the implementation must measure:

| Situation | Executor | Dispatcher | New invocations | New trusted results | New claims |
|---|---|---|---|---|---|
| initial turn blocked or mismatched at any guard | 0 | 0 | 0 | 0 | 0 |
| confirmation required, before any valid claim | 0 | 0 | 0 | 0 | 0 |
| valid confirmation continuation | 0 | 0 | 0 | 0 | 0 |
| initial turn, actual `ALLOW`, no admitted result | 0 | 0 | 0 | 0 | 0 |
| result replay, any status | 0 new | 0 | 0 | 0 | 0 |
| the same result replayed again | 0 new | 0 | 0 | 0 | 0 |

Not promised, and not to be invented: idempotency across *different* `RecordedTurn` values
describing one user action — that belongs to the dispatcher's claimed-invocation set and
the store's single-claim rule, both outside the pipeline — and detection that a replayed
result was already reported in an earlier turn.
