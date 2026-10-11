# L1 and L2 comparison; neither approved for live execution

L1 retains a separately injected bounded model-backed router before the legacy responder. It requires an explicit router endpoint/model/profile/prompt, deadline, output/native/request bounds and endpoint ownership. Only unambiguous {intent:respond,confidence:number} at the approved threshold proceeds; malformed output, tool proposal, low confidence, timeout or uncertain transmission stops the attempt. No retry, model fallback or error-to-respond fallback exists.

L2_FOUR_INPUTS recognizes only the exact original four input strings and has no router generation. It is an experimental deterministic policy, not a claim that the original router behaves identically. The original source's pure rules classify those four as [None, respond, None, None]; the remaining three ordinarily require model routing. Gate6B also proved none is an original deterministic direct response. No input was changed to force a rule match. L2 fixture confidence0.9 is a proposed policy detail, not an observed model score and not approved for clients.

| Comparison | L1 | L2_FOUR_INPUTS |
|---|---|---|
| Successful four-attempt fake sequence | 12 provider substeps | 8 provider substeps |
| Legacy visible response | separate responder output | same responder ownership |
| Granite role | observational only | observational only |
| Additional policy | bounded respond-only model router | explicit allowlist and deterministic confidence |
| Equivalence limit | new prompt/parser/error/serialization behavior; model identity unresolved | removes real routing for three inputs; cannot be silently substituted |

Prompt/memory is explicit: NONE requires empty snapshot; SNAPSHOT requires a supplied immutable string. No database or procedural-memory mutation capability is present. Current adapter sends system(+snapshot) plus current message to legacy; bounded previous delivered history is supplied to Granite. Approval must specify whether this matches desired legacy context or whether a separately reviewed prompt/history adapter is needed. Action-tag instructions are not inherited by default; any returned action tag/tool_calls aborts without execution.

Dummy test limits (1024 context,32 output,2048 native bytes,16384 request bytes,0.05s provider and delivery deadlines,keep-alive1) exist only in fixtures. They are not recommended live budgets. Live L1/L2 selection and exact prompt/hash/model/limits remain operator release decisions. The factory refuses production construction while unresolved.
