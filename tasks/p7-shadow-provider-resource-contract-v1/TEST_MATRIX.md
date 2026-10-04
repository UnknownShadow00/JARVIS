# Future D06 verification matrix

These are requirements, not executed live tests.

| Case | Required result |
|---|---|
| Correct alias/blob/context | Exact digest chain and num_ctx=64000 |
| Alias missing/replaced | Admission blocked; no pull/repair/fallback |
| Wrong model response identity | Not eligible live evidence |
| Two shadow generations | At most one actual remote generation |
| Legacy in flight / lifecycle unload | Reviewed ownership prevents interference; currently blocked |
| Cancelled local waiter | Slot not reused until remote generation termination is established |
| Provider unavailable/load failure/timeout | Explicit incomplete; no fake zero proposals |
| OOM/RAM/GSP failure | Shadow-only failure; no restart or safety change |
| Network destination substitution | Reject unapproved endpoint |
| UI direct access | No authorized direct edge |
| External/local fallback | Rejected |
| Adapter bypass / binding copied to proposal | Rejected |
| Raw prompt/model persistence | Not required by default |
| Provider/model evidence join | Separate D05/controller association; unchanged D03/D04 |
| 32 GB cap | Configuration and measured future workload stay within approved ceiling |
| Session safety | No invocation, source/config change, infrastructure or package install |

Current offline checks: manifest/blobs, OS/service/socket/GPU inventory, 26 source gates, canonical pytest/golden and unchanged production bytes. They do not prove future concurrent runtime safety.
