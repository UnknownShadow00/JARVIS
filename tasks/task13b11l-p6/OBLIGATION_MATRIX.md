# Obligation Matrix — Task 13B11L-P6

**FROZEN AND HASHED BEFORE `app/execution/obligations.py` EXISTED.** That is the method
this series runs on, and it earned its keep again here.

## 1. Provenance of the table

The blocked task 13B11L deliberately did **not** freeze a matrix
(`tasks/task13b11l/OBLIGATION_MATRIX.md`): one of its inputs was about to change, and
*"freezing a table that is known to be about to move would invert the method"*. R1 and R2
made the change. This table is frozen against the corrected P3 outputs, at classifier rule
set **"2"**, and the old blocked analysis is untouched history.

Expectations are computed by an `if` ladder written in contract rank order, in the shape of
the validated 13B10C5 `derive_obligation`, deliberately **not** the shape the module takes
(an ordered rule table selected by minimum rank). Two independent shapes that must agree is
the point.

Rows whose inputs come from real requests — the 41 unsupported verbs, the chat controls, the
supported-action controls, the ambiguity controls — are composed through the **live**
`classify -> route -> lane` chain, not hand-written.

## 2. Digests

| Version | Rows | SHA-256 | Why |
|---|---|---|---|
| v1 | 503 | `77a42976461cd61a64bc34184569e305d6bf8577c68585eb4ccef72505cd54b6` | first freeze, module absent |
| v2 | 513 | `e6c53692f1a09b7c8948e0a004fc69eb08327fe2524fb8d34aa4a4fbe0b05c3a` | +10 rows, purely additive |
| **v3** | **442** | **`4d5c788a3ac81cfc4adf09a0f7430bb69ca74833f0e39c76ab3b0750f1325adf`** | confirmation input reshaped |

Nothing was re-frozen to make the module agree. Both movements are recorded because both
have a cause outside the module's behaviour:

**v1 → v2** added group `G11` after the freeze script's own coverage assertion was
strengthened from "every obligation is reachable" to "every *reason* is reachable" and
`external_status_claim_without_trusted_result` turned out never to be selected. Proven
additive: 10 rows added, **0 removed, 0 moved** — every one of the 503 original rows is
byte-identical in v2, and `obligation_priority`, `obligation_source`, `value_projections`
and `classifier_version` are identical.

**v2 → v3** changed an input *column*: `confirmation_state: ConfirmationState` became
`confirmation_claimed: bool`, because importing P4's confirmation machine broke the
zero-importer invariant P5 had gone out of its way to preserve. See `DECISION_INPUT.md` §3.
Group `G1` shrank (8 confirmation states → 2 approval states) and group `G12` was added
(class × permission × approval, 72 rows), so the table is narrower in one dimension and
wider in another.

## 3. What v3 contains

```
rows                 442
valid                370   (361 operational + 9 conversational)
contradictions        72
```

| Group | Rows | What it varies |
|---|---|---|
| `G1` result-permission-confirmation | 48 | every (result status, permission outcome, approval) on one action turn |
| `G2` class-value | 54 | every request class × every value projection |
| `G3` action-target-capability | 48 | every primary action × target resolution × capability |
| `G4` multi-action | 16 | every primary action × multi-action |
| `G5` reporting-intent | 72 | 12 base states × all 6 reporting intents |
| `G6` unsupported-verbs | 41 | the router's 41 unsupported verbs, through the real chain |
| `G7` controls | 16 | plain chat, a declarative remark, supported actions, through the real chain |
| `G10` ambiguity-controls | 6 | real ambiguous phrasings, through the real chain |
| `G11` external-status-claim | 10 | a required external status claim × value |
| `G12` class-permission | 72 | every class × every permission outcome × approval |
| `G8` priority-overlap | 38 | one row per pair of ranks in play |
| `G9` contradiction | 21 | one row per contradiction code |

Recorded per row: lane, request class, lane reasons, primary action, reporting intent,
target resolution, multi-action, capability, permission outcome, approval, result status,
result executed, value projection — and the expected `ResponseObligation`, priority, reason,
source, plus validity or the exact contradiction code.

Every one of the eleven obligations and all twenty-two reasons are reachable from a valid
row; every rule wins at least one row; every contradiction code is reachable.

## 4. What the freeze caught

Two rank predicates, while there was still nothing to unpick:

1. All 41 unsupported verbs landed on rank 1 (22, answered "shall I proceed?") or rank 4
   (19, answered "which one?") rather than rank 6. Both imply an execution that can never
   happen, which contract §13.1 forbids in terms. See `OBLIGATION_PRIORITY.md` §3.
2. Four input combinations P4 and P5 cannot produce were not being refused
   (C-17 … C-20), and a fifth (C-21) emerged from the v3 reshape.

The module was then written against the corrected table and agreed with it on the **first
run**, 0 failures across all 442 rows including the min-rank priority proof.

## 5. Where it lives

* sealed: `/home/jarvis/.hermes-poc/evidence/task13b11l-p6-obligation-engine/obligation-matrix.json`
* repo fixture: `tests/execution/obligation_matrix.json`, columnar, carrying
  `source_matrix_sha256` so a reader can tie it back to the sealed table. The fixture is the
  expectation; the module is what is measured against it. **Never regenerate it from the
  module.**
