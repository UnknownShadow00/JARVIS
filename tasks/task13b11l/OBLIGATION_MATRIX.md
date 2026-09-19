# Obligation Matrix — Task 13B11L

**NOT FROZEN. NOT HASHED. Deliberately.**

Task §46 requires a frozen, hashed matrix before implementation. It is not produced here, and
that is a decision rather than an omission.

## Why not

One of the matrix's inputs is about to change. `P3_RECONCILIATION.md` establishes that twenty
explicitly requested operations currently arrive as `OTHER`/`NONE`/`CONVERSATIONAL` and never
reach `REPORT_CAPABILITY_UNAVAILABLE`. Once the upstream fix in `BLOCKING_CHANGE.md` lands, they
arrive as `ACTION_REQUEST`/`UNKNOWN_ACTION`/`OPERATIONAL` and do. Every rank-6 row, and every row
that currently falls through to rank 11, moves.

Freezing and hashing a table that is known to be about to move would invert the method that has
protected this series: in 13B11K the frozen table caught five wrong cells precisely *because* it
was settled before the code. A table frozen against inputs in flux proves nothing, and re-freezing
it a task later would quietly normalise re-freezing.

## What the unblocking task should freeze

The dimensions are settled even though the values are not:

| Dimension | Values |
|---|---|
| lane | `OPERATIONAL`, `CONVERSATIONAL` |
| request class | the 9 `RequestClass` members |
| route condition | `primary_action` ∈ 8, `target_resolved` ∈ {True, False, None}, `multi_action`, `capability_available` |
| permission outcome | `ALLOW`, `REQUIRE_CONFIRMATION`, `DENY`, absent |
| confirmation condition | none required / required and unclaimed / claimed |
| tool result | absent, `SUCCESS`, `ERROR`, `TIMEOUT`, `BLOCKED`, `CONFIRMATION_REQUIRED` |
| reporting intent | the 6 `ReportingIntent` members |
| value availability | none / current `VERIFIED` / current `SUPPLIED` / superseded only |

Recorded per row: expected `ResponseObligation`, expected source, expected reason, and
validity — `valid` or `contradiction` per `CONTRADICTION_POLICY.md`.

Coverage requirement: every one of the 11 `ResponseObligation` members reachable by at least one
valid row, every contradiction row raising, and `MISSING_CONTEXT` reachable **only** where no
higher-priority grounded source exists (CT-018).

## Two mapping questions to settle before the freeze

Both are recorded in `CONTRADICTION_POLICY.md` §3 and neither should be decided silently by an
implementer:

1. **`PermissionOutcome.DENY`** has no obligation of its own in the frozen eleven. Does it map to
   `REPORT_CAPABILITY_UNAVAILABLE` (rank 6), or does the contract need a twelfth member — which
   would be a contract extension under §6.2, not an implementation choice?
2. **`ToolResultStatus.TIMEOUT`** — `REPORT_TOOL_ERROR` (rank 2) is the honest family, since
   rank 3 would claim the effect happened. But "errored" and "outcome unknown" are different
   statements, and the distinction currently survives only in the `TrustedToolResult` the builder
   reads, not in the obligation.

These are the same shape as the 13B11I permission-matrix decisions: operator questions, answered
once, in writing, before the table is hashed.
