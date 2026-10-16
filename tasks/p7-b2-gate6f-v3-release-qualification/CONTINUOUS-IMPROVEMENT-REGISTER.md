# Continuous improvement register (Gate 6F)

Candidate `ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733`, predecessor 6E r2 `c28942a9…`. Patch `candidate-vs-gate6e-r2.patch` (`03a25969…`), 11 files changed (9 source, 2 tests), none removed.

## Completed fixes

| ID | Severity | Problem | Fix | Tests |
|---|---|---|---|---|
| F01 / G6F-SEC-01 | High | `OPERATOR_STOP` from V2 is written on any shutdown; archive validation treated it as operator retirement (production now has exactly that shape after a power-off) | Proof carries `stop_attribution`; retirement intent only from the signed successor payload; renamed refusal | source-proof AST test; archive/successor tests |
| F02 | High | Shared host behind different ports or alias endpoints was invisible to D06 domains unless hand-declared | `topology.py`: attested host/GPU/service domains, fail closed on unverified, explicit residency approval for B/C; app graph requires it | topology A–D, attestation strictness, graph requirement, same-host-other-port conflict |
| F03 | Medium | Next permit only re-verified the local controller checkpoint | `OPEN_HOLD`/`AUTHORIZE_ONE` re-validate coordinated bundle (bound to controller checkpoint), evidence health and high-water | permission-drift test; full suite |
| F04 | Medium | Replayed signed `TERMINAL_STOP` set the in-memory stop before the durable nonce failed; replayed permits surfaced raw `IntegrityError` | Durable nonce checked before any effect; `CONTROL_REPLAY` | 3 replay tests |
| F05 | Medium | Known D06 conflict recorded a possible-send and permanently held domains as REMOTE_UNKNOWN | `OwnedProvider.precheck` before `Store.begin` | 2 tests |
| F06 | Medium | 6E qualification used an empty memory snapshot (not source-faithful) | `source_memory.procedural_snapshot`, digest-pinned, no truncation | build_prompt byte-equality test |
| F07 | Low | Control socket: 2 s per recv, no whole-request bound | 5 s whole-request deadline | trickle test |
| F08 | Low | Tampered V2 archives leaked historical exception types | fixed `V2_ARCHIVE_INVALID` code | 5 mutation tests |

No existing assertion was weakened. One test fixture changed: `Integrated` now supplies an explicitly `OFFLINE_FIXTURE` topology because the graph requires one. Two first-run test bugs in the new file (envelope arithmetic, read-only V2 bundle) were corrected; one environmental failure (Landlock canary file wiped by the Core reboot) was resolved by recreating the empty canary in `/tmp`. All logs retained.

## Approval-dependent proposals (not implemented as defaults)

| ID | Proposal | Needs |
|---|---|---|
| P01 | G6F-LP-2: normal responder `num_ctx` 8192 | X4 + Modelfile attestation |
| P02 | Bind memory snapshot digest into the release contract | X3 |
| P03 | Wall-clock permit expiry shared with signer | release design |
| P04 | Off-host / privileged append-only high-water authority | OS provisioning |
| P05 | `NOT_DISPATCHED` step state for refusals after possible-send but before transport | controller schema change (schema 6) |
| P06 | V2: record the real stop cause instead of defaulting to `OPERATOR_STOP` | production change, out of scope |
