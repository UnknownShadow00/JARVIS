# Continuous improvement register

| Finding | Implemented isolated correction | Regression evidence |
|---|---|---|
| Companion not on runtime acceptance/provider path | Typed service/operator transport; mandatory protected graph; CONSUME/BIND/SEND/SETTLE/checkpoint hooks | Four-turn graph, REST/WS, crash/unknown/refusal tests |
| Approval previously burned attempt immediately | Separate signed APPROVE, one-use CLAIM and actual CONSUME; exact D09 association | Approval≠acceptance, concurrent consumption, no refunds |
| Local rollback could replay opening | Protected CLAIM before local control effect; exact claimed-control reconciliation | Opening rollback/replay regression |
| No accept-based service transport | Bounded real listener and two independently instantiated clients with kernel identity pins | Partial/malformed/FD/concurrency/replay tests |
| Worker registered before start could race shutdown | Register and start under same lock; refuse late worker after stop | Shutdown-during-partial-request regression |
| Privileged reader could follow service SQLite paths | Bounded O_NOFOLLOW file read and query-only in-memory SQLite snapshots, ownership/link/digest checks | Symlink/hardlink/oversize/digest/atime tests |
| File-read access time changes looked like tampering | Compare only identity/content-relevant stat fields, retaining mtime/ctime/size checks | Dedicated atime regression; intermediate failure retained |
| Service-controlled FIFO could block a privileged snapshot read | Nonblocking no-follow open, then regular-file/size/owner validation | FIFO regression in separately preserved release-r2 |
| Helper failure could leave apparent complete stop | Downgrade local terminal to CLOSED_INCOMPLETE | Missing-authority stop regression |
| Model proposal mismatch | Normal context8192 in isolated profiles and protected factory; frozen Granite unchanged | Four-turn request assertions and source qualification tests |
| Empty-memory fixture could be accepted as recommended graph | Require exact pinned source procedural snapshot | Empty-memory protected factory refusal |
| Synthetic records labeled LIVE | Candidate attempts/receipts/backup validation require OFFLINE_FIXTURE | Explicit origin test plus full baseline |
| New distinct-UID environment not authorized | Automated guarded future runner and exact human provisioning instructions | Syntax/nonroot refusal tested; privileged execution pending |

No architecture-wide redesign, historical event rewrite, production source edit, package installation, commit or push. Earlier candidates remain sealed. Test-authoring, snapshot-reader and disposable filesystem failures are recorded rather than hidden; final tests must pass after fixes.
