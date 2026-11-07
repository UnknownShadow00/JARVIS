# JARVIS V2 comprehensive security audit R1


Reviewed 385 captured files and 46 explicit coverage units across the complete active JARVIS application, clients, automation and documented current Proxmox broker successor. Final source identity: `f4cac30259a7bf4610add2063679ae49138ee637+dirty-snapshot:ac7ab490e6e3fa3900f26cfc8e8ab50e86e3e14482a8d2ec1f3024e33252581b`. The standard Cloudflare workflow used four hunting waves, fresh coverage critics, independent candidate validation and separate final record verification.

**0 confirmed security vulnerabilities; 2 independently reviewed conditional leads.** Severity is assigned only to confirmed records. The audit also reproduced six implementation defects affecting stop/confirmation, duplicate effects, process selection, recording limits, WebSocket cleanup and CLI fallback. Their exact effects, conditions and fixes are separate from vulnerability claims.

Hypothesis A demonstrated anonymous read/cancel only with synthetic admitted authority; stock startup and actual other-UID/browser reachability remain unresolved. Hypothesis B's exact tested SQLite substitution was rejected, while deployed ancestor replacement assurance remains unqualified. Screenshot temporary storage remains a separate conditional different-UID lead.

Source controls preserve request identity, scoped receipts, synthetic executor isolation, HMAC/checkpoint continuity, explicit enrollment, inert restore and nonactivating recovery decisions. Current broker source and 18 selected synthetic cases were reviewed; actual identities, services, guest and production qualification remain external facts.

Prioritise the common emergency-stop gate, process ownership tracking, privileged-route authentication and private screenshot output, then retry/buffer/cleanup/CLI fixes and deployment provenance. Application source was not modified. All tests used synthetic state under bounded OS isolation; no production system, real database/credential, provider or VM was used.

## Scope and evidence

Profile: standard. No agent budget was specified. Final 385-file source is snapshot-expanded; base HEAD is `f4cac30259a7bf4610add2063679ae49138ee637` with current dirty/uncommitted code captured. Exact source/skill hashes, source transitions, isolated reproduction commands, artifact provenance and the 46-unit ledger are retained. No compatible earlier structured audit ledger/findings existed.

This is a comprehensive current-source assessment with explicit external-assurance limits. See [Scope/inventory](SCOPE-AND-INVENTORY.md), [Threat model](THREAT-MODEL.md), [Coverage/limits](COVERAGE-AND-LIMITATIONS.md), [Validation summary](validation-summary.json) and [Machine findings](findings.json).

## Confirmed security findings

No confirmed exploitable security vulnerability met the required evidence gate. No severity is assigned to conditional leads or ordinary hardening defects.

## Conditional leads requiring validation

| Lead | Fingerprint | Decisive blocker |
|---|---|---|
| Shared temporary screenshot namespace may redirect capture output across OS users | `app/computer/screenshot.py:shared-temp-output` | The effective capture temporary root, its ancestor and generated-directory permissions/ACLs, umask, namespace isolation and applicable OS link protections are unobserved. A different OS principal capability to precreate/populate the namespace or influence an output leaf has not been established. A private per-user root with protected ancestors, or a protected victim-owned 0700 directory, can prevent the proposed path. |
| Anonymous loopback authority access remains conditional on an admitted serving deployment | `app/server.py:anonymous-loopback-authority` | No actual serving launch or supported deployed embedding with an admitted authority and an empty configured token has been established. The current stock runtime opener fails admission for missing/enrolled/legacy stores without the required externally supplied context; a synthetic bind does not demonstrate ordinary deployed startup. |

Complete traces, evidence, blockers and safe plans: [NEEDS-VALIDATION.md](NEEDS-VALIDATION.md). Previous hypotheses and rejected escalations: [HYPOTHESES-AND-FALSE-POSITIVES.md](HYPOTHESES-AND-FALSE-POSITIVES.md).

## Reproduced implementation defects

| Priority | Defect | Evidence |
|---|---|---|
| P1 | Queued confirmation executes while emergency stop remains active | [D1](agents/hunt-legacy/artifacts/legacy_effects.txt) |
| P2 | Streaming failure repeats an already completed tool effect | [D2](agents/hunt-legacy/artifacts/legacy_effects.txt) |
| P1 | Shutdown selects and terminates an unrelated same-UID process | [D3](agents/hunt-process/artifacts/process_selection.txt) |
| P2 | Continuous speech bypasses recording frame cap | [D4](agents/hunt-voice/artifacts/vad_bounds.txt) |
| P2 | Malformed accepted WebSocket sessions retain manager entries | [D5](agents/hunt-ws/artifacts/ws_cleanup.txt) |
| P2 | CLI POST omits credential and treats HTTP failure as offline | [D6](agents/hunt-deploy/artifacts/deploy-controls.txt) |

Details, bounded native reproductions and smallest fixes: [IMPLEMENTATION-DEFECTS.md](IMPLEMENTATION-DEFECTS.md). These priorities schedule repairs and do not denote vulnerability severity.

## Validation and positive controls

| Source capture | Selected cases | Retained result |
|---|---:|---|
| snapshot | 10 | [ledger_controls](agents/hunt-ledger/artifacts/ledger_controls.txt) |
| snapshot | 8 | [recovery-controls](agents/hunt-recovery/artifacts/recovery-controls.txt) |
| snapshot | 14 | [infra-controls](agents/hunt-infra/artifacts/infra-controls.txt) |
| snapshot-current | 7 | [current-regressions](agents/parent-current/artifacts/current-regressions.txt) |
| snapshot-current | 10 | [registry-controls](agents/parent-registry/artifacts/registry-controls.txt) |
| snapshot-final | 6 | [proposed-tests](agents/hunt-final-registry/artifacts/proposed-tests.txt) |
| snapshot-final | 2 | [hot-journal-controls](agents/parent-final/artifacts/hot-journal-controls.txt) |
| snapshot-expanded | 8 | [current_chain_controls](agents/hunt-infra-current-chain/artifacts/current_chain_controls.txt) |
| snapshot-expanded | 10 | [current-file-controls](agents/hunt-infra-current-files/artifacts/current-file-controls.txt) |

These are separate revision-tagged checks, not one full current-suite baseline. Additional tiny fixtures establish precise mechanics. Current source preserves token/Origin rejection when configured; scope/payload/operation-bound replay; writer ownership/cancellation/revocation fencing; exact synthetic adapter restrictions; fresh-byte HMAC/continuity/rollover verification; explicit genesis/witness admission; fixed-schema inert restore; and permit/reference/expiry/CAS-bound recovery history with activation/execution false. Two isolated hot-journal cases verified authenticated reconciliation and foreign-custody refusal without writes.

## Dependency, configuration and operational assumptions

Electron has an exact source lock; Python resolution and deployed/binary/advisory qualification remain unknown. Containers, clients, helper output, downloads, custody/time and actual installed infrastructure need the owner evidence listed in [DEPENDENCY-AND-CONFIGURATION-RISKS.md](DEPENDENCY-AND-CONFIGURATION-RISKS.md). Source-only/synthetic evidence establishes design and fixture behaviour; actual production and multi-UID enforcement were not observed.

## Prioritised remediation

[RECOMMENDED-FIXES.md](RECOMMENDED-FIXES.md) lists concrete source changes and acceptance invariants. No application fix, token/ACL, package installation, real execution activation or privileged qualification was performed during this audit.

## Coverage conclusion

40 source-covered units; 3 record-linked units for independently disposed leads; 3 external-assurance blocked units; zero planned/in-progress or unvalidated candidate records. Distinct final-clean coverage review accepted the expanded current source selection after the successor broker was added. Each retained confirmed/needs-validation record received an independent final record review.
