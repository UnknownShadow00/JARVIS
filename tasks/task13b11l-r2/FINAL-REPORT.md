# Task 13B11L-R2 — classifier version reconciliation

## Verdict

**JARVIS CLASSIFIER VERSION RECONCILIATION IMPLEMENTED**

```
ea0cb32040a0e24d0b80de706929086b6dd36b66   fix: bump classifier rule version after lexicon repair
  parent  9ace0e3a0855708d992467a179d08f6affef43e1
  8 files, 1141 insertions, 22 deletions       NOT pushed
```

## What was wrong

R1 changed the classifier's frozen lexicon (44 → 64 action verbs, 26 → 40 sensitive) and
left `CLASSIFIER_VERSION` at `"1"` by operator instruction, against the constant's own
stated contract. One version name then identified two different rule sets, so an audited
classification could not be replayed against the rules that produced it. Behaviour was
correct; identity was not.

## What was done

```
- CLASSIFIER_VERSION = "1"
+ CLASSIFIER_VERSION = "2"
```

`"1"` keeps its original meaning — the pre-R1 44-verb rule set. `"2"` names the reconciled
one. Of **319 non-comment lines** in `classifier.py`, **exactly one** differs from
`9ace0e3`; the rest of the diff is the comment block defining both values. The patch
script asserted that itself and would have refused otherwise.

## Results

| requirement | § | result |
|---|---|---|
| version set to `"2"` | 4 | **done**; router, lane, canonicalization, permission all still `"1"` |
| exactly one version moved | 4 | **1 of 5** |
| classification output unchanged apart from the version | 5 | **520 rows × 16 fields byte-identical**, 0 non-version fields moved |
| lexicon unchanged | 6 | 4 set digests **identical**; rule table and reason vocabulary identical |
| 41-verb P3 sweep | 7 | **41/41** `UNKNOWN_ACTION` + `OPERATIONAL` |
| chat / extra chat / supported controls | 8 | **8/8, 9/9, 8/8** identical to R1 |
| golden | 9 | **12/20, the same eight IDs** |
| legacy probe | 10 | **byte-identical**, `fc68a0b0…d98291` |
| full suite | 11 | 3464 → **3744 passed, 11 deselected, 0 failed** |
| version assertions updated, none weakened | 12 | **6 updated**, each a written-out literal; one strengthened |
| serialization carries `"2"`, round-trip unchanged | 13 | **done**, key set unchanged, 1 distinct serialization over 50 runs |
| every other production module byte-identical | 14 | **24/24 IDENTICAL** |
| Hermes unused | — | `2237be35…` clean, 0 processes, 0 Ollama, 0 refs in the diff |

**The §5 proof is a measurement, not an assertion.** 260 requests × 2 context shapes × 16
fields were snapshotted from production *before* the bump and hashed. Recomputed after,
with `classifier_version` removed, the snapshot reproduces byte-for-byte
(`2b94f79f…`) across 8,320 field comparisons.

## Test changes

Six version assertions moved, each writing the literal `"2"`. None accepts either value,
none was deleted, none derives the expectation from the constant under test.
`permissions_decisions_test::test_d10_version_is_independent_of_the_other_version_constants`
was **strengthened** — it previously asserted `all(value == "1")`, which could only
anticipate its own claim; it now pins each of the five names individually, and the
classifier at `"2"` beside four constants at `"1"` demonstrates the independence it was
written to record.

`classifier_lexicon_table.json` was deliberately **not** edited: it is a verbatim copy of
R1's sealed frozen tables, and its `"1"` is a true record of the pre-R2 state. The test
asserts the frozen `"1"` and the live `"2"` separately, so the movement stays visible.

**One test sits outside §3's authorized list**, and is named rather than buried:
`router_non_activation_test::test_the_earlier_phase_modules_are_untouched` pins a sha256
per module, and the constant lives in the file it hashes. Treated exactly as R1 treated
it — six digests and the assertion untouched, the comment now carrying the full chain
`c554b34a…` → `3a7db133…` → `02534d68…` with each authorizing task.

## Still passive

`execution.mode` is `legacy`, both Hermes flags false. The live request path imports no
`app.execution` module; `app/execution/router.py` is still the classifier's only importer.
Legacy confirmation slice `9c43b6f9…` unchanged, `registry.call` still 4 call sites,
`app/execution/obligations.py` still absent.

## Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11l-r2-classifier-version/`, sealed with
`SHA256SUMS` excluding itself, 0 failures. The R1 bundle was verified unmodified at entry
and at exit (42/42 OK, digest `46c47521…` both times).

## Next

**STOP.** P6 was not implemented and must not be in this turn.

Re-run task **13B11L** (the P6 obligation engine) from baseline `ea0cb32…`. Its blocking
condition was cleared by R1: all 41 router-unsupported verbs present as `UNKNOWN_ACTION`
on the operational lane, so `REPORT_CAPABILITY_UNAVAILABLE` is selectable from structured
state alone. Freeze the obligation matrix against the corrected P3 outputs. The classifier
now reports rule-set version `"2"`, which is what any P6 audit record should carry. The old
blocked 13B11L analysis remains history and must not be overwritten.

Do not enable Hermes. Do not start 13C. Do not wire anything live.
