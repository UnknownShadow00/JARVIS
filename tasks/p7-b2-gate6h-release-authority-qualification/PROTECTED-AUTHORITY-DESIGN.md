# Protected authority design — isolated companion, integration pending

The minimum boundary is a protected writer identity whose files, readers and key policy the application/service and development agent cannot alter. Hashes in service-writable roots do not supply that boundary. Gate6H adds a companion transaction engine and a socket handler at the existing local-control boundary. The production factory still refuses. application.py and CheckpointWriter still use local HighWater/direct DB access: replacing this coupling with an authenticated client/export adapter is a release blocker. This is not a protected end-to-end production runtime.

## Proposed arrangement

| Principal | Allowed authority | Excluded authority |
|---|---|---|
| Root installer | Own release/config/dependencies/unit, public-key policy and authority parent | No agent-accessible general sudo/helper commands |
| jarvis-authority, non-login | Narrow writer to private protected lineage/high-water/nonce/evidence store | No shell, provider network/proxy, credentials, model lifecycle or admin API |
| jarvis-v3, non-login | New controller/D04/D06/domain/checkpoint state and approved provider transport | No signer key, protected root/parent write, mutable release/config/imports or operator identity |
| jarvis-op, separate human | Reviewed console/hardware signer and operator socket | Application Bearer alone cannot impersonate this identity or authorize signing |
| Existing jarvis/nexus agent | Isolated source/documentation work | No service credentials, signing keys, authority writes or production administration |
| Independent evidence/witness owner | Terminal/resource association and append-protected external receipts | Never treats service-supplied clean/terminal flags as independent evidence |

Proposed layout: root-owned /opt/jarvis-v3/<inventory-digest>, directories0755/files0644, protected config and pinned interpreter/dependencies; no writable import, PYTHONPATH or cwd path. /var/lib/jarvis-authority parent root0755, private child jarvis-authority0700, DB0600/single link, no symlinked or attacker-writable ancestors. New application state roots jarvis-v3:0700. Operator socket directory root-owned0750/dedicated operator group, socket0660, actual SO_PEERCRED UID check. Separate service socket admits only fixed read/reconcile/checkpoint/reservation/substep requests. Neither socket signs. No production listener/service transport was installed.

## Actual delivered prototype

candidate_v3/protected_authority.py reuses Authority, successor_payload and the Gate6G signed envelope. Ed25519Verifier uses standard public-key verification only. Test private keys are ephemeral and never exported. A signature proves key possession, not human touch. The fixture's user_present result is a console/peer policy convention, not hardware-presence evidence. Production needs an approved separately authenticated human confirmation flow or reviewed hardware presence mechanism; neither is implemented here.

ProtectedJournal uses SQLite BEGIN IMMEDIATE, synchronous=FULL, rollback journal, unique nonces and an append-only event table with sequence/hash-chain and schema/ownership/mode/link/ancestor/inode checks. Triggers/hashes support consistency; the OS boundary excludes hostile service writes. Every mutation/read checks a helper-side current identity reader. No create-on-open fallback, reset/restore/rebind/delete/arbitrary SQL/path/sign/provider API exists.

SUCCESSOR verifies the exact original payload, current predecessor before/after signature verification, source/config/archive/controller/live bindings, operator peer/expiry and unused nonce. Singleton root and nonce commit together. ACCEPT burns the next ordinal REST/REST/WS/WS before local acceptance, no refund after uncertain acknowledgement/crash. Another permit requires verified checkpoint.

Protected SEND records accepted ordinal, role, pinned resource identity and request digest before transport. Classifier is optional, exactly one responder precedes observer, max3 substeps. Pending SEND survives restart and blocks checkpoint/new send/next permit. SETTLE requires exact associated terminal evidence from a protected independent reader. Timeout/cancel/process absence/restored service ledger does not settle. The real independent terminal reader is absent; tests use fixtures. Attempt counts alone would miss provider-ledger rollback within an attempt; protected SEND/SETTLE addresses that transaction gap in isolation.

The helper-side checkpoint reader must independently validate fixed-path controller/D04/D06/domain/receipt/delivery/observation evidence, accepted associations, current protected sequence, no proposals/unknowns and the coordinated digest. A service callback returning clean:true is not adequate. Helper-side source/config/release/dependency/process reader must recompute protected identities, not echo service strings. These readers and runtime/client wiring remain blockers.

candidate_v3/local_control.py contains AuthoritySocket: real AF_UNIX SO_PEERCRED, operator UID, bounded20,000-byte envelope, canonical body ≤8192 via Authority, exact64-byte Ed25519 signature, one packet/connection, total read deadline and bounded response write. No JSON peer UID/PID is trusted. Existing socket import boundary remains unchanged. Read/checkpoint service transport is not installed.

## Durability, recovery and external root

Commit is authoritative. Real child exits before commit leave the command unconsumed; after commit nonce/reservation/SEND remains burned even without acknowledgement. Never retry provider work blindly. Restart compares fresh invocation/source/config and durable state; no rebind exists, changed identity refuses, and current V3 runtime restarts CLOSED_RECOVERY_HOLD. Unexpected stop does not establish human attribution or remote completion.

Missing/corrupt/inconsistent/unavailable authority refuses, never recreates itself. Backups are review-only, not authority restoration. Recovery needs separately reviewed equal/newer external evidence retaining all consumed authority; no recovery command exists. Process-crash tests do not qualify storage power loss, host rollback or host loss.

A separate on-host authority can resist ordinary service-UID rollback under trusted root/kernel. Actual distinct-UID qualification is pending. Arbitrary root or hypervisor/physical-host rollback can replace the authority and its proofs together; the negative test demonstrates this. Stronger assurance needs independently administered off-host append-protected witness of authority identity/seq/seal/predecessor/successor/accepted/pending intent, durable BEFORE acknowledgement, rechecked before startup/progression. No witness was implemented/contacted. Local-only exposure must be explicitly accepted if selected; it never becomes root-rollback protection. Compromise of both domains remains outside the guarantee.

Standard references: [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html), [Linux AF_UNIX peer credentials](https://man7.org/linux/man-pages/man7/unix.7.html), [Ed25519 public-key API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/). This applies standard primitives; it is an engineering design, not a new cryptographic protocol or external certification.
