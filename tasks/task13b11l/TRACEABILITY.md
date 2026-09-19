# Traceability — Task 13B11L

## The blocking finding

| Claim | Source | Evidence |
|---|---|---|
| every operational turn has exactly one obligation, from six named frozen inputs | contract §14.1 | — |
| an action with no authorized tool MUST be `UNKNOWN_ACTION` and answered `REPORT_CAPABILITY_UNAVAILABLE` | contract §13.1 (NORMATIVE) | — |
| no nearest-tool substitution | contract §13.2, INV-011 | — |
| the lane is decided deterministically and an operational turn is never relabelled conversational | contract §4.1, §4.2 | — |
| model prose may be user-visible on the conversational lane | contract §4.2 | — |
| the response layer must not add a parallel extractor over the request text | contract §15.3 | — |
| the two lexicons diverge and P6 is the reconciliation point | `tasks/task13b11h/IMPLEMENTATION.md:106` | — |
| 20 of 41 unsupported verbs never reach `UNKNOWN_ACTION` | measured | `05-verb-sweep.txt` |
| those 20 and plain chat share one identical structured signature | measured | `05-verb-sweep.txt` |
| therefore an unsupported operation currently reaches the conversational lane, where §4.2 permits model prose — violating §13.1 | derived from the two above | `P3_RECONCILIATION.md` §5 |
| the upstream fix is sufficient and narrow | measured, read-only simulation | `06-fix-simulation.txt` |

## Task requirements and how each was met

| § | Requirement | Outcome |
|---|---|---|
| 2 | exact `a0cc4d3c…` baseline | verified; parent `c321cb89…`; clean; legacy; both flags false |
| 3 | 13B11K evidence 50/49/`92fcfff4…` | verified, 0 failures; all 30 sealed bundles re-verified |
| 4 | read normative sources first | contract §4–§18, CT-011/012/018, the 13B11A plan set, the validated 13B10C5 design |
| 6 | reuse `ResponseObligation`, `ObligationDecision`, `OBLIGATION_PRIORITY` | confirmed present and complete; nothing duplicated because nothing was written |
| 9, 47 | priority complete, block if not | **passes** — 11 members, ranks 1–11 once each, identical to §14.2 |
| 32 | reconcile classifier/router, or BLOCK with the exact upstream change | **cannot reconcile** → BLOCKED; change specified and verified |
| 46 | freeze and hash the matrix before coding | deliberately not frozen — an input is about to change; reasoning in `OBLIGATION_MATRIX.md` |
| 5, 72 | do not modify live behaviour or the listed modules | 25 files verified byte-identical; nothing written at all |
| 69–71 | suite, golden, probe | 3247 / 11 deselected; 12/20 same eight; `fc68a0b0…` |
| 73 | Hermes non-use | repo `2237be35…` clean, 0 processes, Ollama idle, no inference |
| 75 | do not resolve unrelated deferred issues | D-01, TTLs, timeout-in-`EXECUTING`, lane-as-audit-field, redaction list, `TIMEOUT` provenance source — all untouched |
| 77 | rollback | nothing to roll back; no production commit exists |

## Deferred, carried forward untouched

`browser.open`/`browser.search` versus D-01; numeric confirmation TTLs; the timed-out
confirmation left in `EXECUTING` by P5; `lane` as an audit field; the redaction secret-key list;
`TIMEOUT` as a `ProvenanceSource`; the real registry adapter; live capability projection; live
pipeline wiring.

**Newly recorded by this task** (in `OBLIGATION_MATRIX.md` §"Two mapping questions"): whether
`PermissionOutcome.DENY` maps to `REPORT_CAPABILITY_UNAVAILABLE` or needs a twelfth obligation,
and whether `TIMEOUT` belongs in the `REPORT_TOOL_ERROR` family. Both are operator questions.
