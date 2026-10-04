# Future implementation acceptance matrix — not executed new tests

| ID | Case | Required assertion |
|---|---|---|
| A01 | first accepted turn | JARVIS session resolved/created before one P1 turn |
| A02 | second turn in same context | same session/ledger; different turn |
| A03 | two sessions | different ledgers; no record leakage |
| A04 | client/model fake IDs | no authoritative adoption |
| A05 | wrong-session snapshot/record | shadow rejects before handoff |
| A06 | later ledger append/supersession | old snapshot unchanged |
| A07 | new session | real for_session().snapshot(), no synthetic empty fallback |
| A08 | snapshot exception | no settled context; legacy unaffected |
| A09 | trace string equals/looks like ID | separately minted turn; no trace-derived identity |
| A10 | absent observational trace | None only; no fake ID |
| A11 | WS stream and fallback | one input/turn/snapshot/envelope attempt |
| A12 | WS output chunks | zero additional turns |
| A13 | REST/WS parity | identical authority/order for equivalent accepted contexts |
| A14 | resolver/mint/correlation exception | shadow only fails closed |
| A15 | settled object graph | no store/framework/callable/execution access |
| A16 | provenance writer sentinels | zero writes for inert shadow |
| A17 | retry/reconnect/expiry | pending protocol decision; no invented fixture expectation |
| A18 | voice direct path | explicitly outside REST/WS coverage |

Existing canonical pytest regression: 5721 passed, 11 deselected, 0 failed (2 warnings). These regressions do not prove an unimplemented context owner. Deterministic golden: 12/20, unchanged eight failures. Future owner construction conflicts with provenance_non_activation_test.py::test_there_are_zero_live_provenance_writes; an exact test authorization decision is required before implementation, not granted here.
