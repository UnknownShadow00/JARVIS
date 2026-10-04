# ShadowMeasurementRecordV1 feasibility — not frozen

No complete immutable record/schema is approved here. Table entries distinguish available facts from missing observations, rather than assigning guessed values.

| Proposed fact | Actual source at pinned Core | Can derive truthfully now? |
|---|---|---|
| session/turn correlation | input RecordedTurn.correlation; future Context V1 | yes for admitted input; pre-context failure lacks it |
| trace association | future envelope.context.transport_trace_id | yes once captured; not a P7 outcome field |
| stop stage/reason | PipelineStop.stage/reason (pipeline.py:129-156) | yes only for that alternative |
| response alternative | exact type of TurnOutcome | yes: approved operational / conversational / stop |
| candidate approved response presence | exact ApprovedOperationalResponse type | yes; candidate status is not user-visible success |
| lane | response.lane; optional stop.obligation_state.lane | partial; early stops have none |
| obligation | ApprovedOperationalResponse.obligation | yes there; conversation has no obligation; stop.state is not a selected decision |
| proposal match | guard local flow (:231-277, :457+) | no general returned match status; some stop reasons show a mismatch, but cannot imply all other outcomes matched |
| permission outcome | local PermissionDecision; some stop.obligation_state | no uniform returned value; response drops decision |
| legacy/new lane and route agreement | legacy intent + deterministic P3 route require correlation and comparison taxonomy | not defined by existing TurnOutcome; legacy intent is not P3 lane/action |
| would-be dispatch count | initial successful permission can stop at S09_RESULT, but details vary | needs approved interpretation/source; not equal to actual dispatch |
| zero-execution counters | historical R8 test profile/audit-hook artifact | historical fixture evidence only; outcome.executed=False is not a call counter |
| timestamp/duration | caller recorded_at/evaluated_at, response.created_at; separate tracing wall/perf clocks | timestamps exist, but no frozen shadow interval/queue clock semantics; omit rather than reinterpret |
| measurement failure/drop/coverage | no production owner/writer currently | missing; cannot treat missing records as success |

Sources: pipeline.py:104-156,216-231,345-451 and types.py:317-352; R8 zero-execution-proof.json; 13B11A PRODUCTION_INTEGRATION_PLAN §7. Canonical test proof used profiling and audit hooks, not a production PipelineOutcome observation object. ApprovedOperationalResponse has text/turn/obligation/source/provenance IDs/time/lane; it has no permission, proposal-match, call counts or legacy comparison. ConversationalResponse lacks even session_id; retain input association, do not infer it from model text.

Decision needed: approve a scoped outcome-observation contract with explicit unavailable fields and separate evidence gaps, or define an independently observed stage/measurement boundary before freezing the full schema. The second is recommended for formal P7 evidence. Neither authorizes policy changes, forged events, global tracing hooks in a live server or pipeline implementation changes.
