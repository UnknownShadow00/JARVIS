# P1 source authority

`app/execution/correlation.py:29-38` defines SessionId, TurnId and the existing identifier family. `:44-64` mints session/turn identifiers with uuid4 hex; `:110-159` defines frozen CorrelationContext and new_turn_context. Reuse those constructors and types. `context_from_mapping` deserializes data; it does not authenticate a client or establish ownership.

The existing `new_turn_id` docstring (:56-58) permits an adapter to reuse a trace ID. Operator A8 explicitly supersedes that permission for Shadow Context V1: mint a separate P1 turn, retain only trace association. The source/docstring remains unchanged. No second shadow ID family and no separate correlation UUID are authorized.
