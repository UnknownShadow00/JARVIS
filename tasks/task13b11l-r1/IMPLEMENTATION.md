# Implementation — what was done, in order

Task 13B11L-R1. Small production repair, P3 lexicon only. No P6, no wiring, no Hermes.

## Order of work

1. **Entry verification (§3).** Production HEAD `a0cc4d3c…`, clean, 0 untracked, 10 ahead
   of origin. `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false`.
   Hermes `2237be35…`, clean, 0 processes. Blocked 13B11L produced no production commit
   (`app/execution/obligations.py` absent, 0 commits touching `app/execution` since
   `a0cc4d3c`). All twelve prior 13B11 evidence bundles re-verified: 401 files, 0 failures.
2. **Read the frozen modules.** `classifier.py`, `router.py`, `lane.py` read in full, and
   the mechanism of the defect traced through `ACTION_BEARING_CLASSES` before anything
   was written.
3. **Freeze the decision tables (§6, §7, §8, §11–§14, §16), before any edit.** Expected
   values derived from the operator decision and from the frozen rules restated
   independently — not produced by running repaired code. Sealed with sha256 alongside a
   proof the repair did not yet exist (`classifier.py` at `c554b34a…`, `ACTION_VERBS` 44,
   coverage 21/41, reconciliation test absent).
4. **Baseline.** Suite 3247, golden 12/20 with the eight named IDs, legacy probe
   `fc68a0b0…`, 24 critical files hashed, legacy confirmation slice `9c43b6f9…`,
   `registry.call` 4 call sites.
5. **Collateral scan, read-only.** 2,041 strings from every execution test file and the
   golden set, measured before and after with the frozensets rebound in a throwaway
   process that wrote nothing and asserted its own restore. Exactly two movers, both
   `scale`, both toward `OPERATIONAL`.
6. **Apply the repair.** Exact-string replacement over three anchors, refusing unless
   each appeared exactly once and the file matched its expected digest. 25 insertions,
   0 deletions.
7. **Verify against the pre-edit tables.** 41/41 sweep, 14/14 sensitive, 6/6 not
   promoted, 8/8 + 9/9 + 8/8 controls unchanged, 5/5 security rows, 0 failures.
8. **Add tests.** `classifier_lexicon_reconciliation_test.py` (177) plus
   `classifier_lexicon_table.json`, the table copied verbatim from the frozen JSON.
9. **Update the two existing tests the repair legitimately invalidates** — see
   `REGRESSION_TESTS.md`. Neither relaxed.
10. **Full verification.** Suite 3464/0, golden 12/20 same eight, probe byte-identical,
    24 critical files `IDENTICAL`, legacy slice unchanged, `registry.call` still 4.
11. **No-live-wiring proof over parsed imports**, not greps.
12. **Security review**, 30/30.
13. **One production commit**, parent `a0cc4d3c…`, not pushed.
14. **Evidence bundle sealed**, `SHA256SUMS` excluding itself.

## Method notes worth keeping

- The standing method held: **freeze and hash the table before writing the change.** All
  nine extra controls were *predicted* from the frozen rules and then measured; nine of
  nine matched. A prediction that matches is worth more than a measurement that is
  recorded as the expectation.
- **A read-only collateral scan before the edit turned a 3,247-test gamble into a
  two-string question.** It found both existing tests that would move, before either
  failed, and bounded the blast radius to `scale`.
- Two of my own scans were wrong before the code was: a substring scan for `requests` hit
  the classifier's prose, and `grep 'execution.classifier'` matched a path inside a
  comment through the regex dot. Both were rewritten over the AST. This is the 13B10B and
  13B10D lesson again — **scan the parsed unit, not the characters.** The evidence records
  the corrected measurement and says why the first was wrong.
- `pgrep -af hermes` matched the invoking `bash -c` wrapper and reported 1 process where
  there were 0. Counted by an explicit pattern instead and verified by hand.

## Deviation flagged to the operator

`CLASSIFIER_VERSION` stays `"1"` per task section 5, although the constant's own comment
says a lexicon change bumps it. See `LEXICON_RECONCILIATION.md` → "The one honest
tension". Nothing was weakened to accommodate this; the comment records the exception and
its scope.
