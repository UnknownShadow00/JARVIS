# Task 13B11G — Implementation

Production phase P3 of the 13B11A plan, third unit. The canonicalizer (13B11E) and the lane policy
(13B11F) are already in; the remaining P3 units in the dependency graph are the request classifier
and the action router, and the classifier is the router's prerequisite. This task implements the
classifier only.

## 1. Session note

This task ran across two sessions. The first wrote the frozen documents
(`CLASSIFIER_CONTRACT.md`, `RULES_AND_LEXICON.md`, `PRECEDENCE.md`, `CLASSIFICATION_CORPUS.md`),
the module and the three test files, and captured the production baseline, and was interrupted
before any commit. The second session verified that work independently rather than adopting it,
completed the proofs, and made the commits. Both are recorded in
`00-authorization.txt`; what the second session changed is in §6 below.

## 2. Production baseline

Entry HEAD `a69f33e00a62050aaecf941b93e7beaa0394fffd`, parent
`e7432431b5aaa18eb692b94a5520bdb9184dde62`, branch `main`, one worktree, `execution.mode=legacy`,
`hermes_brain=False`, `hermes_enabled=False`, `dry_run=False`, Python 3.14.4. Six sealed evidence
bundles re-verified with 0 failures and not modified: 13B11F
`9e2acdc5d5283de7bccf564f7a5ced9ff8a140ca0b4232b491322539944cf826` (36 files / 35 entries, the
value the task specification names), 13B11E `cd21e61d…`, 13B11D `9b31a53b…`, 13B11C `586db4bb…`,
13B11B `3e88750c…`, 13B10D `76f64108…`.

## 3. Files

Four added, none modified: `app/execution/classifier.py` (429 lines),
`tests/execution/classifier_test.py` (596), `tests/execution/classifier_non_activation_test.py`
(367), `tests/execution/classifier_generalization_test.py` (83). Diffstat **1,475 insertions, 0
deletions**. `app_py_files` 90 → 91.

The path is `app/execution/classifier.py` because that is the path
`TARGET_COMPONENT_MAP.md` line 19 and `IMPLEMENTATION_PHASES.md` line 19 both name — not the
`classify.py` the task prompt offered as an alternative, which the prompt itself subordinates to
the plan.

## 4. Shape

Eleven rules in a tuple. `classify` walks a fixed sequence of tests in that order and returns on
the first match, so precedence is data and not an artefact of which `if` was written first. Each
rule carries a stable id, its `RequestClass` and its `ClassificationReason`; the class comes from
the frozen P0 enum in `app/execution/types.py` and is never redefined.

Matching is set membership against eight frozen lexicons plus five literal regexes compiled once at
module level. Normalization is one whitespace collapse, one `strip()` and one `casefold()`, applied
to a matching key; the caller's request is carried through untouched.

Contract §5.4 records that the validated router recognises an action verb only in clause-initial
position after an optional polite or temporal prefix. The classifier reuses that discipline: it
takes the leading clause and the head token, so a verb *mentioned* in a sentence cannot become a
request. Full segmentation and the multi-action outcome are router work (§5.2, §8) and are not done
here.

## 5. Decisions recorded

**Context is a key set, not a snapshot object.** The plan says "ledger snapshot". Importing the P2
snapshot type would give the classifier a dependency it must not have, and passing values would
tempt it to answer. A frozenset of fact keys is the smallest projection that lets
`VALUE_QUERY` and `MISSING_CONTEXT_QUERY` be distinguished at all, and both are always-operational
classes, so whichever way that split falls, no model prose becomes more trusted.

**No coreference resolution.** `Open it` is `AMBIGUOUS_ACTION`, full stop. §17.1 forbids inventing
a target, and guessing the referent from context would be exactly that.

**The yes/no question is a status check.** A bare `Is the database up?` reaches
`STATUS_CHECK_REQUEST` through R-09. `Can the scheduler handle retries?` reaches it too, although
it reads as an explanation. This is a deliberate conservative over-classification, inherited from
the 13B10C2 selector: it places the turn on the operational lane, where raw model prose cannot be
final. The reverse error would put an operational turn on the conversational lane.

**`MULTI_ACTION_UNSUPPORTED` is not a class.** `RequestClass` has no multi-action member, and §8
makes it a router outcome. `Open VS Code and deploy to staging` classifies from its leading clause
as `ACTION_REQUEST`; the router detects the second action and refuses to dispatch. Documented in
`PRECEDENCE.md` row 12, not silent.

## 6. What the completing session changed

Three changes, all defended in the open:

1. **Two contract citations were wrong.** The module cited "§18, INV-011" for the never-invent-a-
   target rule; contract §18 is *Tool-result trust* and INV-011 is about unsupported actions
   mapping to unrelated tools. The correct clause is §17.1. A second comment cited "§20" for the
   general-explanation rule, which in the contract is *Metrics*; the supporting clause is §4.1.
   Both were corrected in the module and in `PRECEDENCE.md` and `CLASSIFICATION_CORPUS.md`. Prose
   only: no rule, class, precedence rank or corpus expectation changed.

2. **A fail-open was found and closed.** `RequestClass` subclasses `str`, so
   `classify(RequestClass.OTHER)` was accepted as text and returned `OTHER` — a caller confusing
   its arguments would have got a plausible-looking answer. The purity proof surfaced it. `classify`
   now refuses any `Enum` passed as the request. This is input validation, not a classification
   rule: the frozen corpus (83 rows) and both generalization sets were re-run afterwards with
   identical results, so no expectation moved. Ten tests were added for it.

3. **A second, independent generalization set was run** (`08-independent-generalization.txt`): 33
   unseen requests whose expected classes were predicted from `PRECEDENCE.md` and
   `RULES_AND_LEXICON.md` alone, before running them. 33/33 agreed, 9/9 classes covered. No rule,
   lexicon entry or precedence rank was changed after it ran.

## 7. Results

`pytest -q` 1068 → 1565 passed, 11 deselected, 0 failures (497 new: 325 + 127 + 45).
`tests/execution` 651 → 1148. Golden unchanged at 12/20 with the same eight failures. The legacy
behavioural probe, byte-identical to the fixture used in 13B11B/C/D/E/F, was run at `a69f33e` with
the four new files moved out of the tree and again at the new HEAD: byte-identical,
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291` — the same value the four prior
tasks recorded. All 20 critical files byte-identical.

Production commit `d4eb171d45cc7d55ec18edfa40d2a324889c96de`, parent `a69f33e…`, not pushed.
