# Lexicon reconciliation — the change, exactly

Task 13B11L-R1. Production parent `a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a`.

## The mechanism that made this a defect

`app/execution/router.py` reaches its unsupported-verb branch only through this gate:

```python
if classification.request_class not in ACTION_BEARING_CLASSES:
    return _result(primary_action=PrimaryAction.NONE,
                   reason=RouteReason.CLASS_NOT_ACTION_BEARING, **common)
```

`ACTION_BEARING_CLASSES` is `{ACTION_REQUEST, CONFIRMATION_SENSITIVE_ACTION,
AMBIGUOUS_ACTION, STATUS_CHECK_REQUEST}`. Only the classifier produces those, and only
from a clause-initial head token found in `ACTION_VERBS`. So a verb the router names in
`UNSUPPORTED_VERBS` but the classifier does not know never reaches
`REQUESTED_OPERATION_HAS_NO_AVAILABLE_TOOL` at all — it falls to `OTHER`, which is a
`DEFAULT_CONVERSATIONAL_CLASS`, and with no operational signals the lane policy returns
`Lane.CONVERSATIONAL`, where contract §4.2 permits raw model prose to be the final
answer. Contract §13.1 is normative and requires `UNKNOWN_ACTION`.

Twenty of the router's forty-one verbs were in that state. Measured through the real
`classify → route → lane` chain: **21/41** correct before, **41/41** after.

## The invariant

```
router.UNSUPPORTED_VERBS  ⊆  classifier.ACTION_VERBS
```

Subset, not equality: `ACTION_VERBS` legitimately holds verbs the router routes to a
supported family (`open`, `launch`, `delete`, `remove`, `deploy`) and verbs it does not
name at all (`make`, `write`, `add`, `pay`, …). It may never *omit* one the router names.

The invariant is asserted in `tests/execution/classifier_lexicon_reconciliation_test.py`,
not inside `classifier.py`. Importing the router to check it would create the
`classifier → router` dependency the classifier's own module docstring forbids, and would
make the lexicon depend on its consumer. The classifier still imports exactly
`__future__`, `re`, `dataclasses`, `enum`, `types`, `typing`, `app.execution.types`.

## ACTION_VERBS — 44 → 64

Added, once each, in one block, alphabetically:

```
backup  build  clear  commit  download  fix  flush  merge  modify  patch
pull    reset  restore  revert  roll  rollback  rotate  scale  upgrade  upload
```

Nothing was removed. Nothing else was added. Verified by set difference against the
lexicon frozen before the edit:

| | before | after | delta |
|---|---|---|---|
| `ACTION_VERBS` | 44 | 64 | +20, −0 |
| `SENSITIVE_ACTION_VERBS` | 26 | 40 | +14, −0 |
| `STATUS_VERBS` | 13 | 13 | unchanged |
| `router.UNSUPPORTED_VERBS` | 41 | 41 | unchanged |
| `UNSUPPORTED_VERBS ∩ ACTION_VERBS` | 21 | 41 | +20 |

Shape invariants that still hold: `SENSITIVE_ACTION_VERBS < ACTION_VERBS` (strict
subset), `ACTION_VERBS ∩ STATUS_VERBS = ∅`, every member lowercase, both frozensets
immutable through the public surface.

## What was deliberately NOT changed

`CLASSIFIER_VERSION`, `ROUTER_VERSION` and `LANE_POLICY_VERSION` all remain `"1"`.
Classifier precedence (11 rules, `R-01` … `R-11`, same order), the reason vocabulary
(11 members), the router grammar, the router's unsupported-verb set and the lane policy
are untouched. No rule was added, no branch was added, no function or class was added:
`classifier.py` still has 13 functions, 5 classes and 0 `try` blocks.

### The one honest tension

`CLASSIFIER_VERSION`'s own comment says "Any change to the lexicon, the rules or their
order bumps this." Task section 5 explicitly forbids changing the version. The version is
therefore held at `"1"` and the comment now records the exception, its authority and its
scope — it stands for this repair only. **This is flagged for the operator.** Three
existing tests pin `CLASSIFIER_VERSION == "1"`; bumping it would have failed them and
would have been a change task section 5 forbids. If the operator would rather the rule
held without exception, the follow-up is a version bump plus those three pins, and it is
a separate authorization.

## Diff shape

`app/execution/classifier.py`: **25 insertions, 0 deletions**. Twenty string literals,
fourteen string literals, and three comment blocks. No executable line changed.
