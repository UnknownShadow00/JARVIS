# Existing P1 authority

Imports from `app.execution.correlation`: `CorrelationContext`, `SessionId`, `is_well_formed_id`, `new_session_id`, `new_turn_context`. Existing `new_turn_context` calls existing `new_turn_id`; runtime ID values remain plain strings under the existing `NewType` family. No ShadowSessionId, ShadowTurnId or third correlation scalar exists.

Owner construction invokes `new_session_id()` once. Each explicit operation invokes `new_turn_context(owner_session)` once. No identifier can be passed into the owner or turn API. Exact canonical correlation type and well-formed plain-string IDs are checked; invocation/confirmation fields must remain None for this initial turn. Trace does not participate in minting.

Direct settled-value construction checks shape and association, and is not authentication. Like the existing P1/P2 foundations, this is a trusted-process passive primitive, without a new secret token, caller flag or hostile-Python security claim. Future transport validation remains D01/D02. P1's old trace-reuse docstring is unchanged and superseded for this unit by frozen operator A8.
