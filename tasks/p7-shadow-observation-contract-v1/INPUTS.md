# Allowed settled handoff

The conceptual producer accepts exactly these semantic inputs; unavailable optional observations are explicitly supplied as None. No input omission creates a default success.

| Input | Existing type/value | Source requirement |
|---|---|---|
| correlation | CorrelationContext | Context V1 owner; authoritative same session/turn; initial child IDs absent |
| transport_trace_id | str or None | already-settled Context V1 observational association |
| transport | literal http or websocket | JARVIS-owned ingress observation using server.py's existing trace vocabulary, settled before handoff |
| admission_mode | AdmissionMode.INITIAL_TURN | actual evaluator's accepted pipeline mode, not a client flag |
| terminal | existing TurnOutcome | actual same-turn P7 return; not a rebuilt/fake result |
| binding | BindingProjectionV1 or None | actual already-created V1 binder output for this attempt; no producer binder/snapshot call |
| route | RouteResult or None | actual already-settled P3/P7 route for this attempt; no request recognition |
| proposal_count | nonnegative exact int or None | count of successful adapter parser output, settled externally; not raw JSON claim |
| proposal_match | exact bool or None | actual complete guard observation, settled externally; no producer comparison |
| permission | PermissionDecision or None | actual P4 decision returned for this attempt; no permission projection treated as a decision |

The evaluator is the association owner for facts whose existing types lack session/turn fields (binding, route and PermissionDecision). It must establish their common attempt before handing them over. Producer checks explicit IDs in terminal and rejects disagreements among duplicate settled values, but cannot authenticate the origin of a manually constructed dataclass. Type identity or a hash is not origin proof. Future evaluator authenticity/collection is still separately frozen before implementation; absent observations remain None.

Context/envelope are provenance of identity/trace, not required whole input objects. The producer receives their minimum immutable association rather than raw request, LedgerSnapshot, HTTP/WS object or mutable store. ModelDraft/ToolProposal lists need not enter this producer: count/match are enough. No raw recording, model name, prompt, tool schema, legacy reply, callable, service locator, result/confirmation store, registry/provider handle or timing fact is an input.

Existing terminal response objects contain text/time, and RouteResult contains target/clauses; these fields are not read, hashed, serialized or retained. No to_mapping call blindly serializes a source object. PipelineStop.result must be None and executed exactly False; any obligation_state.result must be None and confirmation_claimed False. No P5 result object is accepted as inert evidence, even when its executed flag is False.
