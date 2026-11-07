# Needs validation

Only independently verified source-grounded conditional leads appear here. No severity is assigned.

## Shared temporary screenshot namespace may redirect capture output across OS users

Fingerprint: `app/computer/screenshot.py:shared-temp-output`.

Screenshot capture accepts preexisting filesystem state in a fixed jarvis_screenshots directory under the effective temporary root and selects a second-resolution PNG name. If a different OS principal can control that namespace or its leaf entries and the installed PNG writer follows those paths, a later victim capture could disclose screen bytes through an attacker-controlled output or overwrite a victim-writable file. Final source supports this conditional path, but it does not establish the effective temporary namespace, OS permissions, installed writer or operational capture environment. No separate-UID disclosure or overwrite was demonstrated. Native helper call paths exist outside serving authority HTTP requests; their actual operation was not observed.

Claimed root cause: Generated screenshot storage accepts preexisting directory and leaf path state without owner/mode validation, a pinned private directory or descriptor-bound exclusive publication; whether another OS principal can influence that state is deployment-dependent.

### Source trace

1. [app/computer/screenshot.py:24](snapshot-expanded/app/computer/screenshot.py#L24) (capture): The default fixed temporary namespace is selected; mkdir(exist_ok=True) accepts preexisting directory state without checking ownership or permissions. A lower-trust OS principal can supply this state only if the effective namespace permits it.
2. [app/computer/screenshot.py:27](snapshot-expanded/app/computer/screenshot.py#L27) (capture): The output basename depends on the capture second, and an absolute pathname is constructed without opening or pinning its directory or leaf.
3. [app/computer/screenshot.py:32](snapshot-expanded/app/computer/screenshot.py#L32) (capture): Captured RGB bytes are passed to the installed mss.tools.to_png writer using the constructed pathname; the application creates no verified exclusive/no-follow output descriptor.

### Evidence

- [app/computer/screenshot.py:19](snapshot-expanded/app/computer/screenshot.py#L19): mss is imported before directory selection or hardware capture; absence prevents this path from executing.
- [app/computer/screenshot.py:24](snapshot-expanded/app/computer/screenshot.py#L24): Temporary root selection is runtime-dependent, and the fixed child directory receives no ownership, permissions or symlink validation.
- [app/computer/screenshot.py:27](snapshot-expanded/app/computer/screenshot.py#L27): The second-resolution output name is predictable and no verified output descriptor is created by the application.
- [app/computer/screenshot.py:32](snapshot-expanded/app/computer/screenshot.py#L32): The installed PNG writer receives a pathname rather than a retained verified descriptor.
- [app/computer/screenshot.py:42](snapshot-expanded/app/computer/screenshot.py#L42): The normal execute wrapper refuses real capture in global dry-run mode.
- [app/tools/registry.py:236](snapshot-expanded/app/tools/registry.py#L236): Strict approval mode requires confirmation even for the Level0 screenshot tool; normal registry dry-run also gates execution.
- [app/brain/tool_params.py:69](snapshot-expanded/app/brain/tool_params.py#L69): Ordinary screenshot chat requests construct only monitor parameters; they do not expose arbitrary output_dir input.
- [app/voice/audio_stream.py:96](snapshot-expanded/app/voice/audio_stream.py#L96): Native voice routes transcripts through the tool-processing helpers directly, without depending exclusively on HTTP application lifespan.
- [app/computer/vision.py:44](snapshot-expanded/app/computer/vision.py#L44): Screen analysis calls the same capture helper; its later file read at104-105 is pathname-based.
- [requirements-desktop.txt:40](snapshot-expanded/requirements-desktop.txt#L40): Desktop installation declares mss>=9.0.0, which does not establish the exact installed writer implementation or an operational desktop.
- [tests/test_screenshot.py:52](snapshot-expanded/tests/test_screenshot.py#L52): The existing capture test replaces the PNG writer with a mock; it cannot establish real writer behavior, cross-UID permissions or shared-temp effects.

### Decisive blockers

- The effective capture temporary root, its ancestor and generated-directory permissions/ACLs, umask, namespace isolation and applicable OS link protections are unobserved. A different OS principal capability to precreate/populate the namespace or influence an output leaf has not been established. A private per-user root with protected ancestors, or a protected victim-owned 0700 directory, can prevent the proposed path.
- The approved audit toolchain contains no mss desktop dependency, and the exact deployed writer version, capture enablement and operational display access are unknown. The parent static upstream MSSv9.0.1 writer observation corroborates ordinary pathname opening in that version only. Existing mocked-writer tests and same-UID source tracing do not establish an unauthorized cross-UID file result under the effective OS/runtime controls.

### Resolution

Local: When an isolated disposable environment provides two dummy UIDs and the already available relevant mss dependency, use a synthetic shared temporary root and mock only pixel acquisition. Use the real PNG writer. Predeclare one harmless output and one victim-owned dummy file; let the lower-trust UID prepare only the synthetic namespace, invoke one victim capture and stop after observing rejection, redirected synthetic bytes or dummy-file overwrite. Compare a victim-owned 0700 private root with protected ancestors. Record effective owner/mode/ACL/umask and link protections plus writer version. Use no real screen, host temporary directory, production file or credential; do not download/install dependencies or alter real accounts.

Deployment: The owner can inspect capture enablement, installed mss version, effective TMPDIR/TEMP or per-user temporary root, generated-directory and ancestor ownership/ACLs, umask and private-temp isolation without displaying screenshots or credentials. Determine whether a different local UID can create or replace relevant directory/leaf entries. No production capture or service probe is needed.

## Anonymous loopback authority access remains conditional on an admitted serving deployment

Fingerprint: `app/server.py:anonymous-loopback-authority`.

Empty-token loopback mode deliberately permits ordinary HTTP requests without a credential, and authority routes assign each accepted request the shared local-service actor. An untrusted local OS principal reaching a serving instance in that mode could read or cancel an operator task. Independent parent-isolated verification of the final source exercised genuine stock lifespan with its missing synthetic database: admission failed before database creation. After explicit synthetic authority binding, native in-memory requests read and cancelled one dummy task without credentials; configured-token and operator-diagnostics controls rejected absent credentials. These results establish conditional route behavior, not a deployed or cross-UID/browser exploit. The normal opener supplies neither ledger/enrollment witness nor explicit legacy approval; serving deployment and local-client trust facts remain unresolved. Present-Origin WebSocket checks are a separate preventing control.

Claimed root cause: Ordinary privileged HTTP routes accept anonymous requests when the configured API token is empty, then use the server-owned service actor rather than a network-caller identity. Whether this crosses an actual lower-trust principal boundary depends on the admitted deployment and its local-client trust model.

### Source trace

1. [app/server.py:239](snapshot-expanded/app/server.py#L239) (api_token_middleware): An ordinary HTTP request is passed onward without credential verification when server.api_token is empty.
2. [app/agent/api.py:103](snapshot-expanded/app/agent/api.py#L103) (cancel): DELETE /tasks/{task_id} supplies the server-owned SERVICE_ACTOR plus the caller-selected canonical task and request identities to Authority.cancel.
3. [app/agent/authority.py:428](snapshot-expanded/app/agent/authority.py#L428) (Authority.cancel): The actor scope selects the task passed to the cancellation effect inside the authority mutation and receipt transaction.
4. [app/agent/authority.py:421](snapshot-expanded/app/agent/authority.py#L421) (Authority._cancel): For a held task, status and outbox state become cancelled; _put persists the task in the surrounding fenced transaction.

### Evidence

- [app/config.py:108](snapshot-expanded/app/config.py#L108): The API token defaults to empty; the validator at114-136 permits this only for configured loopback mode and requires a nonempty token for remote/nonloopback configuration.
- [config.yaml.example:103](snapshot-expanded/config.yaml.example#L103): The public example selects127.0.0.1, an empty token at112 and remote_access_enabled:false at113; its comments explicitly describe anonymous localhost-only use.
- [app/server.py:240](snapshot-expanded/app/server.py#L240): Empty configured token bypasses the ordinary HTTP credential check; nonempty token is constant-time compared through _api_token_ok.
- [app/server.py:404](snapshot-expanded/app/server.py#L404): The authority router is mounted in the actual FastAPI application.
- [app/agent/runtime.py:7](snapshot-expanded/app/agent/runtime.py#L7): Ordinary authority routes share Actor("local-service"); the HTTP caller does not choose a separate actor scope.
- [app/agent/api.py:86](snapshot-expanded/app/agent/api.py#L86): Operator diagnostics independently refuses requests unless a configured matching Bearer credential exists, including when ordinary routes allow anonymous mode.
- [app/main.py:11](snapshot-expanded/app/main.py#L11): The stock entrypoint starts the reviewed app using configured host and port.
- [app/server.py:114](snapshot-expanded/app/server.py#L114): Application lifespan must open the authority before readiness, scheduler, listeners or background startup work.
- [app/agent/runtime.py:17](snapshot-expanded/app/agent/runtime.py#L17): The default opener supplies only the database and legacy JSON paths; no ledger, enrollment witness or explicit legacy approval is supplied.
- [app/agent/authority.py:107](snapshot-expanded/app/agent/authority.py#L107): A missing, empty or symlinked authority database is refused before directory or writer-lock creation.
- [app/agent/enrollment.py:299](snapshot-expanded/app/agent/enrollment.py#L299): Enrolled store admission requires the external witness and ledger guard; this context is absent from the default runtime opener.
- [app/agent/enrollment.py:338](snapshot-expanded/app/agent/enrollment.py#L338): Legacy store admission requires an explicit OperatorPermits verifier/permit tuple; there is no automatic approval on default startup.
- [app/agent/runtime.py:21](snapshot-expanded/app/agent/runtime.py#L21): A trusted local embedding/test hook can bind an explicitly admitted authority; it is not an HTTP enrollment or activation endpoint.
- [tests/test_server_auth.py:17](snapshot-expanded/tests/test_server_auth.py#L17): The test demonstrating anonymous task access explicitly binds a synthetic approved authority; its TestClient at8 skips lifespan unless used as a context manager.
- [app/server.py:206](snapshot-expanded/app/server.py#L206): Present WebSocket Origin is allowlisted independently before either WebSocket accepts, so HTTP Host/CORS behavior does not prove a cross-site WebSocket bypass.
- [app/agent/authority.py:303](snapshot-expanded/app/agent/authority.py#L303): Scope, operation and canonical payload are bound into durable request receipts; these controls prevent request/scope substitution but rely on the caller identity established before the fixed service actor is assigned.

### Decisive blockers

- No actual serving launch or supported deployed embedding with an admitted authority and an empty configured token has been established. The current stock runtime opener fails admission for missing/enrolled/legacy stores without the required externally supplied context; a synthetic bind does not demonstrate ordinary deployed startup.
- An actual lower-trust different OS principal, excluded by the deployment trust model but able to reach this listener, has not been established. Native TestClient input does not measure OS UID, network-namespace, listener or ingress restrictions. Same-UID control of the process/database is explicitly trusted by the authority contract.
- Browser exploitation additionally depends on the concrete browser/local-network policy, accepted request shape and Host/DNS/ingress behavior. No such browser test was performed; configured-token HTTP routes and foreign-origin WebSocket rejection are preventing controls.

### Resolution

Local: The independent parent-isolated fixture has verified genuine stock lifespan refusal before database creation and conditional native read/cancel only after explicit synthetic authority binding, with configured-token and operator-diagnostics controls. Resolve any claimed usable admitted launch by exercising its actual lifespan using synthetic admission context. If that mode is relevant, use an isolated disposable two-UID/loopback fixture to test one unauthenticated held-task read/cancel and the credentialed preventing controls. Test a specific browser request shape separately under its actual local-network/SOP policy. The in-memory fixture did not create a real socket or browser session and does not measure OS-principal reachability.

Deployment: The owner can inspect launch/embedding code and configuration state without probing the service or revealing credentials: establish whether an admitted authority is actually served with an empty token, which OS principals/network namespaces can reach it, whether those principals are outside the intended trust boundary, and what ingress Host/Origin controls apply. If no serving anonymous admitted mode exists, the deployed exploit claim does not apply. Do not open production databases, extract token values or send audit traffic to production.

The public [MSSv9.0.1 writer source](https://github.com/BoboTiG/python-mss/blob/v9.0.1/src/mss/tools.py) was inspected statically. It uses ordinary pathname output; this establishes one upstream implementation, not the installed desktop version. No screenshot or real desktop was accessed.
