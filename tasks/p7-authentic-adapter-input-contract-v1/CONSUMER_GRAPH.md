# Canonical parser and external origin association

```mermaid
flowchart TD
    E[Shadow Envelope: exact request and Context association] --> R[JARVIS AdapterRequest and build_request]
    R --> T[Future separately authorized provider transport]
    T --> N[Future approved faithful wire normalization if required]
    N --> C[Canonical recording plus same-turn caller metadata]
    C --> P[P7 RecordedTurn: canonical parser at S05]
    B[Independent Binding Projection V1] --> P
    P --> O[Settled passive P7 observation facts]
    O --> D[Unchanged ShadowObservationRecordV1]
    D --> S[Unchanged D04 evidence sink]
    T --> A[Future associated origin and attempt evidence]
    P --> A
    S --> M[Future controller reconciles exact stored set]
    A --> M
```

No provider/client/server->ToolProposal factory edge, no binding->fake proposal, no sink->authenticity decision, no dispatcher/audit/P2/provider activation. Future transport/normalizer/collector paths are conceptual and not implemented or assigned modules here.
