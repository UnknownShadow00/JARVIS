# Implementation — what was done, in order

Task 13B11L-R2. Tiny metadata repair: one constant and the comment that explains it.

## Order of work

1. **Entry verification (§2).** Production HEAD `9ace0e3a…` exact, parent `a0cc4d3c…`,
   clean, 0 untracked, 11 ahead. `execution.mode=legacy`, both Hermes flags false. Hermes
   `2237be35…`, clean, 0 processes, Ollama idle. R1 bundle re-verified 42/42 OK, digest
   `46c47521…` matching its recorded value. All 34 evidence bundles verified, 0 failures.
2. **Enumerated every version reference** before touching anything — 16 grep hits across
   `classifier.py` and five test files, each read in context and classified as a pin, a
   key-set listing, a hostile-text probe or a derived use.
3. **Froze the pre-bump classification identity (§5), before any edit.** 260 requests ×
   2 context shapes × 16 fields, snapshotted from the running post-R1 classifier and
   hashed, plus a second copy with `classifier_version` stripped. Recorded alongside proof
   the bump had not happened: `classifier.py` still `3a7db133…`, `CLASSIFIER_VERSION = "1"`,
   zero occurrences of the literal `"2"` in the module.
4. **Baseline.** Suite 3464, golden 12/20 eight IDs, probe `fc68a0b0…`, 24 critical file
   hashes, legacy slice `9c43b6f9…`, `registry.call` 4.
5. **Applied the bump.** One anchor, over a file whose digest was checked first. The patch
   script then compared the two files' non-comment lines itself and asserted that exactly
   one differed and that no code line was added or removed — it would have refused
   otherwise.
6. **Added `classifier_version_test.py`** (280 tests) and the compact fixture
   `classifier_version_identity.json`.
7. **Updated the six existing version assertions**, each to a written-out literal.
8. **Re-pinned the one file digest** the constant necessarily moves.
9. **Verified against both frozen tables** — R2's identity snapshot and R1's behaviour
   tables — 0 failures.
10. **Full verification.** Suite 3744/0, golden unchanged, probe byte-identical, 24
    critical files `IDENTICAL`, one non-comment line changed, importer count still 1.
11. **One production commit** `ea0cb32…`, parent `9ace0e3a…`, not pushed.
12. **Evidence bundle sealed**, `SHA256SUMS` excluding itself.

## Decisions worth recording

- **The full 382 KB snapshot stayed in the evidence bundle; the repo got a 24 KB fixture.**
  Committing 11,442 lines of JSON for a one-line metadata repair would have buried the
  change. The fixture carries the corpus, the lexicon digests, the rule table, the digest
  of the versionless snapshot, and eight spelled-out sample rows — so a failure reports a
  readable row diff before it reports "a hash moved", without the repo carrying the bulk.
- **`classifier_lexicon_table.json` was left byte-identical.** It is a verbatim copy of
  R1's sealed `02-frozen-tables.json`, and its `versions_must_remain.classifier: "1"` is a
  true record of what was frozen before R2. Editing it to say `"2"` would have broken that
  relationship and erased the evidence that the version moved. The test asserts the frozen
  `"1"` and the live `"2"` separately instead, which makes the movement visible.
- **`permissions_decisions_test`'s bulk comparison became a per-name map.** `all(value ==
  "1")` would have had to become `all(value == expected[name])` or similar; pinning each
  name individually is simpler and strictly stronger, and it is what the test's own comment
  always said it was for.
- **The one test outside the authorized list is named, not buried.** See
  `REGRESSION_PROOF.md` → "The one test outside §3's boundary".

## Method note

The snapshot-and-hash approach is the same freeze-first method as the earlier phases,
pointed at behaviour instead of at a decision table. It is what turns "the bump changed
nothing" from an assertion into a measurement: the digest either reproduces or it does not,
across 8,320 field comparisons, and no judgement is involved.
