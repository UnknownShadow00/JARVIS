# Task 13B11K — Trusted Dispatcher Seam Foundation

**Verdict: JARVIS TRUSTED DISPATCHER FOUNDATION IMPLEMENTED**

Phase P5 of the agent execution contract v1 production integration plan. The trusted execution
boundary exists, is pure, and is wired to nothing.

| | |
|---|---|
| Production | `/home/jarvis/JARVIS` `a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a` |
| Parent | `c321cb8958935fa74db0916ec47e56f052410663` |
| Workspace | see `18-workspace-commit.txt` |
| Hermes | `2237be355906fbe6065ce1815711eee52b2d646e`, clean, not running |
| Mode | `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` |

---

## 1. Entry state, verified not assumed

Production began at `c321cb8958935fa74db0916ec47e56f052410663`, parent
`52c5da5d7a5d304acd4088b11e1f9bd509067069`, branch main, 1 worktree, 0 dirty, 0 untracked, 9
commits ahead of origin, Python 3.14.4, `execution.mode=legacy`, `approval_mode=balanced`,
`dry_run=false`, both Hermes flags `false`. Workspace clean at `fd1aadaa3d4486a93f5a3b2b72c71b486de77719`.
Hermes `2237be35…` clean and not running, 0 processes, shared Ollama holding nothing.

The 13B11J bundle matched the task's stated values exactly: **47 files, 46 manifest entries,
`SHA256SUMS` SHA-256 `d5098cc3192880ff6bc6e4e2e659064e4eb71d8192c2fa0b64386509e3df6fcb`,
`sha256sum -c` 0 failures.** All ten sealed `task13b11*` bundles were re-verified — 13B11A
through 13B11J — 0 failures anywhere. No prior evidence was modified.

Baseline measured rather than assumed: **2892 passed, 11 deselected, 0 failed**; `tests/execution`
2475; golden 12/20 with the same eight IDs; legacy probe
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, byte-identical to the sealed
13B11J probe; `registry.call` 4 call sites, all in `app/server.py`; 0 constructions of
`TrustedToolResult` or `ToolInvocation` anywhere under `app/`.

## 2. Ownership, established from the plan

Three independent sources put `PENDING → EXECUTING` in this phase: `CONFIRMATION_STATE_PLAN.md`
§3 ("approval transitions directly into `EXECUTING` under a lock"),
`PRODUCTION_INTEGRATION_PLAN.md` §13, and production `confirmation.py` itself, whose
`EVENTS_REQUIRING_DISPATCHER` reserves `CONFIRM`, `DISPATCH_SUCCESS` and `DISPATCH_ERROR` and
whose refusal message names "phase P5". The component path
`app/execution/dispatch.py` is taken verbatim from `TARGET_COMPONENT_MAP.md` §1 and
`IMPLEMENTATION_PHASES.md` P5 — not `dispatcher.py`.

The refusal-representation question (§28 of the task) was decided from the contract, not
guessed: a permission or confirmation refusal is a `TrustedToolResult` carrying `BLOCKED` or
`CONFIRMATION_REQUIRED` with `executed = false`. `TOOL_INVOCATION_CONTRACT.md` §2 lists both as
result statuses, §3.3 says both carry `executed = false`, and `provenance.py` already names them
as statuses that reach a `dispatch.result` event and are refused there. Only API misuse raises.

## 3. Frozen before the module existed

Eight design documents and the 150-cell `dispatch-matrix.json`
(`ede846eb7ae4c295f2fbd76628e5b0509190513667856a0f6d50a1a68e71ce2e`) were written and hashed
while `ls app/execution/dispatch.py` reported "No such file or directory" and
`grep -rl TrustedDispatcher app/` returned 0 files. Both facts are recorded inside
`frozen-hashes.txt` at the moment of hashing.

**The freeze earned its keep.** On the first scored run, five of the 150 cells failed: the draft
refused a gated invocation with no confirmation id at gate 2 as `invocation_inconsistent`, while
the frozen table said `confirmation_absent` at gate 5. Both are equally safe — the executor is
unreached either way — but contract §12.1 requires a gated action to *present* as
`CONFIRMATION_REQUIRED`, and the P6 obligation engine reads that status. The code changed; the
table did not. Had the table been written afterwards, the wrong answer would have looked like a
design choice.

## 4. What was implemented

`app/execution/dispatch.py`, 796 lines, importing exactly `__future__`, `threading`,
`dataclasses`, `datetime`, `typing`, `app.execution.correlation` and `app.execution.types`.

Seven gates, in the frozen order: type validity → invocation structure → canonicalization
metadata → settled permission outcome → confirmation requirement → atomic execution claim →
executor. `build_invocation()` produces the frozen P0 `ToolInvocation` and nothing else; there is
no `DispatchInvocation`, `ExecutableRequest` or `ToolCallRecord`. Identifiers come from the P1
family — 500 minted ids, 500 distinct, all 32 hex, none carrying request, target, tool or model
text. Raw and canonical arguments are both retained, distinct, copied by value and immutable;
the dispatcher normalizes nothing.

The executor is a structural protocol with **no default**. `TrustedDispatcher(clock=…)` raises
before an instance exists; `None`, a string and an integer each raise `DispatchError`. An
executor may report only `SUCCESS`, `ERROR` or `TIMEOUT` — claiming `BLOCKED` or
`CONFIRMATION_REQUIRED` is a contract violation, which is the seam that stops an executor
manufacturing a verdict.

The confirmation authority is also a structural protocol, declared rather than imported, because
the sealed 13B11I and 13B11J proofs assert that the permission engine and the confirmation
machine have **zero importers and zero symbol references anywhere under `app/`**. Those proofs
are untouched and still pass. The real store is what the tests inject, so what is under test is
the real guarantee.

## 5. The scored matrix

150 cells = 3 permission outcomes × 10 confirmation setups × 5 executor outcomes, each driven
against the real dispatcher and, where a confirmation exists, the real `ConfirmationStore`. Six
fields compared per cell.

**10 cells reach an executor. 140 refuse, every one with `executed = false` and no facts.**
95 `BLOCKED`, 45 `CONFIRMATION_REQUIRED`, 2 `SUCCESS`, 6 `ERROR`, 2 `TIMEOUT`. Plus 5 replay
rows: after any first outcome, a second dispatch of the same invocation is `BLOCKED` /
`invocation_already_dispatched` and the executor call count stays 1.

## 6. Safety properties, measured

* **`DENY` never reaches the executor** — 25 cells, 0 calls.
* **`REQUIRE_CONFIRMATION` cannot bypass the exact approval** — 45 cells. Nine invocation-visible
  bound fields and three invocation-invisible ones were each mutated one at a time; all twelve
  refused, and the honest record stayed `PENDING` every time.
* **No cross-session spend** — an intruder's dispatch is `confirmation_not_found`, reported with
  the same message as an unknown id so the error is not an oracle, and the victim's record is
  untouched.
* **No stale execution** — an expired approval refuses and is expired on access; rewinding the
  clock does not revive it.
* **No replay** — one approval, one invocation; a spent approval cannot authorize a new
  invocation; eight concurrent dispatches of one invocation execute once.
* **No model-created trust** — `ModelDraft`, `ToolProposal` and a result-shaped dict all become
  `executor_contract_violation` with no facts. No promotion helper exists, asserted over the
  module's own public names.
* **No misattribution** — an outcome naming a different invocation is discarded; the result
  always carries the dispatched invocation's identity.
* **Monotonicity** — ten coercion attempts (`confirmed`, `approval`, `permission_outcome: ALLOW`,
  `authorized`, `force`) against both gated outcomes: 0 weakenings.
* **No partial execution** — `MULTI_ACTION_UNSUPPORTED` is unbuildable and refused, and
  `dispatch()` contains no loop.
* **No retry** — a failing executor is called exactly once; the module contains no retry
  vocabulary.

Security review: **32/32 checks pass, no unresolved authority bypass.**

## 7. Purity and non-activation

760 public operations under a CPython audit hook watching file opens, sockets, subprocesses,
dynamic import, `exec`/`compile`/`eval`, filesystem mutation and sleep: **0 sensitive events**,
thread count unchanged at 1. 300 identical `DENY` dispatches produced 1 distinct answer.

0 importers under `app/`. 0 references to any of 14 public symbols anywhere under `app/`. The
package `__init__` is silent. Thirteen named live-path modules are clean. The audit writer, the
provenance ledger constructor and `registry.call` were each monkeypatched to fail the test if
called; none fired. `app/execution/dispatch.py` is the only module under `app/` that constructs
a `TrustedToolResult` or a `ToolInvocation`.

## 8. Legacy unchanged

All **23** critical files byte-identical to the 13B11J baseline, compared against
`git show c321cb89:<path>`: `server.py`, `registry.py`, `computer/safety.py`,
`resource_manager.py`, `logs/audit.py`, `observability/tracing.py`, the four `brain/` modules,
all eight prior `execution/` modules, `config.yaml`, `app/config.py` and production's
`CLAUDE.md`. The legacy confirmation slice of `server.py` hashes `9c43b6f9…` before and after;
`_pending_confirmations` and `POST /confirm/{request_id}` are both still present and still own
every real confirmation. `registry.call` still has its four callers, all in `app/server.py`. 22
`SAFETY_LEVEL` declarations unchanged. Audit schema still v3; `ProvenanceSource` still 8 members
with no `TIMEOUT`.

`pytest -q` 2892 → **3247 passed, 11 deselected, 0 failures** (355 new: 159 + 102 + 48 + 46).
`tests/execution` 2475 → 2830. Golden 12/20 with the same eight IDs. Legacy probe byte-identical,
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`.

## 9. Two corrections made in the open

**The matrix beat the code** (§3 above): five failing cells, the frozen table won, gate 2 now
refuses only the unexpected-id direction.

**A sealed invariant beat the patch.** The first `confirmation.py` patch used `try`/`except` to
convert internal errors into `DispatchClaimRefused`, which broke 13B11J's
`test_no_bare_except_and_no_except_swallows_a_refusal` (0 `ast.Try` nodes, no `except` in
code-only source). Rather than relax it, the three new methods were rewritten with **no
`try`/`except` at all**: two non-raising helpers ask the questions the raising validators would
otherwise answer, every precondition is checked before use, and each refusal is raised directly
with its kind. The module still has 0 `try` blocks and the 13B11J test passes unmodified.

## 10. Prior tests touched

Three, all strengthened, none a non-activation invariant:

* the pinned public-method set of `ConfirmationStore` grows from 6 names to 9 — still exact;
* `test_no_store_method_exists_for_a_dispatch_result` becomes
  `test_the_dispatch_routes_are_exactly_three_named_guarded_edges`, which pins those three names,
  asserts no generic transition API exists, and additionally asserts each takes `invocation_id`
  and takes neither `event` nor `state` — checks the old test did not make;
* the canonicalizer allow-list of passive `canonicalization_version` declarers gains
  `app/execution/dispatch.py`, exactly as 13B11J added `confirmation.py`. The invariant that file
  protects is untouched.

## 11. Deferred, recorded not resolved

A timed-out confirmation stays in `EXECUTING` — the frozen graph draws only `ok` and `error` out
of execution and §18 says the outcome is unknown, so no terminal transition is invented;
`EXECUTING` is not replayable, but the record is unresolved and a later phase must close it. A
settlement that fails after the executor ran is swallowed so the trusted result is not lost; the
inconsistency is invisible until audit integration exists. `ConfirmationAuthority` is structural,
so a caller could inject a permissive double — the same trust the executor already has.

Carried forward untouched: `browser.open`/`browser.search` versus D-01, confirmation TTL values,
`lane` as an audit field, the redaction secret-key list, `TIMEOUT` as a `ProvenanceSource`, the
P6 unsupported-verb reconciliation, live capability projection, the real adapter, live wiring and
the response-obligation engine. Full list in `DEFERRED.md`.

## 12. Next

**STOP.** P5 is structurally complete and unwired. Per `DEPENDENCY_GRAPH.md` §2 the critical path
is `… → dispatcher (P5) → obligations+response (P6) → pipeline/adapter (P7)`, and
`IMPLEMENTATION_PHASES.md` states the ordering rationale explicitly: *"The dispatcher boundary
comes before the response engine… the trusted result type must exist first, or the response
engine would be tested against a stand-in."* It does exist now.

The next unit is therefore **P6: the obligation engine** (`app/execution/obligations.py`) — the
eleven obligations and the frozen priority already declared as data in `types.py`, selected
deterministically from classifier, route, ledger, result and confirmation state, with CT-011,
CT-012 and CT-018 as its gate. The response builder is the second unit of the same phase and
should be split from it, as P4 was split. The real registry adapter is **not** next: the graph
places it at P9, four phases away, behind the shadow pipeline and the inert conformance suite.

Not started. Do not enable Hermes. Do not start Task 13C. Do not wire the dispatcher into live
requests. Do not call real tools.
