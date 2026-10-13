# Coordinated checkpoint and fault qualification

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

CheckpointWriter publishes version2 coordinated snapshots containing controller, D04/D09 bridge, high-water, domain ledger, per-model D06 scope/state/marker, lineage and minimized receipts. Individual files are exclusive/no-follow, private and fsynced; a manifest hashes the exact membership, staging directory is fsynced, then renamed and parent fsynced. Unpublished .pending directories remain identifiable evidence. Published artifacts are never automatically reused or pruned.

Validation cross-checks controller/global accepted identities, terminal/bindings, ownership holds and D04 receipt/step/correlation joins. READY requires settled known evidence. Final uncertain state produces FORENSIC_INCOMPLETE. Offline restore_for_review refuses occupied destinations and supplied newer high-water; it is export only and cannot replace runtime/protected roots or reopen an epoch.

PROCESS_CRASH_QUALIFIED: child os._exit at global reservation, before publication, after publication, plus existing controller crash cases. FILESYSTEM_FAULT_QUALIFIED: disposable ext4, fsync execution, atomic publication, corrupt/symlink members, disk-full simulation, short-write baseline, partial D04 append/join, competing domain writers and stale restore refusal. See exact test logs. No filesystem unmount, kernel fault, host stall or power interruption was induced.

HOST_POWER_LOSS_NOT_PROVEN. Same-host snapshots do not provide host-loss protection. Synchronous SQLite/fsync cannot promise a 30-second wall-clock drain during a disk stall. Static ancestor checks and same-UID parent ownership are not privileged race protection; dirfd/privileged parent and real separate-UID adversarial qualification remain release work. External resource actors are not checkpoint-coordinated by this fixture graph.

Proposed renewed acceptance (NOT accepted): the operator explicitly accepts loss of all V3 local evidence on Core/volume loss for this bounded pilot only, states retention/restoration policy and confirms no inference to production durability or formal P7 exit. V2's earlier local-backup acceptance does not automatically cover the revised multi-provider V3 design.
