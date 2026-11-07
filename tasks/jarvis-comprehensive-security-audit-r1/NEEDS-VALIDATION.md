# Needs validation

Only independently verified source-grounded conditional leads appear here. No severity is assigned.

## Anonymous task access depends on an admitted loopback deployment and an excluded local principal

Fingerprint: `app/server.py:anonymous-loopback-authority`.

Packaged source still permits ordinary task HTTP requests without credentials when the API token is empty and supplies the shared local-service actor. Fresh parent-isolated verification against snapshot-packaged observed genuine stock lifespan refusing its missing synthetic database before creation. Only after explicit synthetic authority binding, native in-memory requests read and cancelled one dummy task without credentials; diagnostics rejected empty-token access and configured-token task reads rejected missing credentials. These results establish conditional task-state route behavior, not an operating anonymous deployment or a cross-UID/browser exploit. Current /stop requires credentials even in empty-token mode, host resource mutation routes deny403, and a configured transport requires a token at lifespan. Those controls narrow other paths but do not wrap ordinary task reads/cancellation. Admission and local-client trust facts remain unresolved.

Claimed root cause: Ordinary task HTTP routes accept anonymous requests in the explicitly configured empty-token loopback mode and operate in a fixed server-owned actor namespace. This could cross a principal boundary only if an admitted serving deployment exists and a locally reachable client is excluded from its intended trust boundary.

### Current trace

1. [app/server.py:251](snapshot-packaged/app/server.py#L251) (api_token_middleware): A received ordinary task HTTP request proceeds without credential verification when server.api_token is empty (251-254); /stop is independently refused at252-253. Lower-trust entrypoint status remains conditional on the unresolved serving/principal facts.
2. [app/agent/api.py:111](snapshot-packaged/app/agent/api.py#L111) (cancel): DELETE /tasks/{task_id} passes the fixed SERVICE_ACTOR and caller-selected task/request identifiers to Authority.cancel; the request ID query is constrained to canonical UUID4 form.
3. [app/agent/authority.py:432](snapshot-packaged/app/agent/authority.py#L432) (Authority.cancel): After task identifier validation, the actor scope selects the task for the cancellation effect inside the fenced mutation and request-receipt transaction.
4. [app/agent/authority.py:425](snapshot-packaged/app/agent/authority.py#L425) (Authority._cancel): For a held task, task status and outbox state become cancelled; _put at427 persists task data in the surrounding transaction. This is a task-state effect, not proof of real executor access.

### Verified evidence

- [app/config.py:108](snapshot-packaged/app/config.py#L108): The API token defaults to empty. The validator at114-136 requires configured loopback host/origins in local mode and a nonempty token for remote/nonloopback mode.
- [config.yaml.example:103](snapshot-packaged/config.yaml.example#L103): The public example selects127.0.0.1, explicitly describes empty-token authentication being disabled for localhost-only use at109, and sets api_token empty and remote_access_enabled false at112-113.
- [app/server.py:251](snapshot-packaged/app/server.py#L251): Empty token bypasses ordinary task HTTP authentication at251-254, with a separate /stop refusal. A configured token is checked at258 using _api_token_ok and constant-time byte comparison at201.
- [app/server.py:402](snapshot-packaged/app/server.py#L402): The actual FastAPI app includes the authority router.
- [app/agent/runtime.py:7](snapshot-packaged/app/agent/runtime.py#L7): Ordinary authority HTTP routes use the fixed Actor(local-service), rather than assigning a caller-specific namespace.
- [app/agent/api.py:94](snapshot-packaged/app/agent/api.py#L94): Operator diagnostics independently requires a configured matching Bearer credential, including when ordinary routes permit anonymous access.
- [app/main.py:11](snapshot-packaged/app/main.py#L11): The stock entrypoint serves the reviewed FastAPI app at the configured host and port.
- [app/server.py:115](snapshot-packaged/app/server.py#L115): Mandatory lifespan obtains the authority before readiness, scheduler, listeners and background startup work. A failing get_authority prevents startup.
- [app/agent/runtime.py:17](snapshot-packaged/app/agent/runtime.py#L17): The stock opener supplies only the authority database and legacy JSON paths, without ledger, enrollment witness or legacy approval.
- [app/agent/authority.py:107](snapshot-packaged/app/agent/authority.py#L107): Missing, empty or symlinked databases are refused before directory or writer-lock creation. Existing databases additionally require enrollment or explicit legacy admission at159-163.
- [app/agent/enrollment.py:299](snapshot-packaged/app/agent/enrollment.py#L299): An enrolled store requires the ledger guard and external witness, neither supplied by the stock opener.
- [app/agent/enrollment.py:338](snapshot-packaged/app/agent/enrollment.py#L338): Legacy admission requires an explicit OperatorPermits verifier/permit tuple; its verified payload binds database path, logical state and execution_disabled at343-346.
- [app/agent/runtime.py:21](snapshot-packaged/app/agent/runtime.py#L21): The documented trusted embedding/test hook can bind an admitted authority; it is not exposed as an HTTP activation endpoint.
- [tests/test_server_auth.py:17](snapshot-packaged/tests/test_server_auth.py#L17): The anonymous-task test at30-33 binds an explicit synthetic authority. The module TestClient at8 skips lifespan for ordinary route requests.
- [app/server.py:217](snapshot-packaged/app/server.py#L217): Present WebSocket Origin is checked against local/configured origins before either WebSocket accepts (229-237,456,533). Native HTTP Host/Origin results do not establish browser or WebSocket exploitation.
- [app/agent/authority.py:307](snapshot-packaged/app/agent/authority.py#L307): Mutations bind actor scope, operation and canonical payload to durable request receipts and detect conflicting reuse. Reads and cancellation select records within that actor scope; these controls do not assign network-client identity.
- [app/agent/api.py:72](snapshot-packaged/app/agent/api.py#L72): A non-null transport_permit execution submission independently requires a configured matching Bearer token at75-76. This separate check does not wrap /tasks read/cancel at99-111.
- [app/agent/api.py:106](snapshot-packaged/app/agent/api.py#L106): Task reads use SERVICE_ACTOR; get_task validates the canonical task UUID and checks actor scope through _get at authority.py:379-384.
- [app/agent/authority.py:3](snapshot-packaged/app/agent/authority.py#L3): The contract trusts local code controlling the process/database and describes Actor as a server-owned namespace rather than application authentication. No multi-user isolation baseline is promised.
- [docs/authority_enrollment.md:18](snapshot-packaged/docs/authority_enrollment.md#L18): Documentation explicitly requires trusted embedding to bind an already verified authority and says unprovisioned default startup fails closed. This is a supported conditional embedding mechanism, not evidence of an actual serving instance.
- [docs/TARGET_HOST_READINESS.md:54](snapshot-packaged/docs/TARGET_HOST_READINESS.md#L54): Loopback is explicitly the Phase2 containment boundary; future remote access requires additional identity/session/scoping controls. An excluded local principal must therefore be established rather than inferred from a generic multi-user threat model.
- [tasks/jarvis-comprehensive-security-audit-r1/agents/verify-latest-auth/artifacts/verify_auth_packaged.txt:3](agents/verify-latest-auth/artifacts/verify_auth_packaged.txt#L3): Parent-promoted fresh snapshot-packaged sandbox output records stock_lifespan_error authority_unenrolled_or_missing, stock_database_created false, synthetic-bound native read/cancel200 and cancelled dummy task, empty-token diagnostics401, configured-token missing401/valid200, and no real socket/browser/otherUID test. The native requests use arbitrary Host and Origin; the route fixture explicitly skips lifespan.
- [app/server.py:123](snapshot-packaged/app/server.py#L123): Actual lifespan rejects a configured execution transport when the API token is empty; this additional preventing control does not require a token for an admitted authority without a configured transport.
- [app/server.py:252](snapshot-packaged/app/server.py#L252): Empty-token requests to /stop receive401 rather than reaching the worker cancellation path.
- [app/server.py:340](snapshot-packaged/app/server.py#L340): All four host resource mutation HTTP routes unconditionally return403/offline_operator_control_required.

### Decisive blockers

- No actual serving deployment with an admitted authority and an empty configured token has been established. The stock opener lacks the admission context required for missing, enrolled or legacy stores; explicit synthetic binding does not demonstrate ordinary deployed startup.
- No separately restricted local OS principal, excluded by the application's intended loopback trust boundary but able to reach its listener, has been established. The fresh native in-memory fixture measures neither UIDs nor listener/network namespace/ingress controls; trusted local process/database control is outside this claim.
- Any browser-specific claim additionally requires a concrete permitted request shape, browser local-network/SOP behavior and actual Host/DNS/ingress facts. No browser test occurred, and present-Origin WebSocket rejection remains an independent preventing control.

### Safe resolution plans

Local: Fresh parent-isolated snapshot-packaged evidence already verifies genuine stock startup refusal and, separately, native dummy-task read/cancel after explicit synthetic authority binding, with credentialed/diagnostics controls. Do not expand this result to working stock startup or real execution. If a supported admitted serving mode is identified, exercise its genuine lifespan with synthetic admission context, then use a disposable isolated two-UID loopback fixture to attempt exactly one unauthenticated dummy held-task read/cancel and verify missing/valid configured-token controls. Browser testing is a separate concrete request/policy experiment only if that claim remains relevant; no deployed endpoints or real stores are needed.

Deployment: The owner can inspect launch/embedding code and configuration presence without revealing secrets, opening production databases or sending service traffic: establish whether any admitted authority is actually served with an empty token, which local principals and network namespaces can reach it, whether any such principal is outside the intended trust boundary, and applicable Host/Origin/ingress restrictions. If no admitted anonymous serving mode or excluded reachable principal exists, reject the deployed access claim. Do not create credentials, provision authority, enable an executor or change deployed access merely to validate it.
