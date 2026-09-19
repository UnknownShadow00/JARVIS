# Task 13B11L — Deterministic Response-Obligation Engine Foundation

**Verdict: JARVIS RESPONSE OBLIGATION FOUNDATION BLOCKED**

Blocked by the decision gate the task itself specifies in §32. The blocker is a real, measured
defect in the P3 foundation, not a limitation of P6. Nothing was implemented and nothing in
production was changed.

| | |
|---|---|
| Production | `a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a` — **unchanged**, 0 dirty, 0 untracked |
| Workspace | `23eb1cfc0f5e7963f38db79c1efc82afda2cf96f` at entry (see §1) |
| Hermes | `2237be355906fbe6065ce1815711eee52b2d646e`, clean, not running |
| Mode | `execution.mode=legacy`, `hermes_brain=false`, `hermes_enabled=false` |

---

## 1. Entry state — verified, with one discrepancy reported

Production matched exactly: HEAD `a0cc4d3c…`, parent `c321cb8958935fa74db0916ec47e56f052410663`
(the 13B11J commit, as required), branch main, 1 worktree, 0 dirty, 0 untracked, 10 ahead of
origin, `execution.mode=legacy`, `approval_mode=balanced`, `dry_run=false`, both Hermes flags
`false`. Hermes `2237be35…` clean, 0 processes, shared Ollama idle.

13B11K evidence: **50 files, 49 manifest entries, `SHA256SUMS` SHA-256
`92fcfff4e2dde49f1b0dd5e34c1d26121f0d95fc57a33ef7ba2fd33404621ba0`, `sha256sum -c` 0 failures** —
exactly the values the task stated. All 30 sealed bundles under `evidence/` re-verified, 0
failures, no prior evidence modified.

**Reported, not auto-reconciled:** the task names workspace `8fded988`. The workspace is actually
one commit further on, at `23eb1cfc`, whose parent *is* `8fded988`. That commit is
`docs: record the 13B11K evidence bundle digest` — the same sealing pattern 13B11J used, and
13B11K's own final report predicted it ("sealed before this line was written"). The tree is
clean, no production artefact is involved, and the named commit is a direct ancestor. Noted here
rather than treated as a baseline mismatch.

## 2. The two blocking pre-checks

Task §9/§47 and §32 each make a check blocking. They were run before any design work.

**`OBLIGATION_PRIORITY` — passes.** 11 `ResponseObligation` members, 11 priority entries, no
member missing, no stray entry, ranks `[1…11]` each exactly once, identical to contract §14.2 and
to the validated 13B10C5 `priority_order`. Not the blocker.

**The §32 classifier/router reconciliation — fails.** This is the blocker.

## 3. The finding

`router.py::UNSUPPORTED_VERBS` (41 verbs) is only consulted for a request the **classifier**
already judged action-bearing: `ACTION_BEARING_CLASSES` gates it, and the router short-circuits
to `PrimaryAction.NONE` with `CLASS_NOT_ACTION_BEARING` before any lexical extraction, so that it
"never contradicts the classifier". A verb absent from `classifier.py::ACTION_VERBS` therefore
never reaches the router's `UNKNOWN_ACTION` verdict.

All 41 verbs were run through the real production chain, read-only:

* **21 / 41** reach `UNKNOWN_ACTION` + `OPERATIONAL` — correct per §13.1.
* **20 / 41** fall through. The task named five; the real gap is four times larger:
  `backup build clear commit download fix flush merge modify patch pull reset restore revert roll
  rollback rotate scale upgrade upload`.

All twenty produce one identical structured signature — `OTHER` / `no_matching_rule` / `NONE` /
`class_not_action_bearing` / no target / `capability_available=False` / `CONVERSATIONAL`. So does
plain conversational input: `"hello there"`, `"thanks"`, `"okay"`, `"hmm"`, `"tell me a joke"`.
Measured overlap: **1 identical signature. Separable by structured state: False.**

Every candidate P6 rule fails, and the failures are not close ones: mapping `OTHER` to
`REPORT_CAPABILITY_UNAVAILABLE` answers "thanks" with a capability refusal; the correct signal
`REQUESTED_OPERATION_HAS_NO_AVAILABLE_TOOL` is never produced for these twenty; a caller-supplied
capability projection would need something to first decide "this is a requested operation", which
is P3's job; forcing the lane in P6 is forbidden by §4.1/§4.2 and task §28; and reading the
request text is forbidden by task §12 and contract §15.3.

## 4. Why this matters beyond P6

Contract §13.1 is NORMATIVE and is being violated today. `"rollback the last deployment"` is
assigned `Lane.CONVERSATIONAL`, and §4.2 permits model prose to be user-visible on that lane. A
request to roll back a deployment currently routes to an unconstrained model answer, with no
obligation, no capability refusal and no operational source lock — the precise failure this
contract exists to prevent.

Nothing is wired, so nothing is at risk today. But the defect has been latent in the P3
foundation since 13B11G, and it existed undetected through four subsequent phases because nothing
asserted that the two lexicons agreed.

## 5. The exact upstream change

Add the twenty missing verbs to `classifier.py::ACTION_VERBS`. `router.py` needs no change.

Verified read-only, in a throwaway process that rebound one frozenset, restored it and asserted
the restoration:

| | before | after |
|---|---|---|
| unsupported verbs reaching `UNKNOWN_ACTION` + `OPERATIONAL` | 21 / 41 | **41 / 41** |
| conversational probes still `CONVERSATIONAL` | 8 / 8 | **8 / 8** |
| control prompts unchanged | — | **8 / 8** |
| prompts whose structured state moves | — | exactly the twenty |

After the fix the chain satisfies §13.1 with no P6 involvement at all: `ACTION_REQUEST` is in
`ALWAYS_OPERATIONAL_CLASSES` → lane `OPERATIONAL`; the router returns `UNKNOWN_ACTION`; the
obligation engine selects `REPORT_CAPABILITY_UNAVAILABLE` at rank 6 from state it already has.

One operator decision is needed: which of the twenty also belong in `SENSITIVE_ACTION_VERBS`. It
changes nothing today — no tool exists for any of them — and everything the day one is added. A
recommended split is in `BLOCKING_CHANGE.md` §3, for confirmation or overrule. Full scope,
alternatives considered, and the re-freeze procedure are in that document.

## 6. Why the matrix was not frozen

Task §46 requires a hashed matrix before implementation. It was deliberately **not** produced.
Every rank-6 row, and every row currently falling through to rank 11, moves when the upstream fix
lands. In 13B11K the frozen table earned its keep by catching five wrong cells precisely because
it was settled before the code; freezing one against inputs known to be in flux proves nothing
and would normalise re-freezing. The dimensions, the coverage requirement and the two open
mapping questions are specified in `OBLIGATION_MATRIX.md` so the unblocking task can freeze it in
one pass.

## 7. What was delivered instead

The complete P6 entry-criterion package, ready for the task after the fix: the obligation
contract and its must-nevers; the decision input mapped to what production already produces, with
the one gap (a provenance availability + trust projection) specified; the obligation → source
mapping; the contradiction policy and corpus; the priority proof; and the test plan — including a
41-verb reconciliation regression test, so this gap cannot silently reopen.

Two new operator questions are recorded rather than decided: whether `PermissionOutcome.DENY`
maps to `REPORT_CAPABILITY_UNAVAILABLE` or needs a twelfth obligation (a contract extension under
§6.2, not an implementation choice), and whether `TIMEOUT` belongs in the `REPORT_TOOL_ERROR`
family.

## 8. Non-change, measured

25 files byte-identical to `a0cc4d3c` — `server.py`, `registry.py`, `computer/safety.py`,
`resource_manager.py`, `logs/audit.py`, `observability/tracing.py`, the four `brain/` modules, all
eleven `app/execution/` modules, `config.yaml`, `app/config.py` and production's `CLAUDE.md`.
`app/execution/obligations.py` does not exist. `pytest` **3247 passed, 11 deselected, 0 failures**.
Golden **12/20**, same eight IDs. Legacy probe
`fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, matching the sealed digest.
Hermes never started, no inference performed.

## 9. Next

**STOP.** The next unit is not P6.

1. **Unblock P3** — the twenty-verb classifier lexicon fix in `BLOCKING_CHANGE.md`, after the
   operator answers the sensitivity question. One frozenset, one sealed module, the standing
   freeze-and-hash method, and a new regression test asserting the two lexicons agree.
2. **Then P6, unit 1** — the obligation engine, freezing the matrix against the corrected inputs.
3. **Then P6, unit 2** — the deterministic operational response builder producing
   `ApprovedOperationalResponse`, split from the engine exactly as P4 was split.

Do not enable Hermes. Do not start Task 13C. Do not wire anything into live requests. Do not
build user-facing response text.
