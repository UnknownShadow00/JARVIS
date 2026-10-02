# Minimal counterexample — zero proposals

minimal-counterexample.json spells all 21 input fields as a static construction recipe. It is analysis data, not a final corpus and not a new production type. Identifiers and timestamps are fixed; there is no model call, provider data, store or executor.

| Fact | Exact value / owner |
|---|---|
| Mode | RESULT_REPLAY: invocation/result present, confirmation absent |
| Request | What is a cache? |
| Actual classification | GENERAL_EXPLANATION |
| Actual route | NONE, target=None, target_resolved=None, capability_available=False |
| Initial lane | CONVERSATIONAL, no initial operational signals |
| Final lane | OPERATIONAL, reason TOOL_RESULT |
| Proposal cardinality/match | zero, no candidate exists; adapter valid; supported-action exactly-one guard is not reached |
| Caller capabilities | OPEN_APP/OPEN_URL available in explicit RouterContext; no routed action exists |
| Current permission | not evaluated; permission_projection=None; do not manufacture DENY/ALLOW |
| Recorded invocation permission | ALLOW for OPEN_URL/browser.open-era static binding; never substitutes current policy |
| Confirmation projection | None; no confirmation authority |
| Recorded result | exact typed fixture SUCCESS/executed=True for linked OPEN_URL invocation, same turn/session IDs; facts empty |
| Earlier guards | valid S01 shape/C-00a/C-00b; classify, route, lane, parser all succeed; order 7 NONE/zero terminal condition true |
| C15/C-04 condition | route NONE differs from recorded invocation OPEN_URL |
| Disputed stage | C15 says S09/result_invalid; frozen branch has already left the S06–S09 walk |

Both IDs and result description can agree perfectly while request routing disagrees. This isolates route agreement rather than an earlier shape/identity failure. Removing proposals is minimal and exposes the gap; adding one proposal yields the already-determined unexpected_proposal stop. No live URL is visited; example.invalid is an inert fixture target.
