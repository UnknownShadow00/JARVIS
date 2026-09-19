# Task 13B11F — Implementation Notes

Production phase **P3 (second unit)** of `tasks/task13b11a/IMPLEMENTATION_PHASES.md`. Pure and
unwired: the lane policy exists, is exhaustively tested, and nothing calls it.

Production commit `a69f33e00a62050aaecf941b93e7beaa0394fffd` on `main` in `/home/jarvis/JARVIS`,
parent `e7432431b5aaa18eb692b94a5520bdb9184dde62` (13B11E, P3 canonicalizer). Three files added,
**1,138 insertions, 0 deletions, 0 files modified**. Not pushed.

## 1. What was added

| File | Lines | sha256 |
|---|---|---|
| `app/execution/lane.py` | 223 | `3367a6b541ec38c855f8078129e711fb363ce9a2c754f4be4966a18fd27af137` |
| `tests/execution/lane_test.py` | 538 | `e806e765ee5af7fa57f93d611c226f5ce0cc9e293acf2c13991a7a85476f4db0` |
| `tests/execution/lane_non_activation_test.py` | 377 | `b852d39589ccb405a8e9cc0221f1ab8043aeb076eba73eaa9e37474efab2d261` |

Public surface: `decide`, `explain`, `LaneSignals`, `LaneDecision`, `LaneReason`,
`LanePolicyError`; constants `LANE_POLICY_VERSION`, `ALWAYS_OPERATIONAL_CLASSES`,
`DEFAULT_CONVERSATIONAL_CLASSES`, `SIGNAL_REASONS`, `NO_SIGNALS`. `Lane` and `RequestClass` are
imported from `app/execution/types.py`, never redefined.

## 2. Order of work

The truth table was derived from the frozen contract and hashed
(`24968be4a892ebbb72a8ed4602ea755e82dd49aa292c454bf3810dab62ed4e30`) **before** the module and both
test files existed. The tests transcribe that table by hand and recompute the expected lane with
their own small function rather than importing the policy, so the implementation is checked against
the contract rather than against itself.

## 3. Design decisions and why

**The policy is three lines and a table.** Always-operational class → OPERATIONAL; any condition →
OPERATIONAL; otherwise CONVERSATIONAL. There is no fourth branch, no per-class special case, no
scenario-specific logic and no benchmark string anywhere. The class membership lives in two
frozensets and the condition list in one read-only mapping, so the policy reads as data.

**Escalation is structural, not conventional.** The function has no code path that returns
CONVERSATIONAL after finding operational state — the conversational return is only reachable when
the class is conditional *and* every condition is false. That is why the 896-row sweep over the
seven always-operational classes can be asserted to produce exactly `{OPERATIONAL}`. §4.2 is
enforced by the shape of the function, not by a rule a later edit could forget.

**Conditions are booleans the caller supplies, not state the policy reads.** `tool_result` comes
from the P5 dispatcher, `confirmation_required` from P4, `tool_proposal` / `action_target` /
`external_status_claim_required` from the P3 router, and `active_operational_provenance` /
`operational_correction` are a projection of the P2 ledger. Passing the projection rather than the
ledger keeps the function pure, keeps it testable as a table, and — as the task required — stops
the lane policy acquiring a hidden dependency on P2 storage.

**`signals` is required, not defaulted.** An implicit all-false default would mean a caller that
forgot to pass its state silently got the conversational lane. Requiring the argument makes the
omission a `TypeError` at the call site instead of a quiet downgrade.

**`isinstance`, not equality, decides membership.** `RequestClass` is a `str` enum, so
`"VALUE_QUERY" == RequestClass.VALUE_QUERY` is true and the two hash alike — a bare string would
sail through a dict lookup. Both the class and the signals record are checked by type. A test
asserts the equality first and the refusal second, so the reason for the check is recorded in the
suite.

**There is no fallback lane.** Malformed input raises `LanePolicyError`. Falling open to
CONVERSATIONAL would mean that corrupting the deterministic state makes model prose *more* likely
to reach the user — the exact bypass INV-001 exists to prevent.

**Booleans are checked with `is`.** `1`, `"yes"` and truthy objects are rejected. A policy whose
outcome depends on the truthiness of whatever the caller passed is not deterministic in the sense
§4.1 means.

**Reasons exist because the contract asks for them.** §14.1 names "lane reasons" as a frozen input
to the obligation engine, and P6 has no other source for them, so `explain()` returns a
`LaneDecision` with an ordered `LaneReason` tuple and `decide()` returns just the lane. Reasons are
metadata: they authorize nothing, create no provenance, and are **not** added to the 17-field audit
schema.

## 4. The one interpretation, recorded not guessed

Whether the seven conditions reach `GENERAL_EXPLANATION` is genuinely ambiguous if the YAML key
`always_conversational_classes` is read alone. The normative sections resolve it: §4.1 defines
OPERATIONAL by what a turn *involves*, naming a tool result among them; §4.3 applies the conditions
"additionally", which only means anything for classes not already unconditionally operational; §4.2
forbids re-labelling an operational turn conversational; and INV-001/INV-010 fail if a turn holding
a tool result reaches the conversational lane. Of the two readings only this one can never make
model prose more trusted, which is also what fail-closed requires. Recorded in `TRUTH_TABLE.md` §6
and `02-contract-and-plan-verification.txt` §8. No contract file was modified.

## 5. Deviation from the planned signature

`PRODUCTION_INTEGRATION_PLAN.md` sketches `lane.decide(class, route, snapshot, events)`. `route` is
the P3 router result, `snapshot` the P2 ledger snapshot and `events` the P1 stream; the router does
not exist yet and reading the ledger here is forbidden. `LaneSignals` is the deterministic
projection of exactly those three objects, which the P7 pipeline will fill in. The planned name
`decide` is kept. `TARGET_COMPONENT_MAP.md` maps both `lane.py` and `lane-policy.json` onto this one
module, so the table lives here as data rather than in a separate config file.

## 6. What was deliberately not done

No wiring into any request or response path. No request classifier and no action router — nothing
in the module parses text, and `app/execution/` contains no classifier or router module. No
permission, confirmation, dispatch or obligation logic. No audit event and no schema change. No
provenance read or write. No canonicalizer call. No new correlation identifier. No change to the
frozen P0 types, and no duplicate `Lane` enum. `ProvenanceSource` was **not** extended for TIMEOUT.
The three operator decisions — lane as an audit field, the redaction secret-key list, TIMEOUT as a
provenance source — were left open, and tests assert they are still in their pre-task state.

## 7. Verification

`pytest -q` went 758 → **1068 passed**, 11 deselected, 0 failed; `tests/execution` 341 → 651; the
310 new tests pass on their own (201 + 109). The deterministic golden ran 12/20 before and after
with the same eight failing IDs. The legacy probe, carried byte-identically from 13B11B/C/D/E
(`bb4624f9…`), produced `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` at
`e743243` before `lane.py` existed and the identical digest at HEAD after the commit.

All 19 critical production files hash identically before and after — verified by diffing the two
hash blocks, not by eye. `execution.lane` references outside the package: 0. Lane-policy symbols
outside the package: 0. `app.execution` outside the package: 1, the P0 line `app/config.py:14`. The
1,152-row sweep under a CPython audit hook fired **no** sensitive runtime event. Execution mode
`legacy`, `hermes_brain=False`, `hermes_enabled=False`; Hermes at `2237be35`, clean, 0 processes;
shared Ollama `{"models":[]}` throughout — no model was loaded for this task.
