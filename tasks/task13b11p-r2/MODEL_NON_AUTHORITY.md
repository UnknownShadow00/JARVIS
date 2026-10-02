# MODEL NON-AUTHORITY — specified, not implemented

No model was called. Nothing in this task sent a prompt, opened a socket, started Ollama or
touched Hermes. The design properties below are the implementation target; none is
measured.

Recorded model content enters a turn through exactly three admitted fields — `request`,
`recording` and `adapter_request` — and reaches exactly three consumers: the classifier,
the router, and the frozen adapter parser. It reaches no authority input.

| Claim a model or caller might make | Why it carries nothing |
|---|---|
| `confirmed=true` | no such field exists on `RecordedTurn`; the admission type cannot carry the assertion |
| `permission=ALLOW` | `permission_outcome` is never admitted; the policy is re-decided every run from JARVIS-owned inputs, and a replayed invocation's outcome must *equal* that decision (C-07) |
| `executed=true` / `status=SUCCESS` / `tool_succeeded=true` | a structured field outside `{text, proposals}` is rejected by the adapter (`invalid_response`); execution truth arrives only as a `TrustedToolResult` the pipeline cannot construct |
| "I already did it" / "user confirmed" in prose | prose enters no authority input and is final only on the conversational lane, where no operational claim is made |
| a confirmation id in model output | the admission mode is derived, not declared; an id alone grants nothing, and the record it names must pass full binding equality |
| an arbitrary tool name or argument | the proposal stays untrusted; tool identity and whole-map canonical equality are checked against the caller's authoritative expected projection |
| a claim inside `raw_arguments` | inert data that fails canonical-argument equality |

The admission mode itself is the sharpest case: it is a derived read-only property over
three presence booleans with no constructor field, so no caller and no model can author
which shape a turn is.

Unsupported actions stay contained: all 41 reach `UNKNOWN_ACTION` and the operational lane
through the unmodified classifier (version `"2"`) and router, and the existing P6
capability-unavailable path answers them. There is no raw operational fallback anywhere in
the design — a failure that P6 cannot represent returns a non-renderable `PipelineStop`,
never prose.
