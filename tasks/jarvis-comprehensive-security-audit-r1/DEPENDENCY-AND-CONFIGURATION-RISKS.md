# Dependency, configuration and operational risks

No deployed CVE or supplier-compromise verdict is asserted. dependency-inventory.json records source requirements and the client lock. The separately available audit toolchain is not deployed-artifact evidence.

- Python core/desktop requirements use lower bounds; no complete hashed Python resolution/SBOM is supplied. Capture an approved resolved graph, artifact hashes and advisory status from an owner-produced build inventory before rollout.
- Electron has a consistent v3 package-lock.json: 13 non-root exact package entries, registry HTTPS URLs and SHA512 integrity values, including Electron 42.10.1. This corrects the initial blanket no-lock assumption. Source lock integrity does not establish downloaded Electron binaries, build execution or installed deployment identity.
- Docker base/provider images and CI actions are referenced through mutable tags; Piper/voice downloads lack content-hash verification and a model URL uses main. Pin approved artifacts and verify hashes/signatures. No malicious artifact or exploitable dependency version was established.
- Docker's explicit COPY statements exclude runtime .env/data from image contents, but no .dockerignore bounds context submission. Exclude credentials/state/models/audit artifacts from build contexts. The image has no USER directive; choose a dedicated runtime UID and reviewed mounts/limits.
- Compose publishes host loopback while binding backend 0.0.0.0 inside the shared bridge. Actual command-line bind/ingress and token policy must match the intended trust boundary; configuration host validation does not validate incoming Host or identify a local OS user.
- Token-enabled HTTP/WS checks work in the fixtures. Existing PWA/Electron/hologram clients lack the configured-token browser transport; implement an authenticated browser-compatible channel before enabling remote use. Retain Origin checks; avoid weakening authentication for compatibility.
- Current registry/dictation refuse real effects regardless of legacy approval settings. Direct trusted native helper imports remain separate; future adapters need explicit validated authorization.
- Tool parameters/audit/trace output can contain operator text and paths. Keep private ownership and bounded retention; minimise raw Tailscale/path/diagnostic data. No cross-principal secret disclosure was substantiated from those source paths.
- HMAC keys, latest external references, independent anchor/custody directories and trusted time are operator-provided. Hardware antirollback, rotation and coordinated-custody rollback protection are not established by ordinary files or local hashes.
- Current Proxmox successor uses13 pinned source files, explicit preissuance/root-owned evidence, separate precheck/main modes, peer/grant/receipt checks and proposed unit/seccomp restrictions. Source manifest and RELEASE.json binding were checked; archive execution, installed file ownership, effective drop-ins, restricted identities, serial exclusivity, guest/bootstrap/network state and real CA/API behaviour remain unqualified.
- The Phase2 observer imports an installed credential-bearing helper outside the repository. Its implementation/TLS policy was not opened or run; a constant tls_verified field does not qualify it.

Final integration notes: configured transport requires a token; request/response/operator/ledger keys must be independent. The socketpair is same-process synthetic scope. Preflight canonical encoded byte size: Unicode echo can exceed the response frame cap after escaping, leaving conservative UNKNOWN with durable evidence. Some legacy success tests remain stale despite the reviewed fixes; do not treat an old suite total as a current baseline. CLI wake --offline can start a server before encountering the intentionally denied resource endpoint: align/document the offline workflow without weakening the HTTP denial. No full suite was run.

## Source evidence

| Observation | Frozen source |
|---|---|
| Python lower bounds | [core requirements](snapshot-packaged/requirements-core.txt), [desktop requirements](snapshot-packaged/requirements-desktop.txt) |
| Electron exact resolution/integrity | [package-lock.json](snapshot-packaged/frontend/electron/package-lock.json), [inventory](dependency-inventory.json) |
| Image identity/runtime/COPY | [Dockerfile](snapshot-packaged/Dockerfile#L1) |
| Host publication versus backend bind | [Compose](snapshot-packaged/docker-compose.yml#L44) |
| Mutable CI actions | [workflow](snapshot-packaged/.github/workflows/tests.yml#L13) |
| Voice binary/model downloads | [Piper installer](snapshot-packaged/scripts/install_piper.py#L14), [model installer](snapshot-packaged/scripts/install.py#L15) |
| Broker source/release/qualification policy | [successor README](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/README.md), [source hash manifest](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/src/SOURCE-SHA256SUMS), [live acceptance requirements](snapshot-packaged/tasks/proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md) |

These links substantiate source observations; they do not establish installed versions, active settings or exploitability.
