# Future tests — specification only

| ID | Input/fault | Required assertion |
|---|---|---|
| B01 | REST exact string and settled context | envelope preserves both; capture before _process |
| B02 | WS streaming | one envelope before stream; none per chunk |
| B03 | WS stream returns None | one envelope across fallback |
| B04 | equivalent REST/WS contexts | equivalent authority-bearing content |
| B05 | extra client authority keys | ignored as authority, not mapped to fields |
| B06 | non-string WS message | no shadow envelope; no coercion/change to legacy |
| B07 | invalid/unowned correlation or wrong-session snapshot | reject before downstream handoff |
| B08 | mutated original payload/later ledger write | settled text/snapshot unaffected |
| B09 | resolver/composer exception | legacy response/stream/cleanup unchanged |
| B10 | cancellation/disconnect | existing semantics preserved, no second attempt |
| B11 | sleep rejection | no context/envelope |
| B12 | registry/model/dispatcher/store sentinels | zero reachability/calls from composer |
| B13 | framework/callable in object graph | reject |
| B14 | voice wrapper | no REST/WS shadow coverage claim |
| B15 | module imports/public shape | pure composition; exact two-field value |
| B16 | mode off | future consumer inert; no owner state allocation |

Future wiring needs explicit non-activation gate review. These are not implemented or scored tests. Regression result is retained separately and cannot establish envelope implementation correctness.
