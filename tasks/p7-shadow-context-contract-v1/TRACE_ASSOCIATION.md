# Observational trace association

The server establishes a transport trace with start_trace (`server.py:359,524`; `app/observability/tracing.py`). Capture its current trace value as immutable observational metadata while that trace is active. Use a plain nonempty string from the server tracing context, never a client identity field. If no trace is available, retain None explicitly; never substitute a turn ID. Trace availability grants no authority.

P1 turn IDs are separately minted uuid4 hex. Trace IDs are not converted, hashed, parsed or copied into turn identity. No equality claim, derivation or fallback authority exists. Multiple observations can share a turn association; a trace cannot select a ledger. Correlation semantics are in CORRELATION.md.
