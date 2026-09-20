# Regression tests

## Counts

| | before | after |
|---|---|---|
| full suite | 3247 passed, 11 deselected, 0 failed | **3464 passed, 11 deselected, 0 failed** |
| `tests/execution` | — | 3047 passed |
| new file `classifier_lexicon_reconciliation_test.py` | did not exist | 177 passed |
| all ten non-activation files | — | 665 passed |
| golden | 12/20, eight named IDs | **12/20, the same eight IDs** |
| legacy probe digest | `fc68a0b0…d98291` | **`fc68a0b0…d98291`, byte-identical** |

`+217` = 177 new tests, plus 40 from two existing parametrizations in
`classifier_test.py` that iterate `ACTION_VERBS` and therefore expanded 44 → 64 rows
each. Those two were already written to cover the whole lexicon; they needed no edit and
now cover the twenty new verbs automatically.

## What the new file asserts

`tests/execution/classifier_lexicon_reconciliation_test.py`, 177 tests, driven by
`classifier_lexicon_table.json` — copied verbatim from the table frozen *before* the
edit, in the repo's existing convention (`dispatch_matrix.json`,
`permissions_policy_table.json`, `confirmation_transition_table.json`). No expectation in
the file is re-derived from the code under test.

1. the frozen table records the pre-repair parent and the 44/26/41 counts
2. the operator decision is 20 split 14 + 6, disjoint, exhaustive
3. `ACTION_VERBS` gained exactly the twenty, lost nothing, is 64
4. `SENSITIVE_ACTION_VERBS` gained exactly the fourteen, lost nothing, is 40
5. the six withheld verbs are action-bearing and not sensitive
6. every prior shape invariant still holds (strict subset, disjoint from `STATUS_VERBS`, lowercase, immutable, frozenset)
7. **`UNSUPPORTED_VERBS ⊆ ACTION_VERBS`** — the repair's reason for existing
8. the router's own set was not touched
9. all 41 verbs reach `UNKNOWN_ACTION` on `OPERATIONAL`, per-verb, against the frozen class
10. the sweep moved 21/41 → 41/41
11. no verb gets a nearest supported action, a resolved target or `capability_available`
12. the 14 sensitive classify `R-02`, the 6 ordinary classify `R-03`
13. a bare repaired verb is still `AMBIGUOUS_ACTION` (`R-01` still outranks `R-02`/`R-03`)
14. 8 chat controls, 9 extra chat controls, 8 supported-action controls — full frozen signature unchanged, seven fields each
15. the five §16 security prompts cannot reach `CONVERSATIONAL`, and are still not executable
16. `reset the service` is `AMBIGUOUS_ACTION` by precedence, asserted by name
17. no version moved; the rule table, its order and all three reason vocabularies are unchanged
18. the classifier's parsed imports are unchanged, and it names no router symbol in code

## Controls

Sections 11 and 12 asked for the blocked review's controls to be repeated. They were
taken verbatim from that review's `scripts/fixsim.py` (`CHAT`, `CONTROL`), measured on
the unpatched classifier, frozen, and re-measured after. **8/8 and 8/8 unchanged**, on
the full seven-field signature rather than on the lane alone.

Section 11 also asked for additional controls using the repaired words in non-action or
explanatory contexts. Nine were added. Each exercises one branch of the *existing*
grammar that already makes the distinction — the classifier only ever tests the
clause-initial head token, so an explanatory opener is settled by `R-08` before any verb
lexicon is consulted:

| control | branch | result |
|---|---|---|
| `what is a rollback` | `R-08` `^what (is\|are\|does\|do\|did)` | `GENERAL_EXPLANATION` / `CONVERSATIONAL` |
| `what does flush mean` | same | same |
| `why did the build fail` | `R-08` `^why` | same |
| `how does a rolling upgrade work` | `R-08` `^how` | same |
| `explain how a merge works` | `R-08` `^explain` | same |
| `describe the patch process` | `R-08` `^describe` | same |
| `define scale in kubernetes` | `R-08` `^define` | same |
| `tell me about the upgrade path` | `R-08` `^tell me (about\|what)` | same |
| `which upgrade path do you recommend` | `R-11` `no_matching_rule` | `OTHER` / `CONVERSATIONAL` |

Each of the nine was *predicted* from the frozen rules in the freeze script and then
measured; all nine predictions matched, before and after. That is the anti-overfitting
evidence: they are one per grammar branch, not nine tuned sentences, and no rule was
added for any of them.

## Collateral scan — run before the edit

2,041 distinct strings harvested from all 29 `tests/execution/*_test.py` files and
`evals/golden.jsonl`, measured through `classify → route → lane` with the production
lexicon and again with both frozensets rebound in a throwaway process.

**Exactly two strings moved**, both beginning with `scale`, both
`CONVERSATIONAL → OPERATIONAL`. Zero moved `OPERATIONAL → CONVERSATIONAL`. Every mover's
head token was one of the twenty.

## The two existing tests that changed, and why neither was relaxed

**`router_generalization_test.py::test_an_unsupported_verb_the_classifier_does_not_know_stops_at_the_class_gate`**
asserted the defect itself. Its own docstring said "P6 will have to reconcile the two
lists." It is now
`test_an_unsupported_verb_the_classifier_knows_reaches_the_capability_gate`, asserting
`UNKNOWN_ACTION` + `requested_operation_has_no_available_tool` +
`capability_available is False` + `target is None` — **four assertions where there were
two** — and its docstring preserves the full history of what it used to record.

**`router_non_activation_test.py::test_the_earlier_phase_modules_are_untouched`** pins a
sha256 per earlier-phase module. Six of the seven digests are unchanged. The seventh,
`classifier.py`, is re-pinned to the new value with the prior value kept in a comment
naming the authorizing task. The assertion keeps its full strength: an unauthorized edit
to any of the seven still fails it. Nothing was widened, skipped, or replaced with a
weaker check. This is the only prior-phase pin this repair touches, and it is touched
once.
