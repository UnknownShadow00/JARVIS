# Why the version moved, and what each value means

## The defect

`CLASSIFIER_VERSION`'s own contract, written when the module was frozen:

> The rule-set version, not the contract version: Agent Execution Contract v1 is
> unchanged. **Any change to the lexicon, the rules or their order bumps this.**

Task 13B11L-R1 changed the lexicon — `ACTION_VERBS` 44 → 64, `SENSITIVE_ACTION_VERBS`
26 → 40 — and held the version at `"1"` by explicit operator instruction (R1 task §5).
R1 flagged the tension rather than resolving it, under "The one honest tension".

The result was an **audit and reproducibility defect**, not a behavioural one. One
version name identified two different rule sets:

| | `ACTION_VERBS` | `SENSITIVE_ACTION_VERBS` | unsupported verbs covered | reported version |
|---|---|---|---|---|
| pre-R1 | 44 | 26 | 21/41 | `"1"` |
| post-R1, pre-R2 | 64 | 40 | 41/41 | `"1"` ← the defect |
| post-R2 | 64 | 40 | 41/41 | `"2"` |

A `Classification` record carries `classifier_version` into everything downstream. With
both rule sets reporting `"1"`, an audited classification could not be replayed against
the rules that produced it, and a disagreement between two records would have looked
like nondeterminism rather than a version difference.

## The assignment

```
"1"  the original frozen rule set: 44 ACTION_VERBS, 26 SENSITIVE_ACTION_VERBS.
     Twenty verbs router.UNSUPPORTED_VERBS names were not action-bearing, so they
     never reached UNKNOWN_ACTION.
"2"  the rule set 13B11L-R1 left: 64 and 40, every router unsupported verb covered.
```

**`"1"` keeps its original meaning.** It was not redefined to mean the repaired rules.
That is the point: a record written before R1 still names the rule set that produced it.
The window in which `"1"` was reported by the repaired classifier is the interval between
commits `9ace0e3` and `ea0cb32` — on this machine only, never pushed, with
`execution.mode=legacy` and nothing wired, so no audit record was ever emitted under it.

## What was deliberately not bumped

`ROUTER_VERSION`, `LANE_POLICY_VERSION`, `CANONICALIZATION_VERSION`,
`PERMISSION_POLICY_VERSION` — all still `"1"`. None of their inputs changed. The Agent
Execution Contract version is likewise untouched: this is a rule-set identifier, not a
contract identifier, and the contract's §5.1 derivation is exactly what it was.

`tests/execution/permissions_decisions_test.py::test_d10_version_is_independent_of_the_other_version_constants`
existed precisely to record that these five are separate names "so that bumping one does
not silently bump another." It previously asserted `all(value == "1")`, which could only
anticipate the claim. It now pins each name individually, and the classifier standing at
`"2"` while the other four stand at `"1"` **demonstrates** it.

## Why this was not folded into R1

It could not be: R1's task §5 explicitly forbade changing the classifier version, and
three tests pinned `== "1"`. Bumping there would have been an unauthorized change. The
correct sequence was to make the semantic repair under its own authorization, flag the
version tension in the report, and let the operator decide — which is what happened.

## Cost of the split

One extra commit, and a one-commit window where the repaired rules reported `"1"`. The
window is documented above and was never observable outside this machine. The alternative
— a silent bump inside R1 — would have put an unauthorized change in a commit whose whole
value was that its boundary was exact.
