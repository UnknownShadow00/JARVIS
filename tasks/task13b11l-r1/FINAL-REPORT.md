# Task 13B11L-R1 — P3 unsupported-verb classifier reconciliation

## Verdict

**JARVIS P3 CLASSIFIER RECONCILIATION IMPLEMENTED**

Production `/home/jarvis/JARVIS`, one commit:

```
9ace0e3a0855708d992467a179d08f6affef43e1   fix: reconcile unsupported action classifier lexicon
  parent  a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a
  5 files, 1606 insertions, 12 deletions       NOT pushed
```

## What was wrong

`app/execution/router.py` reaches its unsupported-verb branch only for a request
`app/execution/classifier.py` has already classified into `ACTION_BEARING_CLASSES`, and
those classes come only from a clause-initial head token in `ACTION_VERBS`. Twenty of the
router's forty-one frozen `UNSUPPORTED_VERBS` were not in `ACTION_VERBS`:

```
backup  build  clear  commit  download  fix  flush  merge  modify  patch
pull    reset  restore  revert  roll  rollback  rotate  scale  upgrade  upload
```

They classified `OTHER`, routed to `NONE` at the class gate and landed on
`Lane.CONVERSATIONAL`, where contract §4.2 permits raw model prose to be the final answer.
Contract §13.1 is normative and requires `UNKNOWN_ACTION` +
`REPORT_CAPABILITY_UNAVAILABLE`. "rollback the last deployment" was an unconstrained model
answer. Task 13B11L measured this at 21/41 and blocked at its own decision gate rather
than patching around it.

## What was done

Twenty verbs added to `ACTION_VERBS` (44 → 64). Fourteen of them also added to
`SENSITIVE_ACTION_VERBS` (26 → 40), per the operator's signed-off split; `backup`,
`build`, `download`, `fix`, `roll` and `rotate` deliberately not. `router.py` untouched.

`app/execution/classifier.py`: **25 insertions, 0 deletions** — thirty-four string
literals and three comment blocks. No executable line changed. Still 13 functions, 5
classes, 0 `try` blocks, and the same seven imports.

The invariant `router.UNSUPPORTED_VERBS ⊆ classifier.ACTION_VERBS` is asserted in
`tests/execution/classifier_lexicon_reconciliation_test.py`, not in the module: importing
the router would create the `classifier → router` dependency the classifier's own
docstring forbids.

## Results, measured through the real `classify → route → lane` chain

| requirement | § | before | after |
|---|---|---|---|
| unsupported verbs → `UNKNOWN_ACTION` + `OPERATIONAL` | 9, 10, 13 | 21/41 | **41/41** |
| sensitive split, the fourteen | 14 | — | **14/14** `R-02` |
| the six not promoted, still action-bearing | 14 | — | **6/6** `R-03` |
| plain-chat controls unchanged | 11 | — | **8/8** |
| additional chat controls (new) | 11 | — | **9/9** |
| supported-action controls unchanged | 12 | — | **8/8** |
| `rollback`/`flush`/`reset`/`upload`/`pull` on `CONVERSATIONAL` | 16 | 5/5 were | **0** |
| nearest-action substitutions, invented targets | 9 | — | **0, 0** |
| full test suite | 17 | 3247 passed, 0 failed | **3464 passed, 0 failed** |
| frozen golden | 18 | 12/20, eight IDs | **12/20, the same eight IDs** |
| legacy probe | 19 | `fc68a0b0…d98291` | **byte-identical** |
| 24 critical files vs `a0cc4d3` | 20 | — | **all `IDENTICAL`** |
| security review | — | — | **30/30** |

Collateral scan over 2,041 distinct strings from all 29 `tests/execution/*_test.py` files
and `evals/golden.jsonl`, run **before** the edit: exactly two moved, both beginning with
`scale`, both `CONVERSATIONAL → OPERATIONAL`. **Zero** moved `OPERATIONAL →
CONVERSATIONAL`, here or anywhere in the security review's probe set.

## Still passive (§15, §21)

The live request path — `server.py`, `main.py`, `brain/router.py`, `brain/llm_client.py`,
`tools/registry.py`, `computer/safety.py`, `resource_manager.py` — imports no
`app.execution` module. `execution.mode` is `legacy`, `hermes_brain` and `hermes_enabled`
are `false`. The legacy `_pending_confirmations` slice in `server.py` is byte-identical
and still owns every real confirmation; `registry.call` still has 4 call sites.
`PrimaryAction.UNKNOWN_ACTION` is a member of both `permissions.NON_EXECUTABLE_ACTIONS`
and `dispatch.NON_DISPATCHABLE_ACTIONS`, and no tool exists for any of the forty-one
verbs. Hermes is at `2237be35…`, clean, 0 processes; no model was run; the diff contains
0 hermes/ollama references.

## Two existing tests changed. Neither was relaxed.

`router_generalization_test.py::test_an_unsupported_verb_the_classifier_does_not_know_stops_at_the_class_gate`
asserted the defect, and its own docstring said "P6 will have to reconcile the two
lists." It is now `…knows_reaches_the_capability_gate` with **four assertions where it had
two**, and the docstring keeps the full history.

`router_non_activation_test.py::test_the_earlier_phase_modules_are_untouched` pins a
sha256 per earlier-phase module. Six of seven digests are unchanged; `classifier.py` is
re-pinned once, with the prior value and the authorizing task in a comment. The assertion
keeps its full strength.

## Flagged to the operator

1. **`CLASSIFIER_VERSION` stays `"1"`** per task §5, although the constant's own comment
   says a lexicon change bumps it. The comment now records the exception, its authority
   and its scope — this repair only. Three existing tests pin `== "1"`. If the rule should
   hold without exception, the follow-up is a version bump plus those three pins, under
   its own authorization. See `LEXICON_RECONCILIATION.md`.
2. **`roll` vs `rollback`.** The frozen split makes `rollback the last deployment`
   `CONFIRMATION_SENSITIVE_ACTION` and `roll back the deployment` `ACTION_REQUEST` — two
   spellings of one intent, two action classes. Applied exactly as frozen and **not**
   smoothed over. Latent: both are operational, both `UNKNOWN_ACTION`, neither executable.
   See `SENSITIVITY_DECISION.md`.
3. **`reset the service` is `AMBIGUOUS_ACTION`, not `CONFIRMATION_SENSITIVE_ACTION`** —
   `"the service"` is a frozen `AMBIGUOUS_REFERENT` and `R-01` outranks `R-02`. This
   satisfies §16 (action-bearing, operational, `UNKNOWN_ACTION`) and honours §8's
   instruction not to force one `RequestClass`. Asserted by name in the tests.

## Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11l-r1-classifier-reconciliation/`, sealed with
`SHA256SUMS` excluding itself, 0 verification failures. The blocked 13B11L bundle was not
modified: re-verified 32/32 OK at entry and at exit, bundle digest `a480f23f…` identical
both times.

## Next

**STOP.** P6 was not implemented and must not be, in this turn.

Recommended: re-run task 13B11L (the P6 obligation engine) from this repaired baseline
`9ace0e3a…`. Its blocking condition is gone — all 41 unsupported verbs now present as
`UNKNOWN_ACTION` on the operational lane, so `REPORT_CAPABILITY_UNAVAILABLE` is
selectable from structured state alone, with no text reparsing. Freeze the obligation
matrix against the *corrected* P3 outputs, not the old ones. The 13B11L analysis remains
evidence and history and must not be overwritten.

Do not enable Hermes. Do not start 13C. Do not wire anything live.
