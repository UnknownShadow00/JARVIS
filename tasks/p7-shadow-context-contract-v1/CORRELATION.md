# Correlation reuses P1 exactly

The canonical contract has CorrelationContext(session_id, turn_id, invocation_id=None, confirmation_id=None), not an independent correlation_id scalar (`correlation.py:110-159`). The context is the authoritative correlation association. Do not mint a third ID, rename trace as correlation or invent correlation == turn equality. Session and turn have distinct meanings within the context.

For an initial accepted user turn, preserve new_turn_context's unset invocation/confirmation fields. An envelope carries no authority to fabricate invocation or confirmation association. Confirmation continuation/result replay are separate existing pipeline admissions, not a REST/WS client privilege. The future context validates the actual P1 type and JARVIS source, not mere UUID-shaped client strings.
