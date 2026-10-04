# Security review

| Threat | Verified boundary |
|---|---|
| Model/client route, capability, tool, target or permission override | No such API inputs; unexpected keywords raise `TypeError`; deterministic P3/P4 owners supply values |
| Fake/missing/extra registry metadata or callable row | Exact type, nested shape, revision/digest and full-value checks reject; fresh reviewed rows used |
| Malformed target or arguments | URL/app predicates and exact two-key raw/canonical maps; invalid P3 result yields no binding |
| Wrong IDs or P2 association | Exact P1 correlation shape, same session snapshot and matching classifier keys required |
| Mutable source state | Frozen output with P3 `MappingProxyType` maps; changing source snapshot after composition does not change projection |
| Dynamic import, service locator, registry call, handler, dispatch, audit/provenance mutation | Static import/call scan and runtime sentinel observed zero execution edges/events |
| Unauthorized consumer or test exception | Exact file/symbol budgets and consumer scans pass; no tenth existing-test exception |

Authority bypasses observed: **0**. Approved vulnerability audit tooling was unavailable on Core; nothing was installed or fetched.
