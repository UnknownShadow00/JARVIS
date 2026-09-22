# Canonical identity and unresolved callable boundary
Canonical module: app/execution/pipeline.py (13B11A TARGET_COMPONENT_MAP, Integration boundary). It is absent at verified production HEAD. P6 plus the recorded adapter are predecessors. Later consumers are the remaining P7 server/API/UI and shadow boundary; P8 waits on full P7 exit.

The proposed plan entry handle_turn(session, text) is explicitly conceptual in task13b11o/PIPELINE_IDENTITY.md:7. A session object would not itself satisfy this task's no-hidden-store requirement. V1 P7_PIPELINE_CONTRACT_V1.md:11–24 specifies constituent boundaries and the output alternatives, but no complete passive callable signature or required/optional input set replacing that session parameter.

Resolved: guard inputs are exact (PROPOSAL_GUARD.md); seven PipelineStop fields/enums are exact; output may use ApprovedOperationalResponse | ConversationalResponse | PipelineStop. Function spelling or choosing that permitted alias is not the blocker.

Unresolved admission semantics: how a caller presents the current invocation/result, before/after confirmation records or claim evidence, selected provenance evidence and internal audit candidate as one turn's inputs; which are required together, which absence is valid, and what is accepted as the S08 eligible handoff. The referenced original STATE_PROJECTIONS.md:3 explicitly says NOT FROZEN as a whole pipeline input. V1 does not supply the replacement field/variant table.

The distinction matters: receiving a completed replay is not receiving a pending request plus an executor dependency. A ConfirmationRecord snapshot alone is explicitly not approval. P7 must not create a new claimed boolean, synthesize a claim or infer execution from dataclass possession. The existing APIs supply constituent types but no whole-turn replay admission API.

Task §5 therefore blocks the whole pipeline before coding. This finding does not make the pure proposal equality guard impossible and does not question the four resolved decisions. Implementing only that subset would not meet the requested whole-pipeline acceptance.
