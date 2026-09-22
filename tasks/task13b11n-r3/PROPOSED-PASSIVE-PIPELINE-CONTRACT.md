# Proposed passive pipeline contract
PROPOSED — NOT FROZEN.
REQUIRES OPERATOR APPROVAL for authority-bearing composition/guard/constraint choices below. Naming and routine serialization can be settled during a dedicated contract task; this draft is not authorization to change policy.

## Candidate scope
Canonical component remains app/execution/pipeline.py. A separately frozen recorded-input API could compose real P0-P6 components with the completed adapter, without importing server/model/registry, emitting audit or touching live state.
This draft intentionally does not declare handle_turn complete, full P7 exit achieved, or any new runtime mode active.

## Candidate inputs
Use existing CorrelationContext; AdapterRequest plus raw canonical recording, caller timestamp and proposal IDs; a session-matched LedgerSnapshot; an explicitly supplied RouterContext; test-owned confirmation/executor boundaries only if the final scope authorizes stateful simulation.
A raw dict of permission/confirmation/trust booleans must not substitute for component outputs. Caller-held policy constraints need explicit evidence provenance and ownership.
Avoid duplicating ClassifierContext, LaneSignals, PermissionRequest, ObligationState or ResponseBuildInput. Freeze one projection function for each linkage, with fixture cases proving its source.
Question: should the minimal unit return a pure candidate state/outcome without invoking injected effects, or run an explicit in-memory simulation through the actual TrustedDispatcher? Both need exact input/output contracts; arbitrary callbacks cannot establish passivity on their own.

## Candidate output
An immutable TurnOutcome discriminated by existing Lane, containing exactly the appropriate existing ApprovedOperationalResponse or ConversationalResponse, plus passive audit records/projections and independently identifiable synthetic dispatch evidence where applicable.
An OPERATIONAL branch must never accept ModelDraft. No duplicate trusted-result or permission type. ModelDraft may stay an internal untrusted artifact or a separately handled digest-only audit reference.
Exact fields, null rules and error variants remain UNFROZEN, especially how a builder failure is represented without relabeling it as a successful approved response.

## Required decisions before freeze
1. Bind request model/turn/session/timestamp, snapshot identity and proposal IDs consistently.
2. Define exact route-to-capability-to-tool and argument binding from existing P3/P4/canonicalization contracts. Do not add capabilities or change browser D-01.
3. Define zero/multiple proposal disposition without selecting, partially executing or treating parser acceptance as permission.
4. Derive final LaneSignals from deterministic state; presence of model proposals may force operational handling under existing policy but cannot grant authority or downgrade a lane.
5. Derive satisfied_constraints only from JARVIS-owned evidence. Preserve DENY and REQUIRE_CONFIRMATION without override.
6. Bind current/historical result, invocation and provenance identities exactly as required by response.py.
7. Freeze failure outcomes and passive audit-event mapping. Preserve ModelDraftAuditRef behavior without raw reasoning retention.
8. State whether any existing non-activation allowlist must gain exactly one passive importer; keep live consumers zero.

## Proposed freeze gates
Static schema/corpus first; synthetic adversarial cases and 18-test conformance mapping; exact parent/source hashes; no arbitrary numeric TTL/resource bounds; no real tool or provider; independent revert; immutable evidence seal.
