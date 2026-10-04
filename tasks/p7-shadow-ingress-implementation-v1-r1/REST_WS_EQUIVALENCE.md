# Fixture REST/WS equivalence

Focused cases label conversational, OPEN_APP-shaped and OPEN_URL-shaped strings REST or WS. They supply the same/equivalent immutable settled view and assert equivalent envelopes and identical retained P1/P2 references. Generalization varies labels including REST fallback and WS reconnect fixture names; the labels never enter the envelope.

`rest-ws-equivalence.json` independently proves equality for identical primitive inputs and context, with zero transport fields. No HTTP/WS adapter is implemented or called. This proves composer neutrality, not live capture count, authenticated continuation, reconnect/retry or server failure isolation.
