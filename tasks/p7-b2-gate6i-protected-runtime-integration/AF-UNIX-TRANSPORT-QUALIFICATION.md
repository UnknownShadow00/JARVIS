# Real AF_UNIX transport qualification

Gate6I adds pathname bind/listen/accept serving and independently instantiated service/operator clients. These are genuine Linux sockets, not socketpairs. Actual kernel peer credentials are checked. Current runs use one kernel UID; they are NOT cross-UID qualification.

Coverage includes valid/partial frames, whole-operation trickle deadlines, oversized frames, malformed JSON, duplicate keys, boolean/unsupported versions, unknown verbs, forged UID arguments, SCM_RIGHTS descriptor rejection/closure, concurrent clients, nonreading peers, broken pipes, stale process pins, socket replacement, wrong peer UID, signed replay, shutdown during partial request, command persistence and reopened authority state. Worker-start/shutdown race was found and fixed by registering and starting workers under one lock. Replies have a bounded socket send buffer and deadline.

Proposed runtime paths replace the ambiguous Gate6H ownership arrangement:

| Path | Owner/group/mode | Reason |
|---|---|---|
| /run/g6i | root:root 0755 | Traversal only for clients |
| /run/g6i/operator | root:approved-operator-group 0750 | Root helper can bind/restart; operator can traverse but cannot replace socket |
| /run/g6i/operator/control.sock | root:approved-operator-group 0660 | Operator may connect; service/agent excluded |
| /run/g6i/service | root:approved-service-group 0750 | Separate service endpoint, no directory mutation |
| /run/g6i/service/control.sock | root:approved-service-group 0660 | Service may connect; agent excluded |
| Protected journal root | root:root 0700; DB0600 | Service cannot read/write/replace authority |

No client gets group write to a directory. A root helper avoids giving an unrelated authority UID broad read access to service-private 0700/0600 state. Its implementation has fixed readers and no shell/admin/provider proxy verbs. Stronger dedicated nonroot authority deployment would need a separately qualified snapshot handoff; it is not silently assumed workable. The helper receives only a public verifier key. Root can read any same-host key; separation is from service UID, not from root.

Listener never unlinks an existing socket at startup. Graceful close unlinks only its own inode; stale crash sockets require human-supervised cleanup. New operator/service/helper PID or start identity requires reviewed provisioning/rebinding; no automatic restart authorization. Socket paths and every ancestor are checked for symlinks and writable ownership.

Implementation references: Linux documents pathname permissions and SO_PEERCRED in [unix(7)](https://man7.org/linux/man-pages/man7/unix.7.html). Descriptor reception/flags use [Python socket APIs](https://docs.python.org/3/library/socket.html). These API references do not establish the unrun OS qualification.
