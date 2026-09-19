# Task 13B11F — Test Plan and Results

310 new tests. `tests/execution` totals 651.

| File | Tests | Covers |
|---|---|---|
| `tests/execution/lane_test.py` | 201 | the frozen table, every class, every condition, combinations, no-downgrade, invalid input, determinism, reasons, serialization, type reuse |
| `tests/execution/lane_non_activation_test.py` | 109 | purity, model non-authority, no text parsing, phase non-interaction, deferred decisions, no live wiring |

The truth table is **transcribed by hand** into the test file from `TRUTH_TABLE.md`, which was
hashed before the module existed. The expected lane for a row is computed by a small independent
function in the test, not imported from the implementation, so a policy change fails a test rather
than redefining the expectation.

## 1. The table itself

Asserted: the version literal `"1"` and its type; the always-operational set is exactly the seven
contract classes; the conditional set is exactly `{GENERAL_EXPLANATION, OTHER}`; the two sets are
disjoint and together cover every `RequestClass` member; `RequestClass` still has nine members and
none is unhandled; the condition names are exactly the seven contract conditions in order; each
condition has its own distinct reason; `LaneReason` has exactly the nine frozen members.

## 2. Request classes

Every member is covered. Each of the seven always-operational classes is OPERATIONAL with no
signals; each of the two conditional classes is CONVERSATIONAL with no signals; and a parametrized
test checks every member's default against the independent table function.

## 3. Operational overrides

Each of the seven conditions is tested alone against each of the two conditional classes (14 cases)
and against each of the seven always-operational classes (49 cases). All seven together escalate.
Twelve condition pairs are tested on both conditional classes.

## 4. The exhaustive table

One test walks all **1,152 rows** (9 classes × 128 combinations), asserting each against the
independent expectation, and asserting the totals: 1,150 OPERATIONAL, 2 CONVERSATIONAL. A second
test collects every conversational row and asserts there are exactly two, that both belong to the
conditional classes, and that both have every condition false.

## 5. No downgrade

For each always-operational class, the set of lanes produced across all 128 combinations is
asserted to be exactly `{OPERATIONAL}`. A separate test asserts that across all 1,152 rows, any row
with at least one true condition is OPERATIONAL — so no combination of flags produces a
conversational turn where operational state exists.

## 6. `GENERAL_EXPLANATION`

Conversational with no operational state, with the reason `NO_OPERATIONAL_STATE`. Escalates on each
of the seven conditions independently, with the matching single reason. The tool-result and
confirmation cases — the ones that decide the §4.1 reading — are asserted individually as well.

## 7. `OTHER`

Conversational with nothing operational; escalates on each condition independently; escalates on
multiple conditions with both reasons recorded in order; and one test asserts `OTHER` and
`GENERAL_EXPLANATION` agree on **all 128** combinations.

## 8. Combined and contradictory state

`confirmation_required` together with `tool_result` resolves to OPERATIONAL with both reasons, in
declaration order. Reason order is proven independent of keyword-argument order. An
always-operational class records the class reason first and then its conditions. Every decision
carries at least one reason, and `NO_OPERATIONAL_STATE` appears on a decision if and only if the
lane is CONVERSATIONAL — asserted across all 1,152 rows.

## 9. Invalid input

Ten bad request-class values (including the bare strings `"VALUE_QUERY"` and
`"GENERAL_EXPLANATION"`, `None`, integers, a `Lane` member and a list) raise `LanePolicyError`. A
dedicated test first asserts `"VALUE_QUERY" == RequestClass.VALUE_QUERY` — true, because it is a
`str` enum — and then asserts the string is still refused, proving membership is checked by type.
Seven bad `signals` values are refused, including a structurally complete look-alike object. Every
one of the seven fields rejects `1`, and eight non-bool values are refused on one field. An unknown
keyword raises `TypeError` from the dataclass. One test asserts that no invalid input anywhere
returns a lane, and one asserts `LanePolicyError` is a `ValueError`.

## 10. Determinism and immutability

Every one of the 1,152 rows is decided 21 times with identical lane, reasons and serialization.
Five hundred repeated calls accumulate no state, and a conversational row decided afterwards is
still conversational. `LaneSignals` and `LaneDecision` are frozen; `SIGNAL_REASONS` is read-only;
`NO_SIGNALS` is all-false with no reasons.

## 11. Serialization

`to_mapping()` produces plain JSON-serializable data with `lane`, `request_class`, `reasons` and
`lane_policy_version: "1"`; 50 repeated dumps produce one distinct string; signals serialize to
seven plain booleans.

## 12. Types reused

`lane_module.Lane is types_module.Lane` and the same for `RequestClass` — identity, not equality.
No name defined *in* the lane module is called `Lane` or `RequestClass`, and `ExecutionLane`,
`ResponseLane` and `TrustLane` do not exist.

## 13. Purity, model non-authority, no text parsing

Imports are asserted to be exactly `{__future__, dataclasses, enum, types, typing,
app.execution.types}`, with `app.execution.types` the only application import. Twenty-nine
forbidden constructs are absent, including `eval`, `exec`, dynamic import, `subprocess`, sockets,
HTTP clients, `ollama`, file access, `getenv`/`environ`, `datetime`, `time.time`, `random`,
`global`/`nonlocal`, `setattr` and `object.__setattr__`. There is no module-level mutable
container. Both public functions take exactly `(request_class, signals)`. No input name contains
any of fourteen model-authority tokens, and `allow_model_raw`, `trust_model`,
`safe_model_response`, `model_says_no_action`, `model_confidence` and `ModelDraft` are absent from
both the source and the module namespace. Twelve string-analysis constructs are absent — `import
re`, every `re.*`, `.split(`, `.startswith(`, `.endswith(`, `.lower()`, `.casefold()`, `difflib`,
`tokenize` — and no identifier contains `prompt`, `utterance`, `transcript`, `user_text` or
`raw_text`.

A separate runtime proof (`scripts/purity.py`) runs all 1,152 rows under a CPython audit hook
watching file opens, sockets, subprocesses, network, dynamic import, `exec`/`compile` and
filesystem mutation: **no sensitive event fired**.

## 14. Phase non-interaction

Fifteen identifiers belonging to other phases are asserted absent from the module's AST. Deciding a
lane with the legacy audit writer monkeypatched to raise runs all 1,152 rows without the writer
ever being called. A real `ProvenanceLedger` is empty before and after a decision. Schema version 3,
the 17 contract fields with `lane` absent, the 8 `ProvenanceSource` members with no TIMEOUT, and the
canonicalizer's version and single rule are all asserted unchanged.

## 15. No live wiring

No production module outside `app/execution/` contains `execution.lane`; eight lane-policy symbols
have zero references outside the package; and ten named live-path modules — `server.py`,
`brain/router.py`, `brain/tool_params.py`, `brain/prompts.py`, `brain/response_cleaner.py`,
`tools/registry.py`, `computer/safety.py`, `resource_manager.py`, `logs/audit.py`,
`observability/tracing.py` — contain no reference. The `app.execution` package exports nothing new.

## 16. Results (production venv, Python 3.14.4)

| Run | Before (e743243) | After (a69f33e) |
|---|---|---|
| `pytest -q` | 758 passed, 11 deselected, 0 failed | **1068 passed, 11 deselected, 0 failed** |
| `tests/execution` | 341 passed | 651 passed |
| `evals.runner --mode deterministic` | 12 passed / 8 failed | **12 passed / 8 failed, same eight IDs** |
| legacy probe | sha256 `fc68a0b0…` | **sha256 `fc68a0b0…` — byte-identical** |

Collection 1068/1079 with 11 deselected by the unchanged `pytest.ini` marker expression. No new
failures. The eight known golden failures are unchanged: `calendar-move-event-002`,
`habit-status-001`, `habit-complete-002`, `safety-delete-downloads-001`, `safety-shutdown-002`,
`safety-derived-injection-004`, `clarify-open-target-001`, `clarify-delete-target-002`.
