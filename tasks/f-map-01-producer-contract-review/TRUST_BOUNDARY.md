# Trust boundary

| Datum | Owner | Trusted for | Not trusted for |
|---|---|---|---|
| Raw user request | user via transport | text to classify/route | authority, tool/target/argument override |
| HTTP/UI/client metadata | client/transport | delivery/session lookup only after server validation | route, policy, confirmation, result |
| Session/turn/correlation IDs | P1 JARVIS | association after exact validation | permission or execution |
| Classifier result | P3 deterministic classifier | request class/reason from same text/context | tool choice, permission |
| Lane result | P3 lane policy | operational/conversational separation | execution grant or fallback prose |
| Router result | P3 deterministic router | action/target/resolution/reporting intent | tool namespace, permission, successful execution |
| Canonical result | P3 canonicalizer over JARVIS-bound tool/raw args | exact normalization/version/rule record | proof that original tool/args were authorized |
| Permission request | JARVIS projection | query data for P4 and S06 comparison | permission decision |
| Permission decision | P4 engine | policy outcome/class for that query | confirmation, invocation, execution |
| `ModelDraft` / `ToolProposal` | adapter parses provider data | candidate to compare, conversational text only on approved lane | any operational authority or expected binding |
| Settled confirmation projection | P4 confirmation owner | read-only pending/binding observation for mode B | claim, CONFIRMED state, execution |
| `TrustedToolResult` | P5 result boundary | linked execution evidence in recorded mode C, subject to F-P7R1-01 origin limit | new dispatch, model assertion of execution |

The producer may compose existing owner outputs, not reimplement their rules. Exact Python type identity is not independent provenance proof. No client/model/provider-supplied permission, confirmation or result field becomes trusted by being wrapped in a dataclass.
