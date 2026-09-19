# TASK 13B11H — FINAL REPORT
## Deterministic action router foundation (production phase P3, fourth and final unit)

## 1. Verdict

**JARVIS ACTION ROUTER FOUNDATION IMPLEMENTED**

The contract §5.2 routing derivation — primary action, reporting intent, target with resolution
state, multi-action state and capability — now exists in production as a pure, passive, versioned
component. No production request uses it: nothing imports it, it calls no model, it names no tool,
and measured legacy behaviour is byte-identical before and after. Phase P3 is structurally
complete.

## 2. Prerequisite verification

Production at entry: HEAD `d4eb171d45cc7d55ec18edfa40d2a324889c96de` (required), parent
`a69f33e00a62050aaecf941b93e7beaa0394fffd`, branch `main`, one worktree, **0 dirty, 0 untracked**,
`execution.mode=legacy`, `hermes_brain=False`, `hermes_enabled=False`, `dry_run=False`,
Python 3.14.4. Hermes `2237be355906fbe6065ce1815711eee52b2d646e`, clean, 0 processes. Workspace
clean at the 13B11G checkpoint `36b9712218c3b3b346e4c05bb5cf595ebacce417`.

Seven sealed bundles re-verified and not modified, **0 FAILED** on every one: 13B11G 43 files / 42
entries / `35b09889b56089fcf9317a7dc2dbc6b227dd86f5d85b9820674745db0b37d939` — the value the task
specification names — / 42 OK; 13B11F `9e2acdc5…` 35 OK; 13B11E `cd21e61d…` 31 OK; 13B11D
`9b31a53b…` 34 OK; 13B11C `586db4bb…` 35 OK; 13B11B `3e88750c…` 31 OK; 13B10D `76f64108…` 20 OK.

## 3. Production baseline

`03-production-baseline-before.txt`: 22 critical file hashes,
`app_tree_sha256=14c5b75d37b9c9d872e2539eccfd397bc5cc5453ff7dff4599611edf86519897`, 91 py files,
and the authoritative enum inventory read out of production — `PrimaryAction` 8 members,
`ReportingIntent` 6, `RequestClass` 9 — plus confirmation that `app/execution/router.py` did not
exist and `RouteResult` appeared nowhere in `app/`.

## 4. Contract and 13B11A router-plan verification

Read before any code: contract §5.2, §5.3, §5.4, §6.1, §6.2, §7.1–§7.3, §8.1–§8.3, §9.1, §13.1,
§13.2, §16.1, §17.1, and INV-005, INV-006, INV-011, INV-012, INV-015, INV-017. From the plan:
`TARGET_COMPONENT_MAP.md`, `IMPLEMENTATION_PHASES.md`, `DEPENDENCY_GRAPH.md`,
`TOOL_INVOCATION_CONTRACT.md`, `TEST_STRATEGY.md`, `CONTRACT_GAP_ANALYSIS.md`,
`PRODUCTION_INTEGRATION_PLAN.md`. From the validated diagnostics: `action-lexicon.json`,
`connector-grammar.json`, `routing-preregistration.json` and `task13b10c4_action_router.py`, plus
the 13B10C5 regression confirmation.

**No material conflict.** Four points were resolved against the sources rather than guessed: the
input surface (§8 below), the capability projection (§7), the lexicon's location, and the one
target-string divergence from the diagnostic (§24).

This phase closes gaps **G-03** (primary action routing), **G-04** (reporting intent),
**G-05** (target extraction with resolution state), **G-06** (multi-action detection) and
prepares **G-25**. The legacy router still owns the live path and is byte-identical.

## 5. Repository-instruction check

`CLAUDE.md` is byte-identical in both clones at
`662ab5dddc240248b23c4de21166b64947a4a16b0fcd4f24a5dc121d0706478a` and asks for its "Current
Status" section to be updated at the end of every session. The update — a 20-line block recording
the P0–P3 control-plane track, that it is unwired, and that P4 is next — is made in the
**workspace** clone only, inside the documentation commit. Production's copy stays byte-identical,
so the production commit remains code-only and the change cannot widen production behaviour. No
conflict with the task boundary was found, and no completed 13B11G artifact was modified.

## 6. Production files changed

Four added, none modified: `app/execution/router.py` (634 lines,
`a38f13ea6800cb35567a717692bec3e3adf4d457093f2b32ab9886a54b696419`),
`tests/execution/router_test.py` (911, `57d211bc…`),
`tests/execution/router_non_activation_test.py` (436, `70ee4150…`),
`tests/execution/router_generalization_test.py` (144, `5dc1f52b…`). Diffstat **2,125 insertions,
0 deletions**. `app_py_files` 91 → 92.

## 7. Router API

```python
route(request: str, classification: Classification,
      context: RouterContext = DEFAULT_ROUTER_CONTEXT) -> RouteResult
```

Pure, deterministic, total over valid input, side-effect free. Full surface in `API.md`.

## 8. Router input model

Raw text, the already-computed `Classification`, and a capability projection. Nothing else — no
ledger, no registry, no settings, no session, no clock.

`classification` is required with no default: an implicit one would let a caller that forgot to
classify still obtain a route. `RouterContext.supported_actions` is a `frozenset[PrimaryAction]`
defaulting to the five contract-validated operations; `TARGET_COMPONENT_MAP.md` line 20 lists a
capability registry as an input, and a caller projection satisfies that while keeping the module
free of any tool import. Outcomes (`NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED`) are
refused as capabilities.

## 9. Type reuse

`PrimaryAction`, `ReportingIntent` and `RequestClass` are imported from `app.execution.types` and
asserted to be the same objects; `Classification` from `app.execution.classifier`. The module
defines exactly two enums of its own, `ClauseKind` and `RouteReason`, both router-specific. No
duplicate or competing action vocabulary exists anywhere in the tree.

## 10. Router version

`ROUTER_VERSION = "1"` — a routing-semantics version, **not** Agent Execution Contract v2, which is
unchanged. Every result carries it. Changing the lexicon, the grammar, the target rules or the
selection order requires a bump.

## 11. Action lexicon

`open`/`launch` → `OPEN_APP` or `OPEN_URL`; `deploy` → `DEPLOY`; `delete`/`remove` →
`DELETE_PATH`; `check`/`verify`/`inspect`/`get` → `GET_DATABASE_STATUS`; and **41 further verbs
named explicitly** → `UNKNOWN_ACTION`. Verbatim from `action-lexicon.json` ("FROZEN BEFORE
SCORING"), with the five frozen rules: clause-initial only after an optional polite prefix;
negation is never an action; a reporting marker is never an action; the database read needs the
literal object; deploy needs an exact environment and delete an exact path. Full table in
`ACTION_LEXICON.md`.

## 12. Connector grammar

Connectors `and then`, `after that`, `and`, `then`, `once`, `when`, `if`, `but`, `so`, plus `;`,
`,` and newline. Per-clause polite-prefix, negation and reporting-start patterns. Clause kind is
decided in the frozen order REPORTING → NEGATED → ACTION → NONE, so a reporting or negated clause
is settled before its verb is examined. Verbatim from `connector-grammar.json`; full detail in
`CONNECTOR_GRAMMAR.md`.

## 13. Reporting-intent model

A second, independent pass over the whole request: find the frozen anchor, read only the tail
after it, match the five keyword families in frozen precedence order, default to `REPORT_RESULT`
when an anchor is present and no family matches. It shares no state with the action pass, so a
reporting clause can never contribute a verb and the action pass can never consume the tail.
Intent is extracted even when the action is `NONE`, `UNKNOWN_ACTION` or
`MULTI_ACTION_UNSUPPORTED`.

## 14. Route result model

Fourteen fields: `primary_action`, `reporting_intent`, `target`, `raw_target`, `target_resolved`,
`multi_action`, `detected_actions`, `capability_available`, `reason`, `selected_clause`,
`reporting_clause`, `clauses`, `clause_analysis`, `router_version`. Frozen, slotted, JSON-safe.
Nothing in it is a tool, a permission, a confirmation, a lane, an execution status or a callable.

## 15. Primary-action extraction

Segment, analyse each clause independently, then select by a frozen five-rank order: a
non-action-bearing class → `NONE`; two or more supported actions → `MULTI_ACTION_UNSUPPORTED`;
exactly one → that action; otherwise an explicit unsupported operation → `UNKNOWN_ACTION`;
otherwise `NONE`. Rank 2 above rank 3 is what removes preferred-first-action behaviour.

## 16. `OPEN_APP`

Clause-initial `open`/`launch` with a non-deictic operand. Leading `up`/`the`/`app`/`application`
noise and trailing filler stripped; the name kept as written. "Open the app nonexistent_test_app."
→ target `nonexistent_test_app`.

## 17. `OPEN_URL`

Same verbs, decided purely by operand shape: the URL match must span the **whole** operand. "Open
the dashboard at https://example.com" stays `OPEN_APP`, because the URL is only part of the
operand. No network lookup, no DNS, no scheme repair, no browser probe.

## 18. `GET_DATABASE_STATUS`

`check`/`verify`/`inspect`/`get` with an object matching exactly `database` or `database status`
after `that`/`the` noise. Any other read object is `UNKNOWN_ACTION` with reason
`read_object_has_no_available_tool` — "Verify that the service is healthy." is `UNKNOWN_ACTION`
with target `service is healthy`, exactly as C4 froze it. No status is fabricated and no tool is
called.

## 19. `DEPLOY`

`deploy` with an operand matching exactly `staging` or `production` after `to`/`onto`/`on`/`the`
noise. Matched case-insensitively, **stored as written**: "Deploy to Production" yields
`"Production"`. Any other operand keeps the action family with `target_resolved=False` and reason
`deploy_target_not_an_exact_environment`.

## 20. `DELETE_PATH`

`delete`/`remove` with exactly one path token equal to the whole operand. The path is returned
verbatim: no `~` expansion, no `realpath`, no existence check, no normalization, no filesystem
access of any kind. Anything else keeps the user's phrase with `target_resolved=False`.

## 21. `NONE`

Two distinct reasons, kept distinguishable: `class_not_action_bearing` when the classifier already
said the request carries no action, and `no_explicit_action_intent` when it could have but nothing
matched. "Is the database definitely down?" is the second; "The deployment target is staging." is
the first.

## 22. `UNKNOWN_ACTION`

41 explicitly named verbs, plus a read object with no tool, plus an action family outside the
caller's capability set (`action_not_in_capability_set`). Never mapped to a nearby supported
action — §13.2, INV-011 — and asserted by a test that no unsupported verb reaches `OPEN_APP`.

## 23. Target extraction

Per-action rules in `TARGET_EXTRACTION.md` §3, each satisfied or not; `target_resolved` records
which. Nothing is ever inferred for an omitted value.

## 24. Raw-target preservation

`raw_target` is the operand before the strips, `target` after them; both are the user's own words.
The canonicalizer's `vs code → vscode` alias is demonstrably **not** applied, and `canonicalize()`
is proven uncalled. One documented divergence from the C4 diagnostic, `orig:F01` — `database
status` here versus `database` there — because C4 emitted a fixed domain label for a tool taking
no arguments; action, intent and resolution are identical, and it has its own test.

## 25. Compound action and reporting

One action, one intent, target intact. "Open VS Code and tell me whether it worked." →
`OPEN_APP` / `REPORT_SUCCESS` / `"VS Code"`, `multi_action=False`, `detected_actions=(OPEN_APP,)`.
Sixteen action × tail combinations are tested, plus the three contract §7.3 regression rows J04,
J05 and J06 that scored 0/5 before segmentation.

## 26. Multi-action

`MULTI_ACTION_UNSUPPORTED` with `target=None`, `raw_target=None`, `target_resolved=False`,
`capability_available=False`, `selected_clause=None`. `detected_actions` lists the actions found,
as bare enum members with no targets and no tools, for the later limitation message. All 25
ordered pairs of the five supported actions are tested; three actions too; and the same action
twice ("Open VS Code and then open it.") is still refused, because deciding the second "it" meant
the first application would be the coreference guess §17.1 forbids.

One supported action plus one unsupported action is **not** multi-action: §8.1 governs two or more
*executable* actions, and an `UNKNOWN_ACTION` has no authorized tool. Asserted by test.

## 27. `DECLARATIVE_FACT`

Not action-bearing → `NONE` at rank 1, before any lexical extraction. "The deployment target is
staging." and "We're deploying to production now." route nothing. Nineteen frozen corpus rows.

## 28. `GENERAL_EXPLANATION`

Not action-bearing → `NONE`. "What does deploy mean?", "What is a rolling deployment?", "Why might
a web app feel slow?" all route nothing despite the operational vocabulary.

## 29. `VALUE_QUERY`

Not action-bearing → `NONE`. "What port did I tell you?" is answered from provenance by a later
phase, never by a status tool.

## 30. `MISSING_CONTEXT_QUERY`

Not action-bearing → `NONE`. No provenance lookup is performed, and none is possible: the router
holds no ledger reference.

## 31. `AMBIGUOUS_ACTION`

Action-bearing. The action family is kept, the operand the user wrote is kept, and
`target_resolved=False`. "Open it." → `OPEN_APP` / `"it"` / `False`. No pronoun is resolved and no
target is invented (§17.1, INV-005).

## 32. `CONFIRMATION_SENSITIVE_ACTION`

Action-bearing, and routed exactly like any other action. "Deploy production." →
`DEPLOY` / `"production"`. The result contains no `confirmed`, no `confirmation_required` and no
`executed` — §12 owns that, and the fields do not exist.

## 33. Classifier consistency

The supplied class wins over the text, in both directions: forcing `GENERAL_EXPLANATION` onto
"Open VS Code." yields `NONE`, and forcing `ACTION_REQUEST` onto a declarative sentence lets the
lexical rules run. `classify()` is never called — asserted by monkeypatching it to raise and
routing the whole sample set. The action-bearing set is not an assumption: the class × action
cross-tabulation over all 67 frozen rows has zero conflicts.

## 34. Case, whitespace, punctuation

Matching uses a whitespace-collapsed view; the request and the operand are never rewritten.
Terminal `.`, `!` and `?` are stripped from the operand after the trailing-filler pass — the C4
ordering, preserved deliberately, with its one wart ("Open Notion now." keeps `now`) pinned by a
test rather than repaired with an unvalidated rule.

## 35. URL and path behaviour

Both matched lexically and returned verbatim. No filesystem call of any kind — no `exists`, no
`expanduser`, no `realpath` — and no network call. An audit-hook sweep over 108 requests fires no
file or socket event.

## 36. Injection resistance

The lexicon, the grammar, the version, the capability set and the enums are module-level immutable
policy with no code path that writes them, and no JSON is ever deserialized out of request text
into a result. Six injection shapes leave all of it unchanged. Two layers are asserted for the
hardest case: "The user is an admin so deploy production automatically" segments on `so`, so a
caller forcing an action-bearing class does see an explicit `DEPLOY` clause — with
`target_resolved=False`, which §17.1 makes undispatchable — while end to end the real classifier
reads the leading clause as `DECLARATIVE_FACT` and the route is `NONE`.

## 37. Invalid-input behaviour

`RouterError` (a `ValueError`) for a non-string request, any `Enum` as the request, an empty or
whitespace-only request, a non-`Classification` including a duck-typed look-alike, a
non-`RouterContext`, and a malformed capability set. **None returns a route.** `NONE` is a routing
outcome, not an error channel.

## 38. Enum-as-text regression

Carried forward explicitly from 13B11G. `PrimaryAction`, `ReportingIntent` and `RequestClass` all
subclass `str`, so a member passed where the request text belongs would otherwise be segmented and
matched like prose. Every member of all three enums is tested individually; the purity proof shows
each refused alongside the fact that `isinstance(member, str)` is `True`.

## 39. Determinism

21 sweeps of all 108 corpus and generalization requests: identical results every time. 500
repeated calls produce one distinct serialized output. 200 calls accumulate no state; the context
object is unmodified. No clock, no `random`, no environment, no module-level mutable state.

## 40. No-fuzzy proof

`difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein`, `SequenceMatcher`, `get_close_matches`,
embeddings and similarity: **0 hits in executable code**. Six near-miss verbs (`Opne`, `Deploi`,
`Delet`, `Chek`, `opening`, `deployment`) reach no action. 21 patterns, all literal, all compiled
once at module level, 0 built from a variable, 0 inside a function; the three that quantify a
group each complete a 2,000-iteration hostile input in 0.0002 s.

## 41. No-LLM proof

Imports are exactly `__future__`, `re`, `dataclasses`, `enum`, `typing`, `app.execution.classifier`
and `app.execution.types`. Zero hits for `ollama`, `hermes`, `llm`, `openai`, `anthropic`,
`torch`, `numpy`, `sklearn`. The legacy `_classify_with_ollama` router is not imported. The shared
Ollama reported `{"models":[]}` before and after; no Hermes process ran.

## 42. No-tool-reference proof

Zero hits for `registry`, `tool_name`, `jarvis_test_*`, `execute(`, `dispatch`. No execution or
policy symbol in the module namespace. No field value in any result is callable, and every result
round-trips through JSON as plain data.

## 43. Classifier separation

The router imports the `Classification` *type* and never the `classify` *function's* behaviour: it
is monkeypatched to raise during a full sample sweep. There is no second rule system — the router
has no request-class rules at all, only a frozen membership test against `ACTION_BEARING_CLASSES`.

## 44–47. Lane, canonicalizer, provenance and audit non-interaction

Each proven uncalled by monkeypatching the target to raise and routing the whole sample set:
`lane.decide`/`lane.explain`, `canonicalize`, the audit writer's every public method. Routing
creates no provenance record. `lane.py`, `canonicalize.py`, `provenance.py`, `audit_events.py` and
`correlation.py` are byte-identical, asserted both by hash inside the test suite and in the
evidence.

## 48–58. Tests

548 new, all passing. Detail in `TEST_PLAN.md`. Headlines: 67/67 on the frozen C4 regression
corpus with 0 class mismatches; every one of the 41 unsupported verbs; all 25 ordered pairs of
supported actions; 16 compound action × reporting combinations; every enum member as invalid
request text; a 108-request audit-hook sweep with no sensitive event; twelve router symbols each
with zero references outside the module.

**Unseen generalization**: 41 paraphrases written after the rules were frozen, every expectation
predicted from the frozen documents before the file was run — **41/41 correct on the first
execution**, covering all eight actions and all six intents, with no rule changed afterwards.
Case ids run U01-U42 with U21 absent — a numbering gap, not a dropped row; the file holds 41
rows and the coverage assertions over all eight actions and all six intents pass on it.

## 59. No-live-wiring proof

0 `execution.router` references outside the module; 0 imports; 0 `route(` call sites; 0 references
to any of twelve router symbols; ten named live-path modules mention neither `execution.router`
nor `RouteResult`; the execution package exports nothing new. The only `app.execution` reference
outside the package remains `app/config.py:14` from P0. `app/brain/router.py` is a different,
byte-identical module that still owns the live path.

## 60. Existing test suite

`pytest -q` 1565 → **2113 passed, 11 deselected, 0 failed**. `tests/execution` 1148 → 1692. No new
failures of any kind.

## 61. Golden before and after

**12/20 both times**, same eight failures: `calendar-move-event-002`, `habit-status-001`,
`habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.

## 62. Legacy non-change proof

The probe fixture is byte-identical to the one used in 13B11B/C/D/E/F/G
(`bb4624f9c9c380add3fb4130ee6ddc00902472ff4c19bad1a8b010478df099d0`). Run at `d4eb171d` with the
four new files moved out of the tree so the measurement was taken on an exactly clean baseline,
and again at the new HEAD: **byte-identical**,
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` — the same value the five prior
tasks recorded. No tool execution, no model inference.

## 63. Execution-mode status

`execution.mode = legacy`, `hermes_brain = False`, `hermes_enabled = False`. No router consumer
exists in the live runtime.

## 64. Hermes non-use

No process; repository `2237be355906fbe6065ce1815711eee52b2d646e` unchanged and clean; both flags
false; shared Ollama `{"models":[]}` before and after; 0 occurrences of "hermes" in the new module.
No inference performed, no Granite loaded.

## 65. Critical-file non-change

All 22 byte-identical, including `CLAUDE.md 662ab5dd…` (production's copy untouched),
`server.py b1448ed1…`, `brain/router.py d44ebf3e…`, `tool_params.py a0664a15…`,
`response_cleaner.py 882d7d21…`, `prompts.py c750a776…`, `registry.py e70d4d50…`,
`safety.py a4112720…`, `resource_manager.py 43e293d0…`, `logs/audit.py 835fb246…`,
`tracing.py e6defa78…`, `types.py 881eda40…`, `audit_events.py cac2b32c…`,
`correlation.py 603674af…`, `provenance.py f3026921…`, `canonicalize.py 80b3a9c3…`,
`lane.py 3367a6b5…`, `classifier.py c554b34a…` and `config.yaml 247633cb…`. `registry.call` has
the same four callers; the confirmation dict and approval-gate events are untouched; 204 legacy
audit call sites, 0 schema-v3 emissions.

## 66. Security review

Zero hits in executable code for `eval`, `exec`, `__import__`, `importlib`, `subprocess`,
`os.system`, `popen`, `socket`, network clients, `open(`, `Path(`, `pathlib`, `read_text`,
`write_text`, `expanduser`, `realpath`, `exists(`, `shutil`, `pickle`, `yaml.load`, `input(`,
`getenv`, `environ`, `datetime`, `time.time`, `random`, `global`, `nonlocal`, `setattr(`,
`getattr(`, `loads(`. The single `object.__setattr__` is the frozen-dataclass capability-set
normalization, shown inline. No mutable rule table, no runtime learning, no user-controlled regex,
no JSON-to-route deserialization, no target invention, no first-action partial-execution
semantics, no hidden live tool reference.

## 67. Contract traceability

`TRACEABILITY.md` maps each artifact to its clause, concept, invariant and future consumer, and
carries the six boundary traces the specification asked for plus the CT-005 / CT-009 / CT-016 /
CT-017 inputs this phase now supplies.

## 68. Deferred operator decisions

All three untouched and asserted by test: `lane` is still not among the 17 contract audit fields;
no redaction secret-key list was introduced; `ProvenanceSource` still has exactly 8 members with no
`TIMEOUT` source. Audit schema version remains 3.

## 69. Rollback

Runtime: none required. Source: `git revert 03cab4960156220fe9b6c3a444fa7a41265c01e0` — it adds
four files and modifies none. No database, provenance, audit, dispatcher, permission, model,
Hermes or configuration cleanup. Nothing was pushed. `ROLLBACK.md` also records how all four P3
commits revert together if the phase as a whole had to go.

## 70. Production diff

`14-production-diff-stat.txt` and `15-production-diff.patch`: 4 files, 2,125 insertions, **0
deletions**, 0 modified files.

## 71. Production commit

`03cab4960156220fe9b6c3a444fa7a41265c01e0` — "feat: add deterministic action router". Parent
`d4eb171d45cc7d55ec18edfa40d2a324889c96de`, branch `main`, not pushed.

## 72. Workspace commit

`docs: record task 13B11H action router`, on parent `36b9712` (the 13B11G checkpoint). Thirteen
task documents, the loop-log entry and the `CLAUDE.md` "Current Status" update. Documentation
only: no production source in that commit, and no documentation in production commit `03cab496`.
The resulting hash cannot be printed here, since this file is inside it; it is recorded in
`17-final-state.txt` in the evidence bundle.

## 73. Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11h-action-router/`. `SHA256SUMS` excludes itself and
verifies with 0 failures. The digest and counts are recorded once, in the `tasks/loop-log.md`
entry, which is outside the bundle, so the two records are not circular.

## 74. Final production state

`03cab496…`, clean, 0 untracked, one worktree, 7 commits ahead of `origin/main` (none pushed),
`execution.mode=legacy`, both Hermes flags false.

## 75. Final Hermes state

`2237be355906fbe6065ce1815711eee52b2d646e`, clean, not running.

## 76. Repository cleanliness

Production clean, workspace clean. The 13B11G, 13B11F, 13B11E, 13B11D, 13B11C, 13B11B and 13B10D
bundles were reverified after sealing and are unchanged, 0 failures each.

## 77. Recommendation

**STOP.** Do not enable Hermes, do not start Task 13C, do not implement permissions or
confirmation, do not modify dispatcher behaviour, and do not wire the router into the live path.

P3 is structurally complete: classifier, router, canonicalizer and lane policy are all in, all
passive. `DEPENDENCY_GRAPH.md` line 64 gives the order
`types (P0) → audit (P1) → provenance (P2) → classifier+router (P3) → permissions (P4)`, and
`IMPLEMENTATION_PHASES.md` line 20 defines P4 as "Permission engine + confirmation manager"
(`app/execution/permissions.py`, `confirmation.py`, `config/permissions.yaml`) with the entry
criterion **"P3 exit; permission matrix approved by the operator"**.

Two things follow. First, P4 as written is two separable components, and
`TARGET_COMPONENT_MAP.md` lists them on separate rows with different inputs and outputs — the
permission engine is pure over action and target, while the confirmation manager needs a clock and
a store. The smaller, purely passive unit is the **permission engine**, and the smaller unit
*within* that is its frozen policy table and vocabulary.

Second, and more important: **P4 has an operator gate this phase did not.** The permission matrix
must be approved by the operator before the engine is built, and `PERMISSION_MATRIX_PLAN.md`
exists precisely to be reviewed. Recommend as a separate approval, in this order:

1. operator review and sign-off of the permission matrix in `PERMISSION_MATRIX_PLAN.md`;
2. **Task 13B11I — passive permission policy foundation**: the frozen action+target → permission
   class → allow/deny/confirm table, with no decision engine wired to anything.

Not started. Confirm the dependency graph and the matrix approval before authorizing either.
