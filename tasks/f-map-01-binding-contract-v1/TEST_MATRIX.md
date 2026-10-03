# Future implementation test matrix (no tests added here)

| Fixture | Required assertion |
|---|---|
| Valid conversational request / CT-013 | No expected tool or permission; safe conversational guard path |
| Valid `OPEN_APP` known app | Exact `apps.open`/`apps` map, P3 canonicalization/version, P4 request |
| Valid `OPEN_URL` absolute URL | Exact `browser.open`/`browser` map, URL unchanged, P4 row 12 |
| Unsupported action / DEPLOY / DELETE_PATH | No invented binding or registry fallback |
| Ambiguous route or target / route `NONE` | No executable expected binding |
| Invalid canonicalization / missing binding | Fail closed; no repaired arguments |
| Exact proposal match | P7 comparison match only; zero execution |
| Proposal mismatch, zero or multiple proposals | Existing P7 guard outcome; binding unchanged |
| Fake model binding, fake client permission/confirmation | No authority transfer |
| Wrong request/session/turn IDs | Producer rejects; no P7 call with fabricated association |
| Replay-associated request | Separate result owner; no replay execution or binder result creation |
| `browser.open` current policy | P4 ALLOW row preserved, URL predicate enforced; browser D-01 unchanged |
| Metadata missing/drift/digest mismatch | No fallback to `list_tools()`/`call()`; projection rejected |
| Purity / determinism | Same inputs same bytes; zero network, subprocess, provider, registry call, dispatch and mutation |

CT-001 must additionally assert fabricated operational prose never reaches user-facing output. Future focused tests must exercise real existing P3/P4/P7 APIs and verify no production consumer until explicitly authorized.
