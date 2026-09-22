# Projection admission gap
Existing constituent APIs remain authoritative. CorrelationContext and AdapterRequest are caller-owned; LedgerSnapshot is a read-only view, not a deeply frozen security envelope; PermissionRequest and CanonicalizationResult expose mappings; confirmation records and invocation/result objects carry their existing fields.

V1 requires stable immutable snapshots, exact current/historical linkage and no defaulting of absent authority. No production type was changed to impose a new aggregate representation. No new PipelineInput, ReplayReceipt, caller claimed flag or callback-bearing session was invented.

P-B01 requests one complete field/variant contract, including required/optional rules for confirmation/result/provenance/audit evidence and the admission checks that establish the current turn's association. A copy/freeze mechanism by itself would not resolve which evidence is required or which seam is selected.
