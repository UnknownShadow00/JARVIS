# Field inventory and exclusions

| Fact | Included location | Authority |
|---|---|---|
| untrusted text | request | client content only |
| JARVIS session/turn | context.correlation | P1 constructors through shadow_context owner |
| correlation association | context.correlation | exact existing P1 record; no new scalar ID |
| P2 current facts | context.snapshot | same-session P2 owner at request time |
| trace association | context.transport_trace_id | server observation, optional None |
| raw JSON/HTTP headers | excluded | not downstream requirements |
| REST/WS object/server/callback | excluded | mutable execution-capable objects |
| route/tool/capability/permission | excluded | must be independently derived by existing authorities |
| confirmation/execution/TrustedToolResult | excluded | cannot be transport-supplied |
| adapter request/recording/model | excluded | separate unresolved adapter-input contract |
| worker/task/clock/store/registry | excluded | not envelope data |

A client may mention any authority-looking word inside request text; it remains text. Extra client JSON keys cannot become envelope control fields. Mere exact Python type identity is not origin authentication; the trusted composition boundary must supply context, never deserialize it from a client payload.
