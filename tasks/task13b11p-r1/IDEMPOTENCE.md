# IDEMPOTENCE AND EXECUTION COUNT

## The guarantee rests on the type, not on a check

`run_recorded_turn` is a pure function of one immutable argument. `RecordedTurn` holds no
callable, no executor, no `ToolExecutor`, no `TrustedDispatcher`, no `ConfirmationStore`,
no `LedgerStore`, no session object, no clock and no mutable collection. Both timestamps
the pipeline needs (`recorded_at`, `evaluated_at`) are admitted data, so there is no clock
to read and no source of run-to-run variation.

Therefore the following are structural, not asserted: the pipeline performs no write, no
mutation, no identifier mint, no network or process access, and no executor call — in any
mode, on any branch, including every failure branch. A guard that could be bypassed is not
what protects these properties; there is nothing present to bypass it with.

## Replaying the same admission

Replaying the same `RecordedTurn` must never cause a double execution, a new confirmation,
a new invocation or a new `TrustedToolResult`. In P7 v1 the stronger statement holds: it
causes none of those the *first* time either.

| Repeated action | Effect |
|---|---|
| same mode-A turn, twice | equal outcome both times; 0 executor calls; 0 writes |
| same mode-B turn, twice | equal outcome both times; the record is not mutated, not expired and not claimed; 0 executor calls |
| same mode-C turn, twice | equal outcome both times; `ObligationState.result` is the same admitted object; 0 **new** executor calls, invocations, claims or trusted results |

Response and obligation construction over an already-existing result is deterministic and
read-only: `obligations.derive`, `response.build` and the provenance selection are pure
over the admitted evidence, and `ApprovedOperationalResponse.created_at` comes from
`evaluated_at`, so two runs of the same admission are byte-equal, not merely equivalent.
The execution count is unchanged by any number of runs because it is zero in all of them.

## Execution-count invariants (frozen)

| Situation | Executor calls | Dispatcher entries | New invocations | New `TrustedToolResult` | New confirmations / claims |
|---|---|---|---|---|---|
| initial turn, blocked or mismatched at any guard | 0 | 0 | 0 | 0 | 0 |
| confirmation required, before any valid claim (mode A waiting) | 0 | 0 | 0 | 0 | 0 |
| valid confirmation continuation (mode B) | 0 | 0 | 0 | 0 | 0 |
| initial turn with an actual `ALLOW` and no admitted result | 0 | 0 | 0 | 0 | 0 — stops at S09 |
| result replay (mode C), any status | 0 new | 0 | 0 | 0 | 0 |
| the same result replayed again | 0 new | 0 | 0 | 0 | 0 |
| any admission failure, any stage | 0 | 0 | 0 | 0 | 0 |

The task's phrasing "valid confirmation continuation: at most the single execution
permitted by dispatcher claim semantics" is satisfied at its lower bound, and necessarily
so: P7 v1 holds no executor, and the single permitted execution — if it ever occurs — is
performed by `TrustedDispatcher` under its own `_claimed` idempotency set, outside this
pipeline and before a mode-C admission. P7 neither performs it nor can repeat it.

## What is deliberately *not* promised

P7 v1 does not provide idempotency across *different* `RecordedTurn` values that describe
the same intent. Deduplicating two distinct admissions of one user action is the
dispatcher's `_claimed` set and the confirmation store's single-claim rule, both outside
P7. P7 also does not detect that a mode-C result has already been reported to a user in an
earlier turn; reporting history is not part of the frozen stage structure. Both are
recorded in DEFERRED.md rather than invented here.
