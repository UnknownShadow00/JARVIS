# Structural isolation

The future shadow composer receives passive value inputs only: normalized envelope, classifier/P2 projection, `BindingProjectionV1`, recorded adapter values, and `RecordedTurn`. It must not import or receive `dispatch`, executor, live `registry`, `registry.call`, tool handler, confirmation machine/store/claim, provider client by default, audit operational writer or live provenance ledger writer. `run_recorded_turn` is passive and has no dispatch step. A `shadow=True`/`dry_run=True` flag with executable objects still reachable is insufficient.

Legacy remains allowed to execute through its existing path; the zero-side-effect invariant applies to the *new shadow branch*. Future static import scans, runtime sentinels and CPython audit-hook tests must distinguish those paths and prove zero new-path dispatch/tool/registry/confirmation/provenance/audit-truth mutations.
