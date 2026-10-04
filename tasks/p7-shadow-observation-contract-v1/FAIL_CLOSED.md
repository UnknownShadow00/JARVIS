# Failure behavior

Wrong exact types, malformed/mismatched IDs, non-initial admission, unknown transport, one-sided binding pair, mutable/behavior-bearing inputs, contradictory duplicated owner facts, invalid count/match, executed/result/claimed-confirmation state, and inconsistent terminal shape produce no record. Use fixed TypeError/ValueError failure categories for the future pure API; no new PipelineStopReason or operational response is fabricated.

Required validation includes: exact P1 session/turn shape and absent child IDs; terminal turn/correlation equality; stopped stage/reason versus response shape; response lane/source enum identity; binding V1/pair/digest/string-map shape; agreement among available route/state, binding-query/route primary_action, and permission/state facts; proposal count/match restrictions in PROPOSAL_OBSERVATION. V1 refuses tool-success/error candidate source/obligation labels in this inert scope. No fallback identity, empty snapshot, guessed permission or lower obligation.

Origin/authenticity of owner types is a trusted caller precondition, not something dataclass-shape validation proves. Producer does not rerun route, binding, guard, P4 or P6 algorithms to authenticate them. If the actual facts cannot be collected, supply only genuinely available optional observations, or reject the attempt; never manufacture missing evidence.

Future consumer isolation must keep producer exception/diagnostic/sink failure out of legacy reply/stream. The producer cannot enforce transport isolation itself because it has no live edge. Producer-failure records and pre-context diagnostics require a separate D04/scheduler mechanism; it must not recursively fabricate this same record or claim sink delivery.
