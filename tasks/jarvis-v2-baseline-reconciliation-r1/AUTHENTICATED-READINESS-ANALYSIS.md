# Authenticated readiness

The12 failures are independently reproduced in compatibility-existing.json; exact identities and phases are mapped in TWELVE-FAILURES.json. Every case reaches cli.main(['ready']) and raises SystemExit(2) because build_parser has no ready choice. None reaches HTTP request processing. There is no evidence that the /ready route was removed or replaced.

Three cases check empty/space/tab token refusal before a request. Eight check authenticated GET/payload/status behavior: two valid-ready payloads succeed, disabled-worker/unready/malformed payloads fail,401 and503 fail. One checks transport failure uses one attempt and never starts/retries a service. Their different expected assertions all fail for the same parser omission, not12 separate auth defects.

Restored17 CLI lines follow the documented RC1 contract: require a nonblank configured token, call existing credentialed _get('/ready') once, require exact boolean readiness fields, reject unavailable worker readiness, preserve nonzero failure and avoid exposing the token. The API route and exact Bearer comparison remain unchanged; there is no anonymous fallback, service start, retry, credential operation or access-policy relaxation.

Separately, server lifespan now uses .strip() when checking whether a configured identity can start a transport-backed synthetic worker. This retains RC1's three startup regression cases, ensuring blank-token refusal precedes background work. Tests use synthetic in-memory identities only, never real credential files.

Final existing suite passes507 including all12 ready cases; release tests cover route401 behavior, nonblank startup and zero mutation. Classification is a reviewed feature omitted from the sibling development integration; intent of the snapshot author is not established. No unresolved authorization design choice is necessary for this restoration. Independent review of the candidate remains required.
