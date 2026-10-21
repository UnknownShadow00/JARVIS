# Antirollback threat model

Proposed trust root: host kernel/root installer, protected authority owner/storage, protected public-key/presence policy and fixed-path independent readers. Stronger root/host-loss guarantees add an independently controlled off-host witness. Application/agent UIDs are outside this root. Current production has none of the proposed provisioning.

| Attack/failure | Delivered isolated evidence/design response | Limit or remaining qualification |
|---|---|---|
| Controller rollback | Protected accepted reservation/seq rejects older snapshot | Runtime adapter and true OS separation absent |
| Provider ledger rollback within accepted ordinal | Protected pending SEND blocks progression until associated SETTLE | Real independent terminal reader absent |
| Backup rollback | Old accepted list/token refuses; no live authority restore API | Root/authority owner can replace anchor |
| Manifest substitution | Signed checkpoint/payload and protected fresh identity checks | Real fixed-path content reader/immutable provisioning absent |
| Source/config/dependency substitution | Root-owned release policy; each stale identity field refuses in fixtures | Reader must recompute protected data, not trust app assertions; lock/signature integration absent |
| Previous operator command replay | Canonical signature, bindings, expiry, unique durable nonce | Actual human-presence mechanism pending |
| Consumed permit reuse | Durable protected ordinal/session/commitment; cap4; no reset/refund | Direct credential/network abuse by hostile process needs separate confinement |
| Concurrent successors | Two real SQLite connections; exactly one root | Separate-UID filesystem boundary unqualified |
| Concurrent permits | Only one next ordinal commits; checkpoint invalidated | Service AF_UNIX adapter absent |
| Crash during nonce consumption | Real os._exit before/after commit for SUCCESSOR/ACCEPT | Not VM power loss/storage controller durability proof |
| Crash after durable acceptance/SEND/SETTLE | Reservations/uncertainty survive; no inferred ack/refund | Incomplete local associations stop progress |
| Old PID/invocation reuse | Nine signed fields plus fresh reader; stale fields refuse | Real pidfd/start/boot/invocation reader pending |
| Service UID edits protected root | Proposed DAC separation, nonwritable ancestry; kernel mount denials tested | No genuine distinct-UID DAC proof or production protected root |
| Symlink/hardlink/writable-parent attack | lstat, single link, no symlink ancestors, inode/mode/ancestor tests | Production ACL/mount/FD/supplementary-group qualification required |
| Replacement of all writable app files | Preserved authority seq/reservation/SEND detects rollback in fixtures | Only valid if service cannot replace authority/readers; no end-to-end claim |
| Replacement of all authority files with old valid copy | Owner/root negative control succeeds | Off-host nonrollback witness required for stronger assurance |
| Corrupt/missing/unavailable authority | Fixed refusal, no implicit recreation | Human recovery only |
| Unexpected shutdown | H-4 truthful generic stop; restart closed; no invented human attribution | Maintenance statement is not retirement authority |
| Resource unknown/external actor | Protected pending SEND plus D06/domain holds; never auto-release | Real actor exclusion/terminal/resource attestation absent |

A hostile service can destroy its own state, deny availability, withhold replies or burn approved capacity. Authority separation should prevent history erasure or a second linked successor. It does not prove model output correctness, provider honesty, GPU exclusivity, human receipt of a frame or arbitrary host integrity. No provider proxy was introduced. Service credential abuse requires separately enforced network/credential restrictions.

A locally signed checkpoint can be replayed with the whole local trust anchor. External replication after acknowledgement leaves a rollback window. Independently durable witness acceptance must precede acknowledgement if root/host rollback resistance is claimed.
