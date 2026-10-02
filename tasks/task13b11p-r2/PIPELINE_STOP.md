# PIPELINE STOP — specified, not implemented

`PipelineStop` is frozen by 13B11O-R1 `PIPELINE_FAILURE_MODEL.md`: seven fields
(`correlation`, `stage`, `reason`, `executed`, `result`, `obligation_state`,
`component_reason`), 16 `PipelineStage` members, 23 `PipelineStopReason` members. Both
enums stay **closed**. This task added no reason, no stage and no field, and wrote no code.

13B11P-R1 established that no new reason is needed: all seven admission failure categories
map onto the existing 23. F-P7R1-03 stands — the reasons remain coarse, several distinct
guards share one reason, and tests assert stage *and* guard identity rather than a finer
stop field. For confirmations the coarseness is also the desired property: a
distinguishable refusal would be an existence oracle.

Retention rule to implement, reconciling the two frozen statements about pre-dispatch and
post-attempt stops:

| Stop | `result` | `executed` |
|---|---|---|
| any stop in mode A or mode B | `None` | `False` |
| mode C, stop at `S01_INPUT` or any stage before S09 passes | `None` | `False` |
| mode C, stop at `S09_RESULT` on an association failure | `None` | `False` |
| mode C, stop at `S10`–`S13` after S09 passed | the admitted `turn.result` | `turn.result.executed` |

`executed=True` with `result=None` is never emitted: the recorded-only core cannot witness
an executor entry and must not fabricate that state (F-REPLAY-01 stays deferred).
`component_reason` carries only existing owner codes — declared adapter error codes, a
replayed result's own `error_kind`, or a P6 contradiction code — and never a
pipeline-invented string.
