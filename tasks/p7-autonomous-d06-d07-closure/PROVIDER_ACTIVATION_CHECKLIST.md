# Future activation prerequisites — not performed

| Requirement | Current evidence / remaining work |
|---|---|
| AI host healthy | OS/GPU/process snapshot only; future runtime health review still required |
| Runtime available | Existing idle listener observed; no API/readiness call performed |
| Exact model alias | Installed manifest/five blobs/context verified; reverify immediately before approved activation |
| RAM ceiling | No >32 GB design; future measured envelope under cap required |
| Shadow concurrency1 | Approved; scheduler not implemented |
| Shared ownership | BLOCKED; resolve legacy unload/load overlap without guessing |
| Core→AI path | Endpoint config/bind verified; provider connectivity/ACL test not performed |
| Adapter ready | Passive canonical parser exists; native normalizer/prompt sources not frozen |
| No alternate provider | Approved contract intent; future runtime sentinel required |
| Observation/sink ready | Frozen contracts only, no implementations; collector/authenticity join needed |
| Scheduler ready | D07 not run; no bounded mechanism/numeric timeout/queue |
| Rollback ready | Plan only; later drain/cancel/loss proof required |
| CT/window ready | D08/D09 unresolved; no live scoring authorization |

Do not perform any activation from this checklist. No new deployment command, firewall operation or infrastructure policy is supplied.
