# Implementation — passive permission policy

Production commit `52c5da5d7a5d304acd4088b11e1f9bd509067069`, parent
`03cab4960156220fe9b6c3a444fa7a41265c01e0`. Five files added, 2,678 insertions, **0 deletions,
0 modifications**.

## 1. What was built

`app/execution/permissions.py` (657 lines): the operator-signed matrix as frozen data, plus one
pure function that reads it.

```python
decide(request: PermissionRequest) -> PermissionDecision
```

No other production module imports it. It is phase P4 of `IMPLEMENTATION_PHASES.md`, split as the
review recommended: the **permission engine only**. The confirmation manager, which needs a clock
and a store, is not in this commit.

## 2. Order of work

The policy table was written and hashed **before** the module existed; the recorded check shows
`ls app/execution/permissions.py` returning "No such file or directory" at that moment.

1. Baseline measured first-hand on a clean `03cab496`: 2113 passed, golden 12/20, probe
   `fc68a0b0…`, 22 critical-file hashes.
2. Six design documents and `policy-table.json` written and hashed.
3. Only then the module, then the tests.

## 3. Shape

Structural gates run **before** any table lookup, so a route that carries nothing executable, an
unavailable action or an unresolved target can never reach a permissive row. Eleven steps, frozen,
in `DECISION_API.md`. Only the last step can return `ALLOW`, and only from a row that declares it —
which is why exactly one `PermissionReason`, `ROW_MATCHED`, can accompany a non-`DENY` outcome, and
why that is asserted by test.

## 4. Decisions taken during implementation, and why

**Capability keys, not `PrimaryAction`.** The review found the five routed actions cannot separate
`files read` from `files move`. `PrimaryAction` was **not** extended (§10). Rows are keyed by a
capability identifier from the real inventory, e.g. `files.move`, `shell.execute`.

**`primary_action` is optional.** This surfaced during implementation, not in the plan: the routed
vocabulary covers five operations while the inventory has thirty-one capabilities, so there is no
`PrimaryAction` member for closing an application, fetching a URL or running a shell command. A
required field would have forced callers to pass a wrong one. `None` means "this capability was not
reached through a routed action". It is not a bypass: when an action *is* supplied every structural
gate applies and the action and capability must agree **in both directions**, and the three
unavailable actions deny against any capability whatsoever.

**The table is a frozen module tuple, not `config/permissions.yaml`.** The plan proposes YAML and
the task authorizes it "only if required". A YAML table means file I/O at import inside a component
whose safety argument is purity. Same choice as the router's lexicon in 13B11H, and recorded in
`POLICY_TABLE.md` as an explicit deferral. The table is still versioned data, hashed, and asserted
against the frozen JSON by test.

**`DenialKind` was added after a defect was found in the first draft.** `messaging.system_egress`
and `resource.control` were denying with reason `CAPABILITY_NOT_REGISTERED`, which is false — those
surfaces exist, and D-06/D-07 forbid them. The two reach different contract obligations: an absent
capability is `REPORT_CAPABILITY_UNAVAILABLE` (§13.1), a prohibition is a refusal. The frozen table
was amended to carry `denial_kind`, re-hashed, and the amendment recorded in `policy-table.json`
itself with the previous digest, what changed, why, and that **no scored test existed yet**. No
row's class, outcome, registration or constraint moved.

**D-04 is encoded as a hard precondition, not a note.** `web_search.fetch` requires the constraint
`EGRESS_TARGET_POLICY`. Until some component discharges it the row denies, so the default state of
an arbitrary caller-supplied fetch is refusal. No networking code was written, and the engine never
inspects a URL — even a public one denies without the constraint. The future validator dependency is
documented rather than faked.

**Overwrite state must be known.** `files.move` with `overwrite=None` denies
(`OVERWRITE_STATE_UNKNOWN`) rather than assuming the safe case. D-03 says a reversible move must
never authorize an overwrite; assuming `False` when the caller does not know would do exactly that.

## 5. Reuse, not duplication

`PermissionClass` and `PermissionOutcome` are imported from `app/execution/types.py` and neither was
extended. There is no parallel `CONFIRM` outcome: the production member is `REQUIRE_CONFIRMATION`,
and the plan's `ALLOW | CONFIRM | DENY` wording is a drift recorded in the review, not followed.
`ModelDraft` and `ToolProposal` are imported only so that passing one as authority raises.

## 6. Results

462 new tests, all passing. `pytest -q` 2113 → **2575 passed, 11 deselected, 0 failed**;
`tests/execution` 1696 → 2158. **40/40** rows decide exactly their signed-off outcome. Golden
unchanged at **12/20 with the same eight failures**. Legacy probe **byte-identical**, `fc68a0b0…`.
22 critical files byte-identical. 360 requests under a CPython audit hook produced **zero**
sensitive events; 21 sweeps identical; 500 repeated calls gave one output. 0 importers, 0 call
sites, 0 references to any public symbol anywhere under `app/`.
