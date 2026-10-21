# Actual tests and evidence

Final source: evidence/candidate-identity.json; manifests and three-file patch retained. Final run archives match all601 current source/harness files, zero mismatches. No source assertion weakened. Gate6G historical baseline preserved:7541 passed/11 deselected/zero failed.

| Run | Actual result | Filesystem/source |
|---|---|---|
| g6h-focused-r5 |458 passed, zero failed|Final source;375 baseline focused+83 new|
| g6h-full-r4 |7624 passed,11 deselected,zero failed,two existing warnings|Final source; tmpfs isolated stage|
| g6h-ext4-final |83 passed,zero failed|Final source, actual ext4 per findmnt|
| g6h-new-final |83 passed,zero failed|Final source, tmpfs|
| g6h-full-r3 |7623 passed,11 deselected,zero failed,two existing warnings|Earlier82-test revision, ext4; explicitly not final source|
| g6h-focused-r4 |457 passed|Earlier82-test revision|
| g6h-full-r2 /focused-r3 |7602 full/436 focused passed|Earlier61-test revision|

All runs, including unsuccessful ones, appear in evidence/test-summary.json and runs/. Initial new-1:18 failed/42 passed, checkpoint fixture recursively read same connection; fixed by separate fixture snapshot. New-2:1 failed/59 passed, fixture attempted to derive digest from absent checkpoint; corrected to exercise actual refusal. Focused-final launch: nonexistent test filename, no tests ran; corrected filename, not a skip. Focused-r2/full-final: original socket import-boundary assertion rejected new module; moved socket handler into existing local_control.py, kept assertion. Final counts above pass. No failing test silently discarded.

After final83-test addition (writable-parent guard regression), full applicable suite reran. New SEND/SETTLE cases test provider-ledger rollback within accepted ordinal, conservative unknowns, conditional roles, stale terminal/resource identity and actual child exits around commits. Other adversarial cases: Ed25519 wrong key/signature, stale nine-field identities, expiry drift, predecessor drift, nonce/permit replay, dual-connection succession/permit races, global cap/order/session, missing/corrupt/schema/chain authority, symlink/hardlink/owner/mode/ancestor drift, old/all app files rollback, restart/incomplete/older-backup refusal, real peercred/malformed/trickle socket. Owner whole-authority rollback is a required successful negative control.

Same-UID mount-confinement denies write/chmod/unlink/symlink/hardlink; no genuine distinct-UID DAC tests. Public-key crypto is real, private fixture keys ephemeral. Readers/model/resource evidence synthetic. Real process os._exit tests are not power-cut/host-loss qualification. No real provider calls.

Static compile140 app/candidate Python files passed, pip check clean, no dependencies installed. Core app venv lacks cryptography: test-only /usr/lib/python3/dist-packages exposes existing system46.0.5 to tests. This is an explicit production packaging blocker; pip check is not a vulnerability audit or dependency lock.

Final full sandbox uses Landlock ABI8 and seccomp, home/production state and credentials denied, no INET/PACKET sockets/connect/signals/ptrace/process-vm/mount/reboot/bpf/io_uring. Trusted supervisor signaled only verified disposable direct children for old crash tests. Full run encountered15 pre-existing network/DNS discovery attempts blocked before send; no provider traffic. Audit counters show zero credential/production/external-write/nonfixture-execution access attempts. Focused/ext4 had zero network attempts. Counters and minimized logs retained.

stat -f uses ext2/ext3 magic wording; findmnt proves actual ext4 for ext4 runs, tmpfs for final full. Golden historical12/20 with eight known failures remains unchanged, not rerun/fixed. No coverage/live-performance/production-root/model-behavior certification claimed.
