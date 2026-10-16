# Evidence manifest — Gate 6F VM-event addendum

The packet was created with an exclusive `mkdir` (no `-p`; it fails if the directory exists), under umask 077. The Core mirror was made the same way. `SHA256SUMS` covers every file in the packet except itself. The seal is SHA-256(`SHA256SUMS`), reported outside the file to avoid self-reference.

## Referenced (unchanged) prior evidence

| Item | Value | Verified 2026-10-15 |
|---|---|---|
| Gate 6F seal | `df3090b9e459b192dc7c23a6bd8113ce4d5d9814c7e370dcad27bbcf554bda06` = sha256(`/home/jarvis/.hermes-poc/evidence/p7-b2-gate6f-v3-release-qualification/SHA256SUMS`) | yes, all members OK |
| Candidate digest | `ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733` = sha256(`candidate/CANDIDATE-SOURCE-SHA256SUMS`) | yes, 29/29 members |
| Candidate full inventory | `d31191bc…`, 596 files under `gate6f-candidates/release-r1/` | yes, 596/596 |
| Older archives | gate6d original-0d81f9fd4921, gate6d engineering-r1, gate6e engineering-r1/r2 | present |
| V2 terminal backup | `/home/jarvis/.hermes-poc/backups/p7-b2/62f417a2…`, manifest `1b59208c9c1243383fbe907faf4440808256c3eed05d35dc33a97eab483025c5` | 5/5 components |

## Packet contents

| File | What |
|---|---|
| FINAL-REPORT.md | verdict, 14 answers, corrections, statuses |
| VM-IDENTITY-VERIFICATION.md | guest identities; human-only Proxmox mapping commands |
| NEXUS-MAINTENANCE-TIMELINE.md | Nexus agent shutdown and resource upgrade |
| JARVIS-CORE-POWER-EVENT-TIMELINE.md | Core ACPI power-off/boot timeline |
| PROXMOX-AUDIT-CORRELATION.md | unverified Proxmox side; human-only audit commands |
| V2-CURRENT-STATE.md | read-only V2/controller state |
| OPERATOR-STOP-SEMANTICS.md | source analysis of `OPERATOR_STOP` |
| V3-SUCCESSOR-IMPLICATIONS.md | candidate review, H-1..H-4, limited exception spec |
| REMAINING-OPERATOR-DECISIONS.md | ordered decisions |
| evidence/core-identity.txt | Core hostname, machine-id, boot list, MAC, CPU/RAM per boot |
| evidence/core-power-event-excerpt.log | filtered Core journal 03:39:55Z–03:43:22Z |
| evidence/core-interactive-logins-2026-10.log | October password logins and power events; key-login count; sudo count |
| evidence/core-context.txt | previous kernel, guest-agent state, linger, kernel-38 install date |
| evidence/nexus-identity.txt | Nexus hostname, machine-id, boot list, MAC, CPU/RAM per boot |
| evidence/nexus-maintenance-excerpt.log | Nexus qemu-ga events, shutdown and boot |
| evidence/v2_readonly_state.py | the write- and network-refusing readback tool |
| evidence/v2-current-state-readback.json | its output, 2026-10-15T19:14:30Z |

Redactions: SSH source ports, sshd PIDs, login session numbers and key fingerprints. No credentials, tokens or environment contents were read or included.
