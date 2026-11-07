# Coverage and limitations

**Revision limit:** ongoing implementation changed 9 captured paths and added 1 public path after the cutoff. Those later bytes are unreviewed; see [exact post-cutoff list](POST-CUTOFF-CHANGES.md). Findings apply to the frozen revision.

51 deterministic units: 3 blocked, 2 candidate, 46 covered. Two candidate-status units link the one independently disposed needs-validation record; these are not unvalidated candidates. Three blocked units retain external filesystem/custody/deployment-dependency assurance facts. Screenshot unit is covered with rejected disposition. No planned/in-progress/deferred source units remain.

Six hunting waves, independent post-wave critics and a distinct final-clean critic reviewed active source and every captured delta. No compatible external prior structured run existed; historical reports did not suppress current review.

| Required area | Units/groups | Evidence/limit |
|---|---|---|
| 1 Authentication/API/WebSocket | http; ws | Token/origin/Host policy and accepted-session cleanup; A remains conditional. |
| 2 Queue/scheduler/execution lifecycle | authority | Durable receipts/occurrences/outbox, cancellation and policy/deadline checks. |
| 3 Authority/capability boundaries | authority; delta-runtime; packaged-transport | Server actor scope, synthetic adapter whitelist, offline registry integration. |
| 4 Replay/request identity | authority; final-registry; current broker | Exact UUID/payload/operation/permit binding and durable replay control. |
| 5 Synthetic/future real executor | authority; legacy | Exact synthetic types; real integration absent; server/registry real effects refused; transport same-process pure synthetic. |
| 6 SQLite/fencing/crash recovery | authority; ledger; final-registry | Writer locks/generations/UNKNOWN plus two isolated hot-journal cases; no power-loss claim. |
| 7 HMAC/rollover/antirollback | ledger; final-registry | Fresh-byte verification, retained ancestry and external minimum reference. |
| 8 Enrollment/genesis/trust anchor | recovery | Explicit disposable admission, separate custody/permit/witness, no auto-enrollment. |
| 9 Archive/restore/branch | recovery; final-registry | Fixed reconstruction and inert restores with preserved original identities. |
| 10 Decisions/witness renewal | final-registry; delta-runtime; packaged-transport | Final current registry, expiry/CAS/renewal/reconciliation and non-activation. |
| 11 Operator CLI/recovery | recovery; delta-runtime; deploy | Inherited descriptors, explicit commit, scope and authentication; final POST/fallback fixes verified. |
| 12 Resource exhaustion/bounds | authority; legacy; ws; voice; current broker | Caps and finite reproductions; history/node/body/queue/physical quota gaps noted. |
| 13 Filesystem/permissions/races | ledger; recovery; screenshot; current broker | B exact-chain rejection; different-UID assurance blocked; screenshot current application path rejected. |
| 14 Config/environment/secrets | deploy; helpers; delta-runtime | Safe YAML/strict sections, token/env precedence, key descriptors and diagnostics. |
| 15 Proxmox broker/worker/restricted identity | infra-current-chain; infra-current-files | Current documented successor and 18 selected synthetic cases; installed qualification unknown. |
| 16 Desktop/HUD/PWA/external routes | http; helpers; screenshot | Three clients, Electron bridge, rendering/caching, routes and dormant screenshot helper boundary. |
| 17 Dependencies/supply chain | lockgraph; deploy; current broker | Electron lock/source manifest reviewed; deployed/Python graph/advisory qualification blocked. |
| 18 Deployment/operations | deploy; current broker; threat model | Compose/container/CI/backup/installer/unit assumptions; no production action. |

## Practical limits

390 hashed public source/test/doc/manifest files include all maintained app/client/script/evaluator code, root task utilities and the current documented broker successor. Coverage is by entrypoint/boundary/attack class, not a claim every line/test executed. Trivial initializers/reexports add no privileged action; sealed evidence and binaries are excluded from active-code conclusions.

The final bounded pass reviews the 16-path packaged delta, including transport/authority/recovery/offline CLI and process/VAD/WS/CLI fixes. Publication of operator-reconciled transport evidence now requires separate explicit authority; live state is rechecked before report commit. Process actor tests do not add an external executor identity. Eight safety and eight transport cases passed in this capture. Across all snapshots 101 selected regression cases passed, plus precise microfixtures; these are separate revision-tagged checks, not a full current suite. Python3.14 audit dependencies differ from unqualified Docker3.11/native deployment stacks.

No production configuration, real database/credential, installed credential-bearing observer helper, model/provider, desktop/audio, guest/PVE endpoint, ACL/token/NIC/console/power action or privileged Gate6K qualification was used. No installation, heavy or concurrent target test, shared availability stress or physical power-loss qualification occurred.

Captures use stable per-file reads and immediate rehash, not atomic cross-file snapshots. Exact cutoff is in run-metadata.json. source-stability-packaged.json records any subsequent drift. Source edited after that cutoff is explicitly unreviewed and requires a new delta pass; the report does not silently extend its conclusions to later bytes.

Actual admitted anonymous startup, excluded local UID/browser reachability, different-UID ancestry/ACL/mount/namespace controls, installed dependency/advisory graph, binary provenance, broker role/unit/TTY/guest/API/custody enforcement and trustworthy time remain external facts, neither assumed present nor absent. This is a completed source assessment with explicit assurance limits, not deployment certification.
