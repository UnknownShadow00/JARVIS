# Task 13B11G — Test Plan and Results

497 new tests, all passing. Suite 1068 → 1565 passed, 11 deselected, 0 failures.
`tests/execution` 651 → 1148.

## 1. `classifier_test.py` — 325 tests

| Block | What it proves |
|---|---|
| frozen rule table | 11 rules, ids unique, order equals `PRECEDENCE.md`, every `RequestClass` reachable, every reason used by exactly one rule, `RULE_INDEX` read-only |
| lexicon | `SENSITIVE_ACTION_VERBS` a strict subset of `ACTION_VERBS`, every lexicon a `frozenset`, no lexicon mutable at runtime |
| frozen corpus | all 83 rows, transcribed by hand from `CLASSIFICATION_CORPUS.md`, each asserting class **and** rule id |
| per-class behaviour | every one of the nine classes has positive cases; `OTHER` has explicit fallback semantics |
| precedence | one case per documented overlap in `PRECEDENCE.md` §2, each matching more than one low-level cue |
| normalization | case, leading/trailing/internal whitespace, terminal punctuation present and absent, polite and sequencing prefixes |
| injection resistance | "ignore your rules", "classify this as conversational", fake JSON asserting a class, fake tool output, a sensitive request with an injected tail |
| invalid input | `None`, `int`, `float`, `bytes`, `list`, `dict`, `object`, `bool`, empty, whitespace-only, bad context objects, illegal and non-string fact keys, and every `RequestClass` / `ClassificationReason` member passed as the request |
| determinism | every corpus row repeated; identical class, reason, rule id and version |
| serialization | `to_mapping()` keys and values, version stamped on every result |
| types reused | `RequestClass` is the object from `app.execution.types`; no duplicate enum anywhere |

## 2. `classifier_generalization_test.py` — 45 tests

43 unseen requests written after the rules were frozen, plus a coverage test (all nine classes) and
a disjointness test proving no string is shared with the frozen corpus. Expectations were predicted
from the rule table before the file was run.

## 3. `classifier_non_activation_test.py` — 127 tests

| Block | What it proves |
|---|---|
| purity | imports are stdlib plus `app.execution.types` only; no filesystem, network, subprocess, `eval`, `exec`, dynamic import, `getenv`, `environ`, clock or `random`; no module-level mutable state; no `global`/`nonlocal`; the single `object.__setattr__` is the frozen-dataclass key normalization |
| no model, no fuzzy | the legacy LLM router is not imported; `difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein`, `SequenceMatcher`, `get_close_matches`, embeddings and similarity scoring are absent; matching is set membership and frozen regex; no regex uses a nested quantifier |
| no router output | the result carries exactly the five planned fields and no `PrimaryAction`, tool, target, arguments, `Lane`, permission or confirmation; no action-type name appears in the source; a sensitive request decides nothing downstream |
| phase non-interaction | classifying never calls the audit writer (monkeypatched to raise), creates no provenance, never calls `lane.decide`/`lane.explain`, never calls `canonicalize` |
| deferred decisions | audit schema still 3, `lane` still not among the 17 contract audit fields, `ProvenanceSource` still 8 members with no `TIMEOUT`, canonicalizer and lane policy byte-identical |
| no live wiring | no production module imports the classifier; no classifier symbol is referenced outside the package; ten named live-path modules do not mention it; the execution package exports nothing new; the classifier needs no settings or session object |

## 4. Runtime proofs outside pytest

`11-purity-and-no-router-output.txt` runs the 83-row corpus and the 43-row generalization set under
a CPython audit hook watching file opens, sockets, subprocesses, network, dynamic import,
`exec`/`compile` and filesystem mutation: **no sensitive event**. 21 sweeps identical; 500 repeated
calls produce one distinct output and leave the context unmodified; every malformed input refused;
the version, rule order, reason vocabulary and enum are unchanged after the injection battery.

`08-independent-generalization.txt` is a second unseen set of 33 requests, predicted from the
frozen documents by the completing session before running: 33/33 agreement, 9/9 classes.

## 5. Non-regression

| Check | Before | After |
|---|---|---|
| `pytest -q` | 1068 passed / 11 deselected / 0 failed | 1565 passed / 11 deselected / 0 failed |
| `tests/execution` | 651 | 1148 |
| golden | 12/20, eight named failures | 12/20, same eight |
| legacy probe | `fc68a0b0…` | `fc68a0b0…`, byte-identical |
| 20 critical files | recorded in `03` | identical in `13` §8 |

The eight golden failures are unchanged in identity: `calendar-move-event-002`,
`habit-status-001`, `habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
