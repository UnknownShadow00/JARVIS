# Binding authority table

| Binding | Frozen owner | Producer role | Current limit |
|---|---|---|---|
| Route/action/reporting intent | P3 `router.route`, after P3 `classifier.classify` | call/reuse identical deterministic inputs; never overwrite | router has no tool name |
| Target text and resolved flag | P3 router | preserve `RouteResult.target`/`target_resolved` exactly | target→tool argument field **unfrozen** |
| Capability pairing/policy | P4 `ACTION_CAPABILITY`, `row_for`, `permissions.decide` | copy declared pair and verified availability; submit query | only two action pairs, no live availability source |
| Tool namespace | separately signed closed binder/schema under P7 integration owner | select **only** from approved mapping | **unfrozen; not capability string or ToolSchema name** |
| Raw argument keys/values, target-bearing field | separately signed closed binder/schema | derive deterministically from routed request/current trusted state | **unfrozen; no legacy/harness copy** |
| Canonical arguments/version/rules | P3 `canonicalize`, `CANONICALIZATION_VERSION` | call existing API; preserve raw and result | no second normalizer |
| Permission class/outcome | P4 engine | none; P7 recomputes at S07 | no producer-created decision |
| Confirmation observation | P4 confirmation-owning boundary | no import or claim; receive only V2 settled projection later | no CONFIRMED state |
| Invocation/result | P5 dispatcher | none | no creation or replay execution |

Frozen P4 pairs are OPEN_APP→`apps.open`, OPEN_URL→`browser.open`; they do **not** establish tool namespace `apps`/`browser` or argument schemas. Browser D-01 remains under current signed policy. See `task13b11o/CAPABILITY_PROJECTION.md` and `task13b11o-r1/PROPOSAL_GUARD.md` §Minimal mapping prerequisite.
