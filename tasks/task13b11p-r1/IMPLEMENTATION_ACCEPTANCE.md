# ACCEPTANCE CRITERIA FOR THE P7 PASSIVE PIPELINE IMPLEMENTATION

The admission contract is frozen; nothing is implemented. The next approved unit is the
resumption of Task 13B11P, P7 PASSIVE PIPELINE IMPLEMENTATION, against the frozen P7
pipeline contract, this admission contract, recorded Hermes outputs and static/test-double
projections only. Re-verify the production parent and every digest below before starting.

## Scope

- Implement `PipelineStop` exactly as task13b11o-r1/PIPELINE_FAILURE_MODEL.md freezes it
  (F-TYPE-01: seven fields, two closed enums, 16 stages, 23 reasons), and `RecordedTurn`
  exactly as TURN_INPUT_SCHEMA.md freezes it (21 fields, frozen, slotted, no callable).
- Implement the single callable `run_recorded_turn(turn: RecordedTurn) -> TurnOutcome` and
  the frozen stage walk. `TurnOutcome` is the permitted alias, not a new authority class.
- Reuse every existing type and engine. Do not duplicate a P0 type, the policy table,
  classifier rules, lane policy, canonicalization rules, P6 priority, P6 contradiction
  checks or any response template.

## Hard requirements

- `RecordedTurn` must contain no callable, store, clock, executor, dispatcher, session
  object or authority boolean. A reviewer must be able to establish the zero-execution
  invariants from the type declaration alone.
- The derived `AdmissionMode` must have no constructor field and no setter.
- `confirmation_claimed` must be derived exactly as RESULT_REPLAY.md specifies. Deriving it
  from `invocation.confirmation_id` is a failure, not a near miss.
- Mode B must have no code path to S09. Mode A with an actual `ALLOW` and no result must
  stop at `S09_RESULT` / `result_invalid`.
- No branch may construct a `TrustedToolResult`, call `claim_for_dispatch`, `confirm`,
  `settle_success`, `settle_failure`, `create_confirmation`, `build_invocation`, any
  `new_*_id`, any ledger mutation or any audit writer.
- Pre-S09 stops: `executed=False`, `result=None`. Post-S09 stops in mode C: retain the
  admitted result and set `executed = result.executed`. Never emit `executed=True` with
  `result=None`.
- Zero importers of the new module under `app/` and zero call sites. The legacy request
  path in `app/server.py` and `app/brain/router.py` stays byte-identical, `execution.mode`
  stays `legacy`, both Hermes flags stay false.

## Evidence the implementation must produce

- Agreement with all 32 rows of `admission-matrix.json`, digest
  `6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434`, re-verified before
  any code is written. Freeze the fixture values first. Where the module and the table
  disagree, the table wins and the disagreement is reported.
- Preservation of all 47 rows of task13b11o-r1/UPDATED_PIPELINE_MATRIX.md (digest
  `b45a373da04d687d43ab2df60bcdcc6c9da46c769528046f796114830bf86d89`), the six cases in
  `contradiction-corpus.json` (digest
  `d1f8e74966a934f3967cdfea71d9c968e6a058966e6cfa3b7798e265b0e5b012`) and the prior 18 CT
  categories.
- A measured executor-call count of 0 and a measured dispatcher-entry count of 0 across
  every fixture, plus a purity proof: no network, no process, no file I/O, no clock read.
- Proof that each of S-01…S-20 in SECURITY_INVARIANTS.md holds, distinguishing the
  structural ones from the checked ones.
- Full regression unchanged: 5468 passed / 11 deselected / 0 failed as the parent baseline,
  golden 12/20 with the same eight ids, legacy probe
  `fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291`, and the critical
  production files byte-identical.
- One focused production commit, files-only where possible. No existing non-activation
  assertion may be relaxed; an update may name only the new passive module and must
  preserve zero live wiring, with explicit justification.

## Out of scope for that task

F-MAP-01 binding derivation; any live executor, isolated P5 continuation API or executor
callback seam; F-FALLBACK-01 live failure response; F-AUDIT-01 schema-v3 correction;
F-REPLAY-01 transport loss; the remaining P7 server/API/UI and shadow boundary; P8; 13C;
Hermes enablement; any policy, schema, TTL or `execution.mode` change; replay of a
non-dispatchable-action result (F-P7R1-02). No push, and no full-P7 or P8 completion claim.
