# Deterministic derivation

1. Validate V1 input type, JARVIS correlation, same-session snapshot, metadata digest/revision and approval mode. Reject inconsistencies before projection.
2. Feed the unchanged request and existing P2 context to classifier v2 and the P3 router, using the same inputs P7 uses. Use the existing lane output when relevant. No separate verb or target parsing.
3. Accept only a single resolved `OPEN_APP` or `OPEN_URL` route. Match the exact V1 action→capability pair and approved registry key against the passive metadata snapshot. Registry metadata cannot introduce an action.
4. Construct the one reviewed raw argument map. Validate the target predicate in `TARGET_SCHEMAS.md`, then call the existing P3 canonicalizer with the V1 tool key. Require a successful result and exact V1 argument keys.
5. Construct the P4 `PermissionRequest` from the canonical result, route, capability and JARVIS approval mode; leave the actual decision to P7/P4. Emit immutable `BindingProjectionV1` with matching `router_context`.
6. For unadmitted or unresolved routes, emit no `expected` or `permission_projection`, with the supported V1 route context only. The existing P7 stage owns the stop outcome.

The derivation has no clock, random choice, provider, network, mutable global state, registry discovery, audit or provenance write. Identical validated inputs and identical reviewed metadata produce identical output bytes.
