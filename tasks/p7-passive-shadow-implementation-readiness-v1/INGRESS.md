# Ingress implementation inventory

Inputs: exact untrusted request str and exact immutable SettledShadowTurnContextV1. Output: immutable ShadowIngressEnvelopeV1(request, context), exactly two fields. No transport enum, trimming, routing, defaults or synthetic IDs. Reuse existing P1/P2 validation through settled view without creating a store.

Mutable state/side effects: none. Allowed imports: stdlib immutable container support, shadow_context settled view; existing correlation/provenance read-only types only if exact validation requires them. No pipeline/binder/model/scheduler/HTTP/WS object. No registry/dispatcher/provider/framework/audit imports. Expected live consumers: zero; server capture points remain contracts only.

Tests: exact text preservation, same REST/WS logical semantics, invalid context/non-string rejection, same-session snapshot association, immutable graph, zero authority override, no binder invocation, no I/O. B01–B16 original matrix includes future wiring cases; do not claim those from composer unit tests. Static inventory identifies no direct new gate for pure ingress; context must first pass. Rollback: revert future additive ingress commit, then context if needed. No code created while D is blocked.
