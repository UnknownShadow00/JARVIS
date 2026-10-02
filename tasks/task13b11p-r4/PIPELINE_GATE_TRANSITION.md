# Pipeline absence → presence / non-activation

BEFORE IMPLEMENTATION: app/execution/pipeline.py must be absent. R3 and all earlier evidence remain true historical records and are never edited. The implementation entry must independently record absence before creating any code.

DURING/AFTER THE NEXT AUTHORIZED IMPLEMENTATION: exactly app/execution/pipeline.py exists as a regular module; app/brain/pipeline.py remains absent. Replace the one source absence assertion in the adapter suite with a presence assertion and the checks below. Record entry absence, exit presence, exact diff and production commit. No automatic authorization to change a second existence test.

The replacement test requires:

1. Canonical file exists; frozen public P7 definitions are exactly run_recorded_turn, RecordedTurn, SettledConfirmationProjection, AdmissionMode, PipelineStage, PipelineStopReason, PipelineStop and TurnOutcome. Imported existing types are dependencies, not new P7 definitions. Other helpers must be private and pure. Entry signature is exactly one RecordedTurn argument, returning TurnOutcome; no dependency parameters.
2. Walk all app Python files except the pipeline and assert zero static importers, qualified pipeline references, dynamically named references or calls to its entry. The module has zero production consumers, including all server/live request paths. Check package __init__ exports remain unchanged.
3. Pipeline imports stay within the passive dependency budget from IMPLEMENTATION_ACCEPTANCE; its AST contains no dispatcher/confirmation-machine/registry/provider/model/network dependency, dynamic import, service locator or executable injected collaborator. Reject constructor/call sites for invocations, trusted results, confirmation mutation, identifier minting, clock reads, ledger writes or audit emission. Do not evade a forbidden symbol with an alias.
4. Adapter consumption is the single exact static import in ADAPTER_CONSUMER_AUTHORIZATION. Its outputs remain untrusted. New pipeline unit tests must also prove runtime zero calls with failing sentinels and repeated immutable recorded inputs; structural presence alone is not runtime conformance.
5. Existing lines 56–59 remain unchanged: mode is LEGACY, hermes_brain False, hermes_enabled False, ACTIVE_EXECUTION_MODES == {LEGACY}. No execution path is activated by the module's presence.

P7's registry/dispatcher/real-tool/provider call counts must be zero. Existing four legacy registry.call sites in app/server.py remain byte-identical; this transition does not erase or invoke them. Confirmation and dispatch non-activation suites receive ZERO changes. No wildcard consumer exception and no second adapter consumer.

This transition is authorized and frozen independently; P-B05 still prevents final contract/fixture freeze and implementation entry.
