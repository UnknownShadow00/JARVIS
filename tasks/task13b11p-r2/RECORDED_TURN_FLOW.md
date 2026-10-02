# RECORDED-TURN FLOW — specified, not implemented

The flow below is the frozen composition of 13B11O-R1 `UPDATED_GUARD_ORDER.md` and
13B11P-R1 `S08_S09_CONTRACT.md`. It is recorded here as the implementation target. No code
exists.

```
RecordedTurn (immutable; no callable, store, clock, executor, dispatcher or authority bool)
  |
  S01 admission: type identity, correlation validity (raise on malformed), derived mode,
      turn/session association, mode-C preconditions C-00/C-00a/C-00b
  S02 classifier.classify(request, classifier_context)            version "2", unmodified
  S03 router.route(classification, router_context)
  S04 lane.explain(request_class, turn.lane_signals)
  S05 hermes_adapter.parse_recorded_response(recording, adapter_request,
          created_at=recorded_at, proposal_ids=proposal_ids)      all-or-nothing
  S04' lane.explain again, with tool_proposal / tool_result / confirmation_required
       derived from admitted facts only
  deterministic branch: UNKNOWN / MULTI / unresolved -> existing P6 terminal
                        NONE + 0 proposals -> conversational or non-action P6
                        NONE + proposals   -> STOP(unexpected_proposal)
  S06 cardinality -> association -> projection -> capability -> tool identity
      -> canonicalize(proposal) -> full canonical-argument equality
  S07 permissions.decide(permission_projection)       DENY -> existing P6 terminal
  S08 confirmation:  mode A ALLOW -> eligible         mode A REQUIRE_CONFIRMATION -> waiting
                     mode B -> waiting or STOP        mode C -> pass through
  S09 result:        mode A eligible -> STOP(result_invalid)   (no executor exists)
                     mode B -> unreachable
                     mode C -> C-01..C-08 then continue
  S10 provenance selection (read-only)
  S11 obligations.derive / require
  S12 response.build
  S13 internal audit projection (never emitted)
  |
  ApprovedOperationalResponse | ConversationalResponse | PipelineStop
```

Three properties of this flow are the reason it is safe, and all three come from the input
type rather than from a guard: the dispatcher is never entered because none is reachable;
no `TrustedToolResult` is ever constructed because the pipeline is not the dispatcher; and
re-running the same `RecordedTurn` is byte-equal because both timestamps are admitted data.

Mode B's row is the blocked one. Everything else is implementable exactly as written once
P-B02 is resolved.
