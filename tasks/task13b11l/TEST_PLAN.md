# Test Plan — Task 13B11L

**No tests were written, because no module was written.** This is the plan the unblocking task
inherits.

## Ran in this task (read-only, against production, nothing written)

| Check | Result | Evidence |
|---|---|---|
| `OBLIGATION_PRIORITY` complete, ranks 1–11 once each | pass | `04-priority-proof.txt` |
| all 41 router `UNSUPPORTED_VERBS` through the real `classify → route → lane` chain | 21/41 correct, **20/41 fall through** | `05-verb-sweep.txt` |
| are the fall-through operations separable from plain chat by structured state? | **no** — 1 identical signature | `05-verb-sweep.txt` |
| does the proposed upstream fix suffice? | yes — 21/41 → 41/41, 0 collateral movement | `06-fix-simulation.txt` |
| production unchanged; suite, golden, probe | 3247 / 12-20 / `fc68a0b0…` | `09-production-non-change.txt` |

## Planned for the implementation

Files: `tests/execution/obligations_test.py`, `obligations_matrix_test.py`,
`obligations_non_activation_test.py`.

| Area | What it must prove |
|---|---|
| every obligation | each of the 11 members has a positive case, or an explicit proof it is unreachable in v1, with reason and source asserted |
| exactly one | no operational turn yields zero or two obligations (CT-011) |
| priority | the walk reads `OBLIGATION_PRIORITY`, never a second tuple; overlapping triggers resolve to the highest rank; no code-order accidents |
| success / error / timeout | a `TrustedToolResult` is the only route to `REPORT_TOOL_SUCCESS`; `ERROR` and `TIMEOUT` can never reach it |
| blocked / confirmation / deny | refusal statuses keep `executed=false` semantics and do not collapse into one category beyond what the contract's eleven allow |
| ambiguity / missing context / unsupported | no target invented, no value fabricated, no nearest-tool substitution |
| value query | decided from the availability + trust projection only; the value itself never appears in the output |
| declarative fact | a user fact never becomes `TOOL_SUCCESS` (§9.3, §16.1) |
| conversational | `GENERAL_EXPLANATION` + `CONVERSATIONAL` yields no operational obligation and no operational claim |
| contradictions | the corpus in `CONTRADICTION_POLICY.md` §2, each raising |
| model non-authority | no public input accepts `ModelDraft`, model text, confidence, a recommended obligation or an execution claim; a boolean `tool_succeeded` does not exist |
| no response text | the output carries no prose, no template and no prompt string |
| purity | AST + CPython audit hook: no filesystem, network, subprocess, clock, random, registry, dispatch, store, model, Hermes or audit writer |
| no live wiring | 0 importers under `app/`, 0 references to any public symbol, package `__init__` silent, named live-path modules clean |
| type reuse | the P0 types are the ones used; no duplicates defined |
| P3 reconciliation regression | the 41-verb sweep, asserted at 41/41 — as a **test**, so the gap cannot silently reopen |

The last row is the one this task most wants to leave behind: the mismatch existed undetected
from 13B11G to 13B11K because nothing asserted the two lexicons agreed.
