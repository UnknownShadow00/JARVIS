# Antirollback results and limits

| Attack | Isolated enforcement | Limit |
|---|---|---|
| Controller or accepted-attempt rollback | Exact protected accepted rows, D09 IDs, commitments, claimed commands and source bindings must match | Real write denial requires distinct-UID qualification |
| Local ledger/substep rollback | Protected SEND history must still join local attempt/kind/request; pending intent blocks progress | A possible-send is not evidence of inference |
| Older backup recovery | Bundle token, clean coordinated joins and protected high-water checked online; backup never restores authority | Offline checksum validation alone grants nothing |
| Replace every service-writable file | Separate protected journal retains acceptance, claims and possible-send; actual whole-directory fixture rollback refuses | Current filesystem owner is shared in tests |
| Source/config/manifest substitution | Installer-pinned file digests, owner/ancestor/link checks and process start/boot binding | Real installed inventory/supervision approval remains pending |
| Signed command/permit replay | Unique durable nonce, one-use CLAIM and CONSUME; max four derived accepted rows | No refund/rebind/recovery API |
| Concurrent successors/consumption | SQLite BEGIN IMMEDIATE plus unique sequence/nonces and exact expected token | SQLite/platform durable storage assumptions apply |
| Missing/corrupt root | mode=rw and strict schema/chain/inode checks; no automatic creation or restore | Availability loss requires human recovery design |
| Crash after commit before acknowledgment | Durable result remains burned; replay cannot be treated as a fresh operation | Process crashes tested; actual VM power cuts not run |
| Service PID/invocation reuse | Kernel UID/PID plus process start/boot pin; approved bindings checked on transactions | New process approval is deliberately unavailable automatically |
| Root/whole-host rollback | NOT DEFEATED | All on-host authority and apparent proofs can be rolled back together |

An on-host root-owned ledger can protect against ordinary service-UID modification only after actual OS separation is qualified. It cannot independently attest that a host administrator/hypervisor has not restored the whole host. A stronger guarantee needs a separately administered anchor and independently approved durable-before-ack/recovery design. No off-host/cloud export was implemented.

Journal uses standard Ed25519 verification and SQLite FULL/DELETE transactions. Hash chains detect inconsistency within the protected domain; hashes are not the OS boundary. [SQLite atomic commit documentation](https://www.sqlite.org/atomiccommit.html) describes the durability mechanism and storage assumptions; this task does not claim power-loss qualification.
