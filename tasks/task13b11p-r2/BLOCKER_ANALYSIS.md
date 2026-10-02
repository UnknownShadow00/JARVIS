# BLOCKER ANALYSIS — P-B02

**JARVIS P7 PASSIVE PIPELINE BLOCKED.** No production file was created or modified.

## The blocker in one sentence

`RecordedTurn` field 15, frozen by 13B11P-R1 as `confirmation: ConfirmationRecord | None`
with exact type identity, cannot be implemented: it would make `app/execution/pipeline.py`
the first module under `app/` to import `app/execution/confirmation.py`, defeating a
zero-importer invariant that phases P5 and P6 each paid a cost to preserve and whose
stated rationale is precisely that an approval must reach a consumer as a *settled
projection*, never as the record.

## The invariant, measured

`tests/execution/confirmation_non_activation_test.py`

```
MODULE_PATH = pathlib.Path(confirmation_module.__file__).resolve()
REPO = MODULE_PATH.parents[2]
APP  = REPO / "app"

def test_no_module_under_app_imports_the_confirmation_machine() -> None:
    hits = []
    for path in APP.rglob("*.py"):
        if path.resolve() == MODULE_PATH:
            continue
        text = path.read_text()
        if "execution.confirmation" in text or "execution import confirmation" in text:
            hits.append(str(path.relative_to(REPO)))
    assert hits == []
```

The scope is **all of `app/`**, with no exclusion for `app/execution/` and — unlike the
obligation engine's equivalent — **no allowlist**. A second parametrized test,
`test_no_public_symbol_is_referenced_anywhere_under_app`, forbids each of 19 public
symbols as a bare **substring** anywhere under `app/`:

`ConfirmationState`, `ConfirmationEvent`, `ConfirmationRecord`, `ConfirmationBinding`,
`ConfirmationStore`, `ConfirmationError`, `ConfirmationNotFound`, `ConfirmationExpired`,
`ConfirmationBindingMismatch`, `ConfirmationDispatcherUnavailable`,
`InvalidConfirmationTransition`, `create_confirmation`, `next_state`, `TRANSITIONS`,
`TERMINAL_STATES`, `EXECUTION_STARTED_STATES`, `EVENTS_REQUIRING_DISPATCHER`,
`NON_CONFIRMABLE_ACTIONS`, `CONFIRMATION_STATE_MACHINE_VERSION`.

A third, `tests/execution/obligations_non_activation_test.py::test_the_confirmation_machine_keeps_its_zero_importers`,
states the rule normatively rather than incidentally:

> Phase P5 went out of its way to leave the P4 machine free of importers, and P6 keeps it
> that way: the contract's own confirmation state for an *action* is
> `ToolResultStatus.CONFIRMATION_REQUIRED`, already in `types.py`, and **whether an
> approval was claimed arrives as a settled projection. The record's lifecycle stays
> P4-internal.**

So 1 + 19 = 20 frozen assertions stand in the way, and the twentieth-first fact is worse
than the assertions: the design rule they encode is the one 13B11P-R1 contradicts.

## Why this is a contract defect and not an implementation problem

There is no implementation that satisfies both the frozen admission contract and the
frozen invariant:

- The contract requires `type(turn.confirmation) is ConfirmationRecord`. Obtaining that
  class object requires importing the module; there is no other legitimate route.
- A function-local import still leaves the forbidden substring in the file.
- A `sys.modules` lookup is a service locator, which 13B11P-R1 §27 forbids outright and
  which the dispatcher's forbidden-construct tests also pattern-match against.
- Duck typing the record would break the contract's frozen exact-type-identity rule and
  would be *weaker*, not stronger.
- Guards B-01…B-07 additionally need `ConfirmationState.PENDING`, `TERMINAL_STATES`,
  `is_fresh_at`, `execution_started`, `BINDING_FIELD_NAMES` and `NON_CONFIRMABLE_ACTIONS`
  — five more forbidden references.

Task §46 is explicit: an implementation bug gets fixed in the implementation; a frozen
contract ambiguity BLOCKS, and the contract is not changed silently. 13B11P-R1's own
`FREEZE_RECORD.md` says the same: "A discovered defect in this contract requires explicit
subsequent version history with new hashes and new evidence."

## Honest attribution

This is a defect I introduced in 13B11P-R1. I froze field 15 as the record type without
checking the confirmation zero-importer invariant, and it is the *same* mistake this
series already made and corrected once: P6 originally imported `confirmation.py`, the
existing suite caught it, and P6 was repaired by replacing `confirmation_state` with the
settled projection `confirmation_claimed` — at the cost of re-freezing its 442-row matrix.
The lesson was recorded. 13B11P-R1 reintroduced it anyway, in a document that cites that
very P6 repair elsewhere. The freeze-first method caught it again, one phase later and
before any production code existed, which is the method working — but it should have been
caught during R1's own review of the production sources.

## Second finding, not a blocker: the integration boundary needs sanctioned allowlist extensions

Measured for every module `app/execution/pipeline.py` must use. "Excludes `app/execution/`"
means the existing test already permits a sibling in the control-plane package.

| Module | pipeline must | Invariant scope | Assertions to extend |
|---|---|---|---|
| `types`, `correlation` | import | none, or package-scoped | 0 |
| `classifier` | call `classify` | `_production_sources()` excludes `app/execution/` | 0 |
| `lane` | call `explain` | excludes `app/execution/` | 0 |
| `canonicalize` | call `canonicalize` | excludes `app/execution/` | 0 |
| `provenance` | read the snapshot | excludes `app/execution/` | 0 |
| `app/brain/hermes_adapter` | call `parse_recorded_response` | already an allowlisted seam | 0–1 |
| `router` | call `route` | all of `app/`, excluded only by the filename `router.py` | ~12 |
| `permissions` | call `decide` | all of `app/`, no allowlist | ~15 |
| `obligations` | call `derive` / `require` | all of `app/`, **allowlist precedent** | ~12 |
| `response` | call `build` | all of `app/`, no allowlist | ~2 |
| `confirmation` | hold a `ConfirmationRecord` | all of `app/`, no allowlist, plus the P6 normative guard | ~20 **and contradicts the stated rule** |

The first ten rows are ordinary work of a kind the frozen 13B11O-R1
`IMPLEMENTATION_ACCEPTANCE.md` already authorizes: "Any phase-local non-activation
assertion update must name only the new passive importer and preserve zero live wiring,
with explicit justification." The precedent is exact — when P6 unit 2 landed, the
obligation engine's importer test was extended to name `app/execution/response.py`, and
its symbol test to permit `ObligationState` and `ObligationReason` in that one file.

Roughly 41 assertion extensions across `router`, `permissions`, `obligations` and
`response` are therefore unavoidable for *any* integration boundary, and none of them
weakens an invariant in substance: no live wiring, no request-path call site, and
`registry.call` stays at exactly four sites in `app/server.py`. They are nonetheless a
visible, countable change to four prior phases' non-activation suites, which no frozen
document has quantified before now. The operator should authorize that scope explicitly
rather than discover it inside a diff.

The eleventh row is the blocker and is categorically different.

## Required upstream fix (recommended, needs an operator signature)

Replace frozen field 15 with a JARVIS-owned settled projection, built by the caller from
the P4 record **outside** the pipeline, carrying only plain data and enums that already
live in `types.py`. Proposed name `RecordedConfirmationObservation`, frozen and slotted:

| Field | Type | Projected from |
|---|---|---|
| `confirmation_id` | `str` | `record.confirmation_id` |
| `session_id` | `str` | `record.binding.session_id` |
| `pending` | `bool` | the record's state being the pending state |
| `terminal` | `bool` | the record's state being terminal |
| `execution_started` | `bool` | `record.execution_started` |
| `claimed` | `bool` | `record.invocation_id is not None` |
| `fresh` | `bool` | `record.is_fresh_at(evaluated_at)` |
| `audit_session_id`, `audit_turn_id` | `str` | `record.audit_ref` |
| `action_type` | `PrimaryAction` | `binding.action_type` |
| `capability`, `tool_name` | `str` | `binding` |
| `permission_class` | `PermissionClass` | `binding` |
| `policy_version`, `canonicalization_version` | `str` | `binding` |
| `target`, `user_id` | `str \| None` | `binding` |
| `raw_arguments`, `canonical_arguments` | `Mapping[str, Any]` | `binding` |

Every type is from `types.py` or the standard library: zero confirmation import, zero
forbidden substring. All seven guards survive, restated over projected fields — B-01
session equality; B-02 `pending and not terminal`; B-03 `fresh`; B-04 audit reference;
B-05 `not claimed and not execution_started`; B-06 the same twelve-field binding equality
against this turn's actual route, expected projection and permission decision; B-07
`action_type not in obligations.NON_ACTION_OUTCOMES`, which is the identical three-member
set as the forbidden `NON_CONFIRMABLE_ACTIONS` and reachable through an import the
pipeline needs anyway.

The honest trade-off: `pending`, `terminal`, `fresh`, `claimed` and `execution_started`
become caller-projected booleans rather than values read from the record, so the caller is
trusted to project truthfully. That is the same trust 13B11P-R1 already places in
`expected` and `permission_projection`, and exactly the shape P6 chose for
`confirmation_claimed`. Security invariants S-02, S-03 and S-18 survive unchanged, because
their strength comes from B-06 binding equality rather than from reading the record; S-14
becomes *stronger*, resting on the absence of the import rather than on an allowlist.

Note what the fix does **not** do: it does not add a resting approved state, an
`authorized`/`ready_to_execute` boolean, or any authority field. `claimed` and
`execution_started` are refusal inputs — a claimed record is inadmissible in mode B — not
grants.

### Artifacts that a V2 of the admission contract must re-freeze

`TURN_INPUT_SCHEMA.md` (field 15's type, and the exact-type-identity sentence narrows to
fields 16–17), `ADMISSION_MODES.md` (the `c` term of the derivation),
`CONFIRMATION_CONTINUATION.md` (B-01…B-07 restated), `ASSOCIATION_RULES.md` (the
confirmation association section), `SECURITY_INVARIANTS.md` (S-02/S-03/S-14 mechanisms),
`IMPLEMENTATION_ACCEPTANCE.md`, and `ADMISSION_MATRIX.md` with `admission-matrix.json`
rows `B01`–`B07`, `X01` and `X02` — a new matrix digest. Fields 16 and 17
(`ToolInvocation`, `TrustedToolResult`) live in `types.py` and are unaffected, so modes A
and C and all 23 of their matrix rows stand as frozen.

## Alternatives considered and rejected

| Option | Why not |
|---|---|
| **B** — drop mode B from v1, leaving two admission shapes | Smaller contract change, but a continuation turn after an approval request would then have no representation at all, and nine matrix rows would be deleted rather than restated. Mode A covers only the first ask. |
| **C** — import `confirmation.py` and extend its 20 assertions | Contradicts the design rule P5 and P6 both paid to preserve, and would leave S-14 resting on an allowlist instead of on absence. The cheapest change to make today and the one most likely to be regretted. |

Recommendation: **Option A**, the settled projection.

## Two decisions the operator owns

1. Approve the Option A contract repair, to be landed as an explicit 13B11P-R1 V2 with new
   digests and new evidence, preserving the R1 documents as history.
2. Authorize the ~41 sanctioned non-activation allowlist extensions across `router`,
   `permissions`, `obligations` and `response`, naming `app/execution/pipeline.py` as a
   passive importer, with zero live wiring and no request-path call site.

Neither is a policy change and neither grants any new authority. Until both are settled,
no production pipeline code should be written.
