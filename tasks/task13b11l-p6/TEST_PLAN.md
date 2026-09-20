# Test Plan — Task 13B11L-P6

1378 new tests in four files, 0 existing tests changed.

| File | Tests | What it settles |
|---|---|---|
| `obligations_matrix_test.py` | ~1100 | the 442 frozen rows, four assertions each, plus the min-rank priority proof per row |
| `obligations_test.py` | ~45 | each rule stated in words: confirmation, error, timeout, success, refusals, ambiguity, values, attribution, lanes, model non-authority, shape |
| `obligations_p3_reconciliation_test.py` | ~75 | the 41 unsupported verbs and the controls, composed through the **live** `classify -> route -> lane` chain |
| `obligations_non_activation_test.py` | ~160 | purity, no raw text, no prose, no live wiring |

## Matrix conformance

Every valid operational row: obligation, priority, reason and source all match the frozen
expectation. Every conversational row returns `None` and `require()` refuses it. Every
contradiction row raises with its exact frozen code — except C-09, which the type system
makes unrepresentable, and the test asserts that instead.

## The priority claim, measured

Per row, not once: `min(rank of every rule that holds) == derive(state).priority`.
`satisfied(state)` exposes the full set, so the result is provably independent of
declaration order (task §64).

## Coverage, with no silent gaps (task §37)

* every one of the eleven `ResponseObligation` members is reachable from a valid row;
* every one of the twenty-two `ObligationReason` members is reachable;
* every one of the twenty-one rules wins at least one row;
* every one of the twenty `ObligationContradiction` codes is reachable.

Each is a test, not a review note. The reason-coverage assertion is also inside the freeze
script, which is how the missing `external_status_claim_without_trusted_result` state was
found before the module was measured.

## Reporting-intent invariance

Twelve base states × all six intents, asserted to collapse to one outcome each (§7.1,
INV-017). Stronger than omitting the field.

## Model non-authority (task §65)

A `ModelDraft`, a `ToolProposal`, a mapping, a bool and a string are each refused by type in
the `result` slot. Bare enum *values* (`"DENY"`, `"OPERATIONAL"`) are refused too — the
str-enum trap this series has hit before. `ObligationState` is asserted to carry no
model-shaped field and no `str`-typed field at all.

## Purity (task §66)

An AST import-budget test pins the module's imports to exactly eight names. A tokenized
code-only scan rejects ~40 forbidden constructs. A `sys.addaudithook` run drives every rank
240 times and asserts zero `open`, `socket`, `subprocess`, `time.sleep`, `exec`, `eval` or
`import` events and no new threads. Determinism is checked over 200 identical calls. The
registry, the audit writer and the provenance surface are monkeypatched to raise and never
hit.

## No response text (task §67)

Every string constant in the module is walked; any that could be shown to a user — `", sir"`,
`"Done"`, `"Please confirm"`, `"Which "`, `"successfully"` and a dozen more — fails the test.
`ObligationDecision` is asserted to have exactly three fields and no message. Every reason is
asserted to be a machine code: lowercase, no spaces, alphanumeric once underscores are
removed.

## No live wiring (task §68)

Zero modules under `app/` import the engine; zero references to any public symbol; the live
request path is scanned by name; `app/execution/__init__.py` does not mention it; no call
site of `derive`, `require`, `source_for`, `satisfied` or `contradiction` exists under
`app/`; `registry.call` still has exactly four call sites, all in `app/server.py`. Proven
again independently over parsed imports in `07-no-live-wiring.txt`.

## What is deliberately not tested here

The response builder (P6 unit 2) does not exist. Live dispatch, a real capability
projection, a real provenance projection and the pipeline are P7+ and remain unwired.
