# Future conceptual graph

```mermaid
flowchart TD
    F[Settled passive shadow facts] --> P[shadow_observation.py]
    P --> R[ShadowObservationRecordV1]
    R --> S[shadow_observation_sink.py]
    C[P1 utc_now: chronology only] --> S
    S --> E[Durable private local P7 evidence]
    S --> Q[Immutable sink receipt]
    E --> M[Future measurement/conformance evaluator]
```

No sink edge to dispatcher, registry, provider/model, audit-v3 or P2. A future controller must reconcile independent attempts/submissions/receipts with the durable set; its scheduler/window/attempt schema is not frozen here. No production consumers/imports/wiring added.
