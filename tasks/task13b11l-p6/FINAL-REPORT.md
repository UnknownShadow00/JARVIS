# Task 13B11L-P6 — deterministic response-obligation engine

## Verdict

**JARVIS RESPONSE OBLIGATION FOUNDATION IMPLEMENTED**

```
8a70d179c527f2912522920918f70a68ee213386   feat: add deterministic response obligation engine
  parent  ea0cb32040a0e24d0b80de706929086b6dd36b66
  7 files, 2289 insertions, 0 deletions, 0 files modified       NOT pushed
```

## What this is

Phase P6 unit 1 of the agent execution contract v1 production integration, re-run from the
repaired P3 baseline. Contract §14.1: every operational turn carries **exactly one** response
obligation, derived deterministically from frozen inputs only (INV-009).

`app/execution/obligations.py` decides *what JARVIS is obligated to report*. It does not
decide how it is worded — no template, no user-facing string, no prompt. It reads no request
text, takes no model parameter, holds no store, clock or registry, and constructs nothing.
Execution truth reaches it only as a `TrustedToolResult`, which from P5 only the dispatcher
can construct.

## The blocker is gone, and proven gone

The original 13B11L BLOCKED because 20 of the router's 41 unsupported verbs collapsed to
`OTHER` / `NONE` / `CONVERSATIONAL`, where §4.2 permits raw model prose, against §13.1
(NORMATIVE). R1 repaired the lexicon (`9ace0e3`), R2 named the repaired rule set
(`ea0cb32`, `CLASSIFIER_VERSION = "2"`).

Measured here twice — first through the raw `classify -> route -> lane` chain before any P6
code existed, then through the engine:

| | |
|---|---|
| unsupported verbs reaching `UNKNOWN_ACTION` + `OPERATIONAL` | **41/41** |
| of which the twenty the blocked task lost | **20/20** |
| reaching `REPORT_CAPABILITY_UNAVAILABLE`, rank 6, `explicit_action_without_tool` | **41/41** |
| answered with confirmation, a target question, success or an intent acknowledgement | **0/41** |
| plain chat still conversational, carrying no obligation | **7/7** |
| the declarative control acknowledged, not refused as unsupported | **1/1** |
| ambiguous phrasings asking for the target | **3/3** |

## The method earned its keep twice

**The frozen table caught two wrong rank predicates.** The matrix was written and hashed
with `app/execution/obligations.py` provably absent. Frozen against the corrected P3
outputs, the validated 13B10C5 ladder put all 41 unsupported verbs on rank 1 (22, answered
*"shall I proceed?"*) or rank 4 (19, answered *"which one?"*). Both imply an execution that
can never happen, which §13.1 forbids in terms. Rank 1 now requires an action an approval
could bind (§12.3 binds an approval to an action type *and a target*) and rank 4 an action
that actually *requires* a target (§17.1) — both grounded in production's own rules, since
the permission engine denies every non-executable action and the confirmation layer refuses
to bind one. Had the module been written first, the table would have been written to match
it.

**The existing suite caught an architectural violation.** The first version imported
`app/execution/confirmation.py` for `ConfirmationState`, and three P4 tests failed
correctly: phase P5 had gone out of its way to leave that machine with **zero importers**.
The fix was on this side, and it cost a matrix re-freeze. The contract's confirmation state
for an *action* is `ToolResultStatus.CONFIRMATION_REQUIRED`, already in `types.py`, and
whether an approval was claimed now arrives as a settled projection — exactly what
`tasks/task13b11l/DECISION_INPUT.md` specified a task earlier. **No existing test was
relaxed, weakened or deleted.** Four constants were renamed for the same reason, because
earlier phases' non-activation tests reserve their own names.

The module then agreed with the corrected table on the **first run**: 0 failures across all
442 rows, including the per-row min-rank priority proof.

## Results

| requirement | § | result |
|---|---|---|
| production began at `ea0cb320…` | 2 | **exact**, parent `9ace0e3a…`, clean, 0 untracked |
| R1 / R2 / 13B11K evidence verified | 3, 4 | 4 bundles, **0 manifest failures**; 36 bundles total, 0 failures |
| blocked 13B11L evidence unchanged | 3 | `ca703e18…`, matching its loop-log value; newest file 2026‑09‑19 21:02 |
| P5 untouched | 4 | `dispatch.py` **byte-identical** across HEAD, `a0cc4d3c` and the sealed bundle |
| classifier rule set | 7 | **"2"**, carried in every composed fixture |
| matrix frozen before the module | 34 | **yes**, `ls` recorded ABSENT in the seal |
| every obligation reachable | 37 | **11/11** |
| every reason reachable | 40 | **22/22** |
| every rule wins a row | 36 | **21/21** |
| every contradiction code reachable | 63 | **20/20** |
| exactly one obligation per operational turn | 11 | **361/361** valid rows |
| priority deterministic, not branch order | 64 | `min(rank of every rule that holds) == selected rank`, **per row** |
| `OBLIGATION_PRIORITY` complete and single | 10, 36 | 11 members, ranks 1–11 once each; no second ordering in production |
| SUCCESS only from trusted executed SUCCESS | 17 | enforced, tested |
| ERROR / TIMEOUT / DENY never become success | 18, 19, 22 | enforced; contradictions raise |
| confirmation never implies execution | 21 | rank 1 requires `not executed` |
| ambiguity invents no target, missing context invents no value | 23, 24 | the decision carries neither |
| no raw request parsing | 13 | no `str` field, no regex, no lexicon import, 0 of 41 verbs in the source |
| no model authority | 14, 65 | draft, proposal, mapping, bool and string all refused by type |
| no response prose | 15, 67 | every string constant scanned; decision has 3 fields, no message |
| purity | 66 | 8 imports; audit hook over 240 decisions sees **0** events, 0 new threads |
| no live wiring | 68 | **0** importers, 0 symbol references, 0 call sites under `app/` |
| no audit / provenance / permission / confirmation mutation | 43–46 | monkeypatched to raise; never hit |
| full suite | 69 | 3744 → **5122 passed, 11 deselected, 0 failed** |
| golden | 70 | **12/20, the same eight IDs** |
| legacy probe | 71 | **byte-identical**, `fc68a0b0…d98291` |
| critical files | 72 | **24/24 IDENTICAL** |
| Hermes | 73 | `2237be35…` clean, 0 processes, mode `legacy`, both flags false |
| security review | — | **34/34** |

## Two contract mappings frozen, and flagged

The blocked task recorded both as open operator questions rather than deciding them. Both
are decided **inside** the frozen eleven, so neither extends the contract — but both would
be resolved differently by a v2 contract, and neither is reversible without one.

**D-P6-01 — `PermissionOutcome.DENY` → `REPORT_CAPABILITY_UNAVAILABLE` (rank 6).** The
frozen eleven contain no `REPORT_PERMISSION_DENIED`; adding one is a §6.2 contract
extension this task is not authorized to make. The distinction is not lost: the reason
carries `permission_denied`, separately from `explicit_action_without_tool`,
`capability_unavailable` and `dispatch_blocked`. Four deterministic refusal causes, one
obligation.

**D-P6-02 — `ToolResultStatus.TIMEOUT` → `REPORT_TOOL_ERROR` (rank 2).** §18 says the side
effect may or may not have happened and the response must claim neither; rank 3 would claim
it did. The reason is `trusted_tool_timeout`, never `trusted_tool_error`, and the
`TrustedToolResult` the builder also receives still carries `status=TIMEOUT`.

## Also flagged to the operator

**The R1 and R2 evidence bundles record a "bundle SHA-256" that cannot be reproduced.**
13B11K and the blocked 13B11L record theirs as `sha256sum SHA256SUMS`, and both match their
canonical loop-log values exactly (`92fcfff4…`, `ca703e18…`). R1 and R2 record
`46c47521…` and `f2be8507…`, computed by a method no script in either bundle contains;
fourteen candidate formulations were tried and none matched. Nothing was modified to make
them agree. Integrity was established three other ways instead — `sha256sum -c` passes with
0 failures, no file in either bundle is newer than its own `SHA256SUMS`, and R1's
`source/classifier.py` is byte-identical to production `9ace0e3a`. A future task should
either document the formula or restate both digests under the `sha256sum SHA256SUMS`
convention the other bundles use.

**The matrix moved twice before it was final**, and both movements are recorded with their
cause in `matrix-versions.txt` rather than quietly re-frozen. v1→v2 is proven purely
additive (10 rows added, 0 removed, **0 moved**, header constants identical). v2→v3 changed
an input column for the confirmation-import reason above.

**`ValueProjection` is still caller-supplied.** Who computes it remains the open question
the blocked task recorded; it is P7 pipeline work, not P6. What is frozen here is that the
projection carries availability and trust class and **never the value**, so no second
recogniser can grow in the response layer (§15.3).

## Still passive

`execution.mode` is `legacy`, both Hermes flags false. Nothing under `app/` imports the
module — proven over parsed imports, not greps. `derive`, `require`, `source_for`,
`satisfied` and `contradiction` have **0** call sites under `app/`. `registry.call` still
has exactly four, all in `app/server.py`. The P4 confirmation machine still has zero
importers. `app/execution/__init__.py` does not mention the engine. The commit adds seven
files and modifies none.

## Evidence

`/home/jarvis/.hermes-poc/evidence/task13b11l-p6-obligation-engine/`, sealed with
`SHA256SUMS` excluding itself, 0 failures. The blocked 13B11L bundle and both repair bundles
were verified unmodified at entry and again at exit; read-only copies of the blocked
finding are carried under `inherited/`.

## Next

**STOP.** The response builder was not built and must not be in this turn.

`task13b11a/IMPLEMENTATION_PHASES.md` lists P6 as `obligations.py` **and** `response.py`,
and `TARGET_COMPONENT_MAP.md` gives them separate rows with separate "must never" clauses;
13B11K reported them separable and this task confirms it. The next approved unit is the
**deterministic operational response builder**: consume `ObligationDecision`,
`TrustedToolResult`, the provenance attribution and the permission/confirmation state, and
construct `ApprovedOperationalResponse` — with no model-authored operational truth, and with
the attribution rules of §16 and the minimal-result principle of §18.4 enforced in the
templates. The real registry adapter is P9, not next.

Do not enable Hermes. Do not start 13C. Do not wire P6 live.
