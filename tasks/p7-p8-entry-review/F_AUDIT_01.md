# F-AUDIT-01

Source: `task13b11o-r1/SCHEMA_V3_FOLLOWUP.md`. `TURN_SUMMARY` currently unconditionally requires non-null `response_obligation`, while a pure conversational turn correctly has none. The prescribed future correction is conditional on `Lane.OPERATIONAL`, with strict negative tests for conversational fake obligations and operational missing obligations. `response.obligation` event remains non-null; schema version and legacy remain unchanged.

R8 emits no final audit record, and passive P8 fixtures need not emit one. F-AUDIT-01 can remain open through an explicitly recorded-only passive unit. It blocks live audit wiring; operational failed-turn audit semantics separately belong to F-FALLBACK-01. No schema change was made.
