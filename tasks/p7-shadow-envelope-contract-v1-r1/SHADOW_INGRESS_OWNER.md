# Pure owner

Future `app/execution/shadow_ingress.py` composes `request: str` plus `context: SettledShadowTurnContextV1` into ShadowIngressEnvelopeV1. It owns data validation/composition only. It does not mint IDs, resolve a continuation handle, read a store, read a trace context variable, choose mode, derive a binding, invoke the pipeline or schedule anything.

The context owner supplies settled association; the server supplies accepted untrusted text. Both are required. No default session, turn, empty snapshot or fake adapter response is created. No module is implemented in this freeze.
