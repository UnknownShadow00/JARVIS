# Operator authority for D04

Historical exact QUESTION: “What separate evidence sink, redaction/retention, interval clocks and loss semantics are required?” Option A: “Approve a bounded separate sink with explicitly sourced facts, drop/error counts and evidence retention.” Historical packet remains unchanged.

The current operator instruction explicitly approves future app/execution/shadow_observation_sink.py; a JARVIS-owned UTC chronology clock only; append-only/no-automatic-delete P7 retention through measurement completion, sealing and explicit cleanup authorization; known evidence loss invalidates the affected window; local-only persistence with audit/P2 separation. This resolves D04's semantic/security choices within those bounds.

This does not approve numeric quotas, interval/latency clocks, attempt/retry keys, a backend/queue/scheduler, complete live measurement accounting, off-Core backups/export, model/provider, CT/window thresholds or production code. Source-derived existing data root and P1 utc_now are reused; exact backend/leaf mechanics are deferred within that authority.
