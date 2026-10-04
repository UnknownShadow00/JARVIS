# Preparation inventory and remaining readiness

| Future unit | Settled inputs/output and responsibility | Existing component reuse | Remaining gate |
|---|---|---|---|
| passive context owner | resolved JARVIS session + one accepted turn → CorrelationContext/P2 snapshot/trace association | P1 constructors; P2 LedgerStore.for_session and snapshot | exact constructor test exception; bounded API/lifecycle implementation scope |
| passive ingress composer | exact request + settled context → immutable two-field envelope | existing context value; no binder call needed | context implementation/type; focused pure tests; no live activation |
| evaluator input builder | envelope + JARVIS-owned classifier/binding facts + authentic adapter data → RecordedTurn | F-MAP producer, P3/P4, existing 21-field RecordedTurn | adapter authenticity/model-free decision, source of all lane/value/clock/proposal fields and test consumers |
| observation producer | actual P7 facts + input association → separate measurement data | existing response/stop enums where present | field completeness, instrumentation ownership, failures without IDs |
| record/writer | immutable observations + accounting → retained evidence | no exact production equivalent exists | serialization, privacy/retention, loss/failure contract and clock semantics |
| server/API/UI consumers | approved mode + admitted user input → isolated capture + later evaluator submission | exact REST/WS points; existing auth/wake/cancel/cleanup | continuation representation, scheduler/resource policy, consumer exceptions, activation authorization |

No evaluator module path, factory signatures, new public P2 API, parser limits, clock or operational commands are selected here. These are useful inventories for the next authorized implementation review, not a claim that every unit is implementable without decisions. Keep raw request and recording text out of a measurement schema unless separately justified; no hidden chain-of-thought fields.

Complete source review covered P1/P2/P7/binder types, actual REST/WS/voice graph, audit-v3 requirements, active-mode/config gates and non-activation tests. Canonical source files and authority copies are retained in session evidence. No local checkout was used as a substitute for inaccessible canonical Core.
