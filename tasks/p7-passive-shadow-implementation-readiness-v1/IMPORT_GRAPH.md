# Proposed bounded import graph

```mermaid
flowchart TD
 context[shadow_context] --> p1[P1 correlation]
 context --> p2[P2 store and snapshot]
 ingress[shadow_ingress] --> settled[context immutable view]
 observation[shadow_observation] --> p1
 observation --> p0[P0 enums and response data]
 observation --> terminal[P7 terminal types only]
 observation --> binding[BindingProjectionV1 type only]
 observation --> route[RouteResult type only]
 observation --> permission[PermissionDecision type only]
```

No new file or edge has been implemented. Context→ingress is a data handoff; only ingress may import context after approved implementation. No reverse dependency or package re-export. Observation reads settled types but never calls their engines. No server/API/UI/Hermes/evaluator/scheduler consumer, and no sink/provider/audit/dispatcher/registry edge. The proposed graph still requires the named source-gate transitions; type-only use is not exempt from current tests.
