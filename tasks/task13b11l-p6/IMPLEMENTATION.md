# Implementation — Task 13B11L-P6

Order of work, and the notes worth keeping.

## Order

1. **Entry verification.** Production `ea0cb320…`, parent `9ace0e3a…`, branch main, clean,
   0 untracked, `execution.mode=legacy`, both Hermes flags false. Hermes `2237be35…` clean,
   0 processes, no Ollama on the host.
2. **Evidence verification.** All four relevant bundles verified with `sha256sum -c`,
   0 failures each. One discrepancy found and reported rather than reconciled — see §4.
3. **P5 baseline.** `dispatch.py` byte-identical across production `HEAD`, `a0cc4d3c` and
   the sealed 13B11K bundle (`72155a7d…`). `a0cc4d3c` is an ancestor; only R1 and R2 sit
   between it and `HEAD`.
4. **Normative sources.** Contract §§4, 5, 7, 8, 12–18, 22; the 13B11A plan's component map,
   phases, dependency graph, audit plan and test strategy; the blocked 13B11L design
   documents; the validated 13B10C5 `derive_obligation` and its
   `response-obligation-design.json`; and every production module in `app/execution/`.
5. **The blocker, re-measured.** The real `classify -> route -> lane` chain at `ea0cb320`:
   41/41 unsupported verbs reach `UNKNOWN_ACTION` + `OPERATIONAL`, 20/20 of the formerly
   lost ones among them, at classifier version `"2"`.
6. **The matrix, frozen and hashed with the module provably absent.** `ls
   app/execution/obligations.py` → *No such file*, recorded in the seal.
7. **The module, written against the corrected table.** Agreed on the first run.
8. **Tests, then the full suite, golden, probe and critical hashes.**
9. **One production commit**, then documentation, then the evidence bundle.

## The method earned its keep twice

**Freezing before coding caught two wrong rank predicates.** The first ladder was the
validated 13B10C5 one, and against the repaired P3 outputs it put all 41 unsupported verbs
on rank 1 or rank 4 — *"shall I proceed?"* or *"which one?"* for operations that have no
tool. Contract §13.1 forbids implying an action will happen. The fix was grounded in
production's own rules (the permission engine denies every non-executable action, the
confirmation layer refuses to bind one, §12.3 binds an approval to a target), not in taste.
Had the module been written first, the table would have been written to match it.

**Running the existing suite caught an architectural violation.** The first version imported
`app/execution/confirmation.py` for `ConfirmationState`. Three P4 tests failed, correctly:
phase P5 had gone out of its way to leave that machine with zero importers. The fix was on
this side — the confirmation input became the settled projection
`tasks/task13b11l/DECISION_INPUT.md` had specified a task earlier — and it cost a matrix
re-freeze. **No existing test was relaxed.** Four more constants were renamed for the same
reason: earlier phases' non-activation tests reserve `SUPPORTED_ACTIONS`,
`REFUSAL_STATUSES`, `NON_DISPATCHABLE_ACTIONS`, `NON_CONFIRMABLE_ACTIONS` and
`EXECUTION_STARTED_STATES` as names referenced nowhere else under `app/`.

## Notes worth keeping

* **Assert reason coverage in the freeze script, not only obligation coverage.** An
  obligation can be reachable while one of the states that selects it never appears —
  `external_status_claim_without_trusted_result` was never exercised by 503 rows.
* **Prove a matrix extension is additive.** v1 → v2 added ten rows; the proof is that all
  503 original rows are byte-identical and the header constants are unchanged, not a
  promise.
* **Make the priority claim measurable.** `satisfied(state)` exists so the test can assert
  `min(rank of every rule that holds) == the selected rank`, which is a stronger statement
  than "the first branch that matched was right".
* **Prevent rather than refuse where the type system can.** `executed` is a derived property
  of `result`, so the C-09 contradiction has no code and needs none.
* **Write the reason vocabulary before the obligations feel too few.** Eleven obligations
  cannot distinguish a permission denial from a missing tool from a blocked dispatch; the
  reason can, and that is what let this task stay inside the frozen contract.

## What was deliberately not done

No response builder (`ApprovedOperationalResponse`) — 13B11K reported them separable and
`IMPLEMENTATION_PHASES.md` lists `obligations.py` and `response.py` as two modules. No audit
emission, no provenance write, no permission or confirmation mutation, no dispatch, no
wiring, no Hermes, no contract extension.
