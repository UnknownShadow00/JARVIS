# STAGE COMPOSITION — not implemented

The 21-row frozen guard order of 13B11O-R1 `UPDATED_GUARD_ORDER.md` is the normative
composition and is reproduced nowhere here to avoid a second, drifting copy. This task
added no stage, removed none, and reordered none.

Two composition facts were established while resolving the canonical module:

- **Stage attribution is ownership, not traversal count.** `PipelineStage` is a closed
  identifier. A mode-C turn refused by C-00a stops at `S01_INPUT` without walking S02–S08,
  which is the honest attribution of a shape failure and not a reordering.
- **Mode narrows reachability; it never skips a gate.** Mode B removes the S08→S09 edge.
  Mode C's C-04…C-07 run *after* S02–S07 have already decided from the original request, so
  a replayed `SUCCESS` or a supplied `ALLOW` cannot backfill an earlier gate.

Instrumentation the implementation must provide, per §22: every corpus row must be able to
prove the stages reached, the guards evaluated, the stop stage and reason, and the
downstream continuation. The natural shape is an opt-in trace list the test passes in and
the production path writes nothing to by default — it must not become a mutable field on
`RecordedTurn`, which is frozen and must stay free of machinery.
