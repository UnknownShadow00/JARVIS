# Coverage and limits

46 deterministic units: 3 blocked, 3 candidate, 40 covered. The 3 record-linked candidate units cover 2 unique conditional leads, each with an independent final disposition. There are no unassigned units or unvalidated candidate records. Three blocked units retain external filesystem/deployment/dependency-assurance facts. Final source coverage critic results are retained separately. No compatible prior Cloudflare ledger/findings file existed.

| Required area | Units/groups | Evidence/limit |
|---|---|---|
| 1 Authentication/API/WebSocket | http; ws | Token/origin/Host policy and accepted-session cleanup; A remains conditional. |
| 2 Queue/scheduler/execution lifecycle | authority | Durable receipts/occurrences/outbox, cancellation and policy/deadline checks. |
| 3 Authority/capability boundaries | authority; delta-runtime | Server actor scope, synthetic adapter whitelist, offline registry integration. |
| 4 Replay/request identity | authority; final-registry; current broker | Exact UUID/payload/operation/permit binding and durable replay control. |
| 5 Synthetic/future real executor | authority; legacy | Exact synthetic types; real integration absent; legacy tools separately scoped. |
| 6 SQLite/fencing/crash recovery | authority; ledger; final-registry | Writer locks/generations/UNKNOWN plus two isolated hot-journal cases; no power-loss claim. |
| 7 HMAC/rollover/antirollback | ledger; final-registry | Fresh-byte verification, retained ancestry and external minimum reference. |
| 8 Enrollment/genesis/trust anchor | recovery | Explicit disposable admission, separate custody/permit/witness, no auto-enrollment. |
| 9 Archive/restore/branch | recovery; final-registry | Fixed reconstruction and inert restores with preserved original identities. |
| 10 Decisions/witness renewal | final-registry; delta-runtime | Final current registry, expiry/CAS/renewal/reconciliation and non-activation. |
| 11 Operator CLI/recovery | recovery; delta-runtime; deploy | Inherited descriptors, explicit commit, scope and authentication; CLI POST defect. |
| 12 Resource exhaustion/bounds | authority; legacy; ws; voice; current broker | Caps and finite reproductions; history/node/body/queue/physical quota gaps noted. |
| 13 Filesystem/permissions/races | ledger; recovery; screenshot; current broker | B exact-chain rejection; different-UID assurance blocked; screenshot lead conditional. |
| 14 Config/environment/secrets | deploy; helpers; delta-runtime | Safe YAML/strict sections, token/env precedence, key descriptors and diagnostics. |
| 15 Proxmox broker/worker/restricted identity | infra-current-chain; infra-current-files | Current documented successor and 18 selected synthetic cases; installed qualification unknown. |
| 16 Desktop/HUD/PWA/external routes | http; helpers; screenshot | Three clients, Electron bridge, rendering/caching, routes and native screenshot boundary. |
| 17 Dependencies/supply chain | lockgraph; deploy; current broker | Electron lock/source manifest reviewed; deployed/Python graph/advisory qualification blocked. |
| 18 Deployment/operations | deploy; current broker; threat model | Compose/container/CI/backup/installer/unit assumptions; no production action. |

## Practical limits

Source selection includes385 hashed text/code/manifest files with all maintained application/client/script/evaluator code and the current documented broker successor. Empty/docstring package initializers and static reexports introduce no separate privileged boundary. Historical task evidence and binaries are excluded from active-code conclusions. Old phase3 and current review-r1 test evidence remain distinct.

No production configuration, real database, credentials, model/provider, actual desktop/audio, installed observer helper, guest/Proxmox endpoint, ACL/token/power/NIC/console or privileged Gate6K operation was used. No availability stress or physical power-loss qualification occurred. Most execution used Python 3.14.4 with the recorded local audit toolchain; the Docker 3.11/native Windows/desktop deployment stacks were not qualified. Selected tests and tiny fixtures are bounded evidence, not the full project matrix.

Snapshot captures are per-file stable and rehashed, not atomic filesystem snapshots. Concurrent Sprint5 changes were recaptured/reviewed twice; the current infrastructure successor was separately frozen and reviewed. Final source-stability evidence records whether all captured files still match the active worktree. Any later edits require a new delta review.

Different-UID path replacement, screenshot shared-temp impact, browser/ingress behaviour, actual admitted server startup, deployed dependency/advisory status, installed role/unit/TTY/API/custody enforcement and secure time remain explicitly unverified. These facts were not assumed present or absent.
