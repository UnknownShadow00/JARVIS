# PIPELINE API — resolved, not implemented

Canonical module: `app/execution/pipeline.py` (`tasks/task13b11a/TARGET_COMPONENT_MAP.md:31`,
"Integration boundary"). Absent at the verified baseline and still absent. The illustrative
`app/brain/pipeline.py` in the task prompt is **not** the plan's path and was not used.

```
run_recorded_turn(turn: RecordedTurn) -> TurnOutcome
```

One positional argument of exactly type `RecordedTurn`. No second parameter, no keyword
collaborator, no default-constructed dependency. `TurnOutcome` is the alias 13B11P-R1 and
13B11O-R1 already permit: `ApprovedOperationalResponse | ConversationalResponse |
PipelineStop`. A pure function of its argument: no store, no clock, no executor, no
network, no I/O.

Unblocked and ready to implement as frozen: the 21-field input table minus field 15, the
derived three-mode discriminator, `PipelineStop` (7 fields, 16 stages, 23 reasons), the
S01–S13 walk, the proposal guard, S09, and every mode-A and mode-C rule.

Blocked: field 15 and therefore mode B. See BLOCKER_ANALYSIS.md (P-B02). No signature is
committed to production until that field's type is re-frozen, because the input type is
part of the public API and re-freezing it after writing the module would invert
freeze-first discipline.
