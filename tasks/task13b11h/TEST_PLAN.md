# Task 13B11H — Test Plan and Results

548 new tests, all passing. Suite 1565 → 2113 passed, 11 deselected, 0 failures.
`tests/execution` 1148 → 1692.

## 1. `router_test.py` — 365 tests

| Block | What it proves |
|---|---|
| C4 regression corpus | all 67 frozen rows, transcribed by hand, each asserting the request class **and** the action, intent, target and resolution; plus coverage of every `PrimaryAction` and every `ReportingIntent`, and that no row puts a real action on a non-action-bearing class |
| lexicon and grammar | the five supported operations; outcomes are not operations and the two sets partition the enum; 41 unsupported verbs; no verb in two families; every lexicon a `frozenset`; the four action-bearing classes; clause segmentation on words, punctuation and newline; `and then` consumed as one connector |
| clause kinds | `REPORTING` / `NEGATED` / `ACTION` / `NONE` decided in that frozen order; a reporting or negated clause containing an action verb is still reporting or negated; all 15 polite prefixes; a verb that is not clause-initial is not an action |
| per-action extraction | `OPEN_APP` names with case and noise variants; four URL shapes; `DEPLOY` with `to`/`onto`/bare and a non-environment operand; `DELETE_PATH` with absolute, `~`, trailing-slash, non-path and two-path operands; the database object and a non-database read; **every one of the 41 unsupported verbs**; no near-miss verb reaches a supported action |
| target invention | every deictic operand unresolved; an unresolved target keeps the user's words; no default ever substituted |
| raw preservation | the canonicalizer's `vs code` alias not applied; `DEPLOY` keeps the user's capitalization; `raw_target` keeps the pre-strip operand; `~` never expanded |
| reporting intent | all six values via ten tails; no anchor means `NONE`; the family precedence is frozen and a two-family tail resolves to the earlier one; a reporting clause adds no action, never becomes the target; **16 compound action × tail combinations**; intent survives a refused action |
| multi-action | **all 25 ordered pairs** of the five supported actions; a multi-action result carries nothing executable; the first action is never selected; the same action twice is still multi-action; one supported plus one unsupported is *not* multi-action; three actions |
| classifier boundary | all nine classes against one action-bearing text; the supplied class beats the text; `classify()` is never called; a non-bearing class still reports the reporting intent |
| capability | true only for a supported action; an action outside the caller's set becomes `UNKNOWN_ACTION`; a narrowed set turns a pair into a single action; outcomes and malformed sets are refused |
| case, whitespace, punctuation | seven spellings of one request; segmentation trims but does not collapse; newline separates clauses |
| injection resistance | six injection shapes leave version, lexicon, class set and enums unchanged; a JSON body naming an action is not deserialized; an injected tail does not survive the leading clause; **the connector case, asserted at both layers** (see §4) |
| invalid input | eight non-string types; **every `RequestClass`, `PrimaryAction` and `ReportingIntent` member passed as the request**; empty and whitespace; five non-`Classification` values plus a duck-typed look-alike; five non-`RouterContext` values |
| determinism and immutability | every corpus row repeated; results and nested clause analyses frozen; 200 calls accumulate no state; the context is not mutated |
| serialization | JSON round-trip; the version on every result; the reason always a frozen member |
| types reused | `PrimaryAction`, `ReportingIntent` and `RequestClass` are the objects from `app.execution.types`; the module defines exactly two enums of its own; every pattern is a module-level literal; no pattern is built from a variable |

## 2. `router_generalization_test.py` — 46 tests

41 unseen requests (ids U01-U42, U21 absent — a numbering gap, not a dropped row) written
after the rules were frozen, covering every `PrimaryAction`, every
`ReportingIntent`, multi-action, unknown action, missing target, declarative and explanatory
classes, a status question with no status verb, and two injection strings. Every expectation was
predicted from the frozen documents before the file was run; **all 42 were correct on the first
execution**, and no rule, lexicon entry, pattern or rank was changed afterwards. Plus coverage,
disjointness from the C4 corpus, and two tests pinning documented v1 limitations so they cannot
drift silently.

## 3. `router_non_activation_test.py` — 137 tests

| Block | What it proves |
|---|---|
| purity | imports are exactly `__future__`, `re`, `dataclasses`, `enum`, `typing`, `app.execution.classifier`, `app.execution.types`; 34 forbidden constructs absent from executable code; the single `object.__setattr__` is the capability-set normalization; no module-level mutable state; no `global`/`nonlocal`; an audit-hook sweep over 20 repetitions fires no file, socket or subprocess event; the signature needs no settings or session |
| no model, no fuzzy | 19 model and fuzzy tokens absent; the legacy LLM router not imported; every pattern compiled from a literal at module level; six near-miss verbs reach no action |
| no tool reference | 11 tool-shaped names absent, including the five C4 diagnostic tool names; the 14 result fields exactly as planned; 16 execution and policy field names absent from both records; no field value is callable; the result is plain JSON data; a sensitive route decides nothing; nine permission/confirmation/lane/provenance types neither named nor imported |
| phase non-interaction | eight cross-phase tokens absent from code; routing never calls the audit writer, the lane policy, the canonicalizer or `classify()` — each monkeypatched to raise; routing creates no provenance |
| deferred decisions | audit schema still 3, `lane` still not among the 17 fields, `ProvenanceSource` still 8 members with no `TIMEOUT`; the seven earlier execution modules asserted byte-identical by hash |
| no live wiring | no production module imports the router; **twelve** router symbols each with zero references outside the module; ten named live-path modules mention neither `execution.router` nor `RouteResult`; the legacy router asserted byte-identical by hash and still holding `_classify_with_ollama`; the execution package exports nothing new; the only `app.execution` reference outside the package is still `app/config.py:14` |

Note on method: the forbidden-token scans read the module with comments and string literals
removed. The docstring legitimately *names* the phases the router refuses to touch — "no
embedding, no similarity", "the canonicalizer's job" — so a scan over the raw file would flag the
very sentences that promise the behaviour.

## 4. Runtime proofs outside pytest

`11-purity-and-no-execution-object.txt` routes all 108 corpus and generalization requests under a
CPython audit hook watching file opens, sockets, subprocesses, network, dynamic import,
`exec`/`compile` and filesystem mutation: **no sensitive event**, 8/8 actions and 6/6 intents
exercised. 21 sweeps identical; 500 repeated calls produce one distinct output; the context is
unmodified. Every unresolved target is shown to appear verbatim in its request. Every malformed
input is refused, including each `str`-subclassing enum member. The injection battery leaves
version, lexicon, class set and enums unchanged.

`13-static-review-and-hermes-non-use.txt` §2 additionally times the three group-quantified
patterns against 2,000-iteration hostile inputs: each completes in 0.0002 s.

## 5. Non-regression

| Check | Before | After |
|---|---|---|
| `pytest -q` | 1565 passed / 11 deselected / 0 failed | 2113 passed / 11 deselected / 0 failed |
| `tests/execution` | 1148 | 1692 |
| golden | 12/20, eight named failures | 12/20, same eight |
| legacy probe | `fc68a0b0…` | `fc68a0b0…`, byte-identical |
| 22 critical files | recorded in `03` | identical in `13` §7 |

The eight golden failures are unchanged in identity: `calendar-move-event-002`,
`habit-status-001`, `habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
