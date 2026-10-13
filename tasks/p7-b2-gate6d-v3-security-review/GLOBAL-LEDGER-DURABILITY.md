# Global ledger and filesystem durability

Logical cap/permit behavior is isolated-tested; protected lineage and actual filesystem durability are not release-qualified. Store uses SQLite schema5, FULL synchronous, DELETE journal, BEGIN IMMEDIATE, a lifetime flock writer and shared reentrant lock. Permit consumption and accepted LIVE/ineligible row commit together. Ordinals1–4 and REST/REST/WS/WS remain permanent across failures. Gate6D adds logical validation of contiguous ordinals, transport, spent-permit/acceptance association, step states and corresponding leases.

| Adversarial case | Observed result / limit |
|---|---|
| Same-parent duplicate successor; concurrent creators | O_EXCL reservation admits only one; competing name refused |
| Crash reservation/before initializer commit/after initializer commit | Reservation remains; replacement successor refused. No automated resume/repair |
| Partial reservation write | Partial artifact retained; second creation refused |
| Missing/corrupt actual predecessor archive | **UNIMPLEMENTED verifier**: current caller-supplied nonempty archive string is trusted. This is a high release blocker, not a passed archive test |
| Nonzero/unknown/incomplete/abort predecessor fields | Refused; now boolean/float count cannot masquerade as integer0 |
| Separate parent/root masking predecessor | **Not prevented globally** without protected root authority. Same-UID directories are not global lineage enforcement |
| Crash before acceptance commit | Rollback preserves zero accepted/spent |
| Crash after acceptance commit before send/ack | Accepted1/spent1 remains, even when no provider was invoked |
| Process exit at possible-send | Accepted1 and unresolved ACTIVE lease persist; no inferred completion |
| Process exit after known-terminal association | Accepted1 persists; remaining incomplete attempt prevents readiness |
| Duplicate REST/WS, cross-transport replay, invalid ordinal | Refused, no refund/additional provider call; matching authentic continuation alone grants nothing |
| Fifth attempt/restart existing accepted set | Cap enforced; restart is recovery hold, not automatic opening; old sessions/permits do not authorize Runtime.request |
| Terminal abort/stop then reopen | Refused. Signed stop audit and terminal state are now one transaction |
| Older backup | verify_checkpoint rejects when supplied newer event high-water; no restore writer exists. Independent monotonic high-water authority across arbitrary DB replacement is missing |

Five new child processes per run exited through os._exit at distinct acceptance/provider boundaries. Initial focused/full tests used tmpfs; all149 focused tests then passed again on Core root ext4 in exclusive disposable `/home/jarvis/gate6d-fs-test-vRWRQNW1`, outside production namespaces. They were not mocked exceptions. This proves process-exit behavior on both tmpfs and the actual Core ext4 filesystem using isolated files; it does not prove abrupt power-loss/disk-controller behavior. Other fixture fault tests inject before/after commit, short writes and backup interruptions. Canonical full suite additionally used its two pidfd-verified disposable writer crashes.

Backup protocol: private UUID directory and parent fsync; SQLite backup; file fsync; exclusively created receipt/lineage files; manifest written last and fsynced; directory fsync; full verifier; only then checkpoint association in live ledger. Publication is manifest-last, not a cross-file atomic rename/transaction. Interrupted directories remain distinguishable and unready. No separate candidate checksum sidecar exists: component digests are in the manifest; the external evidence SHA256SUMS is separately sealed. Partial manifest and missing manifest refuse. Final evidence creation is not a runtime backup writer.

Gate6D moved quiescence validation inside the writer lock, rejects static symlink ancestors/source receipt symlinks, and rejects missing joined receipts in forensic backups even when checksums are rewritten. Unjoined trailing/partial receipt bytes may be retained under FORENSIC_INCOMPLETE, never READY. Source and receipt snapshots share the writer lock; unknown ownership and unsettled attempts block READY. Arbitrary same-UID mutation/rename races are outside current protected-path enforcement.

No restore API writes over occupied state; existing/partial controller initialization refuses and original reservations persist. That is refusal, not a qualified restoration protocol. A caller can still replace older files outside these APIs if it owns them. Root-protected high-water/reservation/archive verification must prevent this before deployment.

Actual target filesystem qualification must cover power interruption, disk-full, fsync/rename/parent durability, journal recovery, simultaneous process writers/readers, disk stalls and backup association failure after manifest publication. SQLite assertions and mocked fsync cannot guarantee hardware durability. Synchronous filesystem calls can exceed30s or wedge the event loop; the current drain method does not provide a supervisor-enforced wall-clock guarantee or automatically complete a final terminal checkpoint. Keep both as explicit release blockers.
