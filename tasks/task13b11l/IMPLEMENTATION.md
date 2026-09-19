# Implementation — Task 13B11L

**Nothing was implemented, and nothing in production was changed.** The task's own §32 decision
gate closed against implementation before any code could honestly be written.

`app/execution/obligations.py` does not exist. Production is byte-identical at
`a0cc4d3cd4b7ca73b9b4a4d92c0cd8270f9a672a`: 25 checked files identical, 0 changed, 0 untracked,
`pytest` 3247 passed / 11 deselected, golden 12/20 with the same eight IDs, legacy probe
`fc68a0b0…`. See `09-production-non-change.txt`.

## What was done

1. **Entry state verified** — production, workspace, Hermes, flags, and the 13B11K bundle
   (50 files / 49 entries / `92fcfff4…` / 0 failures). All 30 sealed bundles re-verified.
2. **Normative sources read** — contract §4, §5, §7, §8, §9, §10, §11, §12, §13, §14, §15, §16,
   §17, §18; CT-011, CT-012, CT-018; the 13B11A plan set; and the validated 13B10C5
   `response-obligation-design.json` and `derive_obligation()`, which are the concept this phase
   transfers.
3. **The two prerequisite checks the task makes blocking** were run first:
   * `OBLIGATION_PRIORITY` completeness — **passes** (see `OBLIGATION_PRIORITY.md`);
   * the §32 classifier/router reconciliation — **fails** (see `P3_RECONCILIATION.md`).
4. **The design that does not depend on the gate was written** — decision input, source
   semantics, contradiction policy, priority proof, test plan — so the unblocking task starts
   from a package rather than a blank page. It is deliberately **not frozen or hashed**, because
   one of its inputs is about to change.
5. **The exact upstream change was specified and verified read-only** — see
   `BLOCKING_CHANGE.md`, simulated in a throwaway process that wrote no file: 21/41 → 41/41 with
   zero collateral movement.

## Why the design was not frozen

The standing method in this series is: freeze and hash the decision table **before** writing the
module. `OBLIGATION_MATRIX.md` cannot honestly be frozen right now, because the set of turns
that arrive as `REPORT_CAPABILITY_UNAVAILABLE` changes the moment the upstream fix lands. Hashing
a table that is known to be about to move would be theatre, and 13B11K's own experience — where
the frozen table caught five wrong cells — is only worth anything if the table is frozen against
settled inputs.

## What an implementer inherits

* the priority is already frozen **in production** as `types.py::OBLIGATION_PRIORITY`, verified
  complete and identical to contract §14.2 — the engine references it, never a second copy;
* the decision inputs are already available as passive P3/P4/P5 outputs, with one gap
  (the value-availability projection) specified in `DECISION_INPUT.md`;
* the contradiction policy and the source mapping are written and argued;
* the test plan names every obligation, every contradiction and every purity proof.
