# Implemented passive API

Canonical app/execution/pipeline.py. Public definitions: run_recorded_turn, RecordedTurn, SettledConfirmationProjection, AdmissionMode, PipelineStage, PipelineStopReason, PipelineStop, TurnOutcome. Single entry run_recorded_turn(turn: RecordedTurn) -> TurnOutcome. No exports added elsewhere.

RecordedTurn has exactly the final R6 21 fields, in order and with frozen defaults. Projection has exactly 16 fields, frozen/slotted, no declared methods. Owner/test boundary supplies recursively immutable projection data; pipeline validates/consumes it without a factory or confirmation import. Exact identity on the three mode discriminators; look-alikes/subclasses fail. Input type/correlation misuse raises at the frozen caller boundary; semantic failures yield non-renderable PipelineStop.

A: no confirmation/invocation/result. B: settled projection only. C: invocation+exact TrustedToolResult only. Other five combinations reject. No callback, dispatcher, executor, store, registry, clock, live session or authority boolean. Existing executor string on result is descriptive. ModelDraft/ToolProposal are untrusted.

PipelineStop has the unchanged seven fields, sixteen stages, twenty-three reasons. Before S09 association, stops retain no result and executed=False. Post-admission downstream failures retain the existing result and its executed flag. No new trusted result or invocation is constructed.

Classification, route, lane, canonicalization, permission, obligation and operational response come from existing passive owners. S08 consumes the projection: B-01 session, B-02 pending, B-03 freshness, B-04 audit/child association, B-05 no invocation, B-06 exact binding+actual requirement, B-07 actionable. Mode B only waits or stops. S09 checks recorded C association; no execution edge.

Option A: actual NONE + zero proposals + Mode C -> S06_PROJECTION/projection_invalid. NONE + nonzero -> S06_CARDINALITY/unexpected_proposal. Neither reaches P6 or S09. Conversational text remains MODEL_RAW; operational responses come only from response.build. No prose fallback.
