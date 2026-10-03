# Trust boundary

| Data | Owner | Trusted for | Not trusted for |
|---|---|---|---|
| Raw user request | User | Intent text for deterministic classification | Route, tool, capability, approval or execution |
| Client metadata | Client/transport | Transport diagnostics after validation | Any control-plane field or authoritative ID |
| Normalized envelope | JARVIS ingress | Preserved text and same-session association | Inferred permission or executable binding |
| JARVIS IDs | P1 ingress | Request/session/turn correlation | Tool authorization by themselves |
| Classifier/lane/router results | P2/P3 deterministic modules | Their respective classification, lane and route facts | Registry identity or permission |
| Canonicalized target/args | P3 canonicalizer plus V1 predicates | Exact comparison values | Execution permission |
| Registry metadata snapshot | Future passive JARVIS boundary | Declared key and handler metadata at reviewed revision | `registry.call`, runtime availability or policy |
| Binding projection | Future V1 composer | Deterministic side of P7 comparison | Dispatch, confirmation or result provenance |
| Permission decision | P4 engine | Settled policy outcome | Confirmation claim or tool execution |
| ModelDraft and ToolProposal | Hermes adapter/model | Untrusted proposal to compare or safe conversational draft | Binding repair or authority |
| Confirmation projection | P5 settled owner | Guard input at its frozen boundary | Machine/store mutation through binder |
| TrustedToolResult | P5 result owner | Recorded continuation under frozen type assumption | Proof of cryptographic dispatcher origin (F-P7R1-01) |

No untrusted text, client flag, or proposal is promoted into an owner-trusted value by type conversion alone.
