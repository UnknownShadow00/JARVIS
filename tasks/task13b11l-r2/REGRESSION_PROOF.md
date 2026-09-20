# Proof that nothing but the version moved

## The method

The standing method is to freeze the expectation before the edit. Here the expectation is
"the classifier's answers", so it was **snapshotted from running production** at
`9ace0e3` while `CLASSIFIER_VERSION` was still `"1"`, and hashed.

- **260 distinct requests** — every probe R1 froze (the 41-verb sweep, the 5 security
  prompts, all 25 controls), every one of the 64 action verbs bare and with two different
  targets, every status verb, every ambiguous referent, the hostile-text probes, and the
  serialization examples the suite pins.
- **× 2 context shapes** — `NO_CONTEXT` and `ClassifierContext({"port",
  "deployment_target"})`, because rules R-05/R-06/R-07 branch on the caller's key set.
- **= 520 rows, 16 fields each**: the 5 classification fields plus `primary_action`,
  `route_reason`, `reporting_intent`, `target`, `raw_target`, `target_resolved`,
  `multi_action`, `capability_available`, `router_version`, `lane`, `lane_reasons`.

Two files were written before the edit and hashed:

```
02-pre-bump-identity.json               fd5ff491…   the full snapshot (382 KB)
02-pre-bump-identity-versionless.json   2b94f79f…   the same, classifier_version removed
```

## The result

After the bump, the snapshot was recomputed and the version field removed again:

```
versionless digest before   2b94f79f187d7daa98c2517a436755dd171b4403effe48bd7d15d3c416672a20
versionless digest after    2b94f79f187d7daa98c2517a436755dd171b4403effe48bd7d15d3c416672a20
byte-identical              True
rows whose non-version fields moved   0 of 520
rows now reporting version "2"        520 of 520
```

That is §5 discharged: for every request in the corpus, in both context shapes, across all
16 fields, the only difference is `classifier_version` `"1"` → `"2"`.

## Section 6 — the lexicon did not move

Each set hashed before and after:

| set | count | sha256 | |
|---|---|---|---|
| `ACTION_VERBS` | 64 | `604c12a7…` | identical |
| `SENSITIVE_ACTION_VERBS` | 40 | `35d691ac…` | identical |
| `STATUS_VERBS` | 13 | `c36eddbf…` | identical |
| `router.UNSUPPORTED_VERBS` | 41 | `a3a1a9bc…` | identical |

Plus the full sorted member lists compared element-wise, the 11-row rule table compared as
serialized mappings, and the 11-member reason vocabulary compared in order. No additions,
no removals.

## Section 7 — the P3 reconciliation still holds

41/41 router unsupported verbs reach `UNKNOWN_ACTION` on `Lane.OPERATIONAL`, each with the
exact `RequestClass` R1 froze. `UNSUPPORTED_VERBS ⊆ ACTION_VERBS` still true.

## Section 8 — controls

All three R1 families re-measured on the full seven-field signature against R1's sealed
table: **chat 8/8, extra chat 9/9, supported-action 8/8 identical.** None of the five named
security prompts reaches `CONVERSATIONAL`.

## Section 14 — only the version literal changed

`classifier.py` has 319 non-comment lines before and after. Comparing them pairwise:

```
- CLASSIFIER_VERSION = "1"
+ CLASSIFIER_VERSION = "2"
total differing non-comment lines: 1
```

The patch script asserted this itself and would have refused otherwise. The other 16
inserted / 6 deleted lines in the diffstat are the comment block explaining what `"1"` and
`"2"` mean. All 23 other critical files plus `config.yaml`, `app/config.py` and production's
`CLAUDE.md` are byte-identical to `9ace0e3`.

## Sections 9, 10, 11 — suite, golden, probe

| | R1 baseline | after R2 |
|---|---|---|
| full suite | 3464 passed, 11 deselected, 0 failed | **3744 passed, 11 deselected, 0 failed** |
| new `classifier_version_test.py` | did not exist | 280 passed |
| ten non-activation files | 665 | **665** |
| golden | 12/20, eight IDs | **12/20, the same eight IDs** |
| legacy probe | `fc68a0b0…` | **byte-identical**, `cmp` clean |

`+280` is entirely the new file. No existing test count changed.

## Section 12 — no version assertion was weakened

Six assertions moved. Every one writes the literal `"2"`; none accepts either value, none
was removed, and none derives the expected value from the constant under test.

| file | before | after |
|---|---|---|
| `classifier_test.py` (dedicated) | `== "1"` | `== "2"`, plus a comment naming both rule sets |
| `classifier_test.py` (injection test) | `== "1"` | `== "2"` |
| `classifier_test.py` (serialization) | `"classifier_version": "1"` | `"classifier_version": "2"` |
| `classifier_non_activation_test.py` | `== "1"` | `== "2"` |
| `classifier_lexicon_reconciliation_test.py` | `== FROZEN[…] == "1"` | frozen table keeps `"1"` as its pre-R2 record; the constant is pinned to the literal `"2"` separately, so the movement is visible rather than edited out |
| `permissions_decisions_test.py` | `all(value == "1")` | each of the five names pinned individually — **strictly stronger**, and now a demonstration rather than an anticipation |

`classifier_version_test.py::test_the_classifier_rule_set_version_is_two` is the
independent literal §12 requires.

## The one test outside §3's boundary

`router_non_activation_test.py::test_the_earlier_phase_modules_are_untouched` pins a
sha256 per earlier-phase module. It is not a version assertion, so it is strictly outside
§3's authorized list — but `CLASSIFIER_VERSION` lives in the file it hashes, so the digest
cannot stay. It was treated exactly as R1 treated it: the other six digests and the
assertion itself are untouched, and the comment now carries the full chain
`c554b34a…` → `3a7db133…` → `02534d68…` with the authorizing task for each. The assertion
keeps full strength — an unauthorized edit to any of the seven still fails it.
