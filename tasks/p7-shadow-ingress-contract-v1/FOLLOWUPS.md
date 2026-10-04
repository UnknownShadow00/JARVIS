# Open decisions, ordered for a complete V1 freeze

1. **Ingress coverage owner:** approve an attachment design that covers REST and WS streaming exactly once while preserving one-branch/legacy behavior; determine whether 13B11A's `_process` location is narrowed or an additional capture point is authorized.
2. **P1/P2 source:** assign live session/turn ID minting, trace association, session lifetime, P2 snapshot owner and classifier context derivation. Current ingress does not provide these.
3. **P7 adapter state:** define model-free shadow result and optional separately authorized live recording source without synthetic model output or changing `run_recorded_turn` silently. Freeze exact composer module/path and scheduling/timeout mechanism.
4. **Evidence semantics:** choose a shadow observation format/writer distinct from executed audit truth or implement the already-specified F-AUDIT-01 v3 correction plus failed-stop representation; freeze retention and failure behavior.
5. **CT claim:** distinguish counterfactual shadow assertions from CT-001's final user-visible requirement. Then freeze measurement window/thresholds and provider identity separately before scored shadow.
