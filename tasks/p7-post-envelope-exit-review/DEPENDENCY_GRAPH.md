# Remaining dependency graph

```mermaid
flowchart TD
  A[Context V1 frozen] --> B[Envelope V1 frozen]
  B --> I[Context and ingress implementation]
  H[Continuation and lifecycle decisions] --> I
  T[Exact test exception authorization] --> I
  I --> E[Shadow evaluator and server integration]
  M[Adapter input and provider decision] --> E
  S[Scheduling and resource isolation] --> E
  O[Observation source and measurement contract] --> E
  E --> C[CT-001 and CT-013 integrated evidence]
  E --> W[Approved measured shadow window]
  E --> R[Rollback drill]
  C --> P[Formal P7 exit review]
  W --> P
  R --> P
  P --> P8[P8 entry remains blocked]
```

F-MAP-01 producer/registry snapshot and recorded P7 are already implemented. They do not provide live adapter data or measurement delivery. No graph edge authorizes implementation. The old single _process collection point is refined by the explicit REST/WS contract, but evaluator placement still requires a scheduling decision. Existing server/API/UI dependency remains, including how a JARVIS-issued continuation handle is conveyed.
