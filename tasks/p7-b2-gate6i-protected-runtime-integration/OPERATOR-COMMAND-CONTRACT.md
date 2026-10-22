# Operator command client

OperatorCommandClient submits only an externally signed body. It contains no signing API. Operator endpoint accepts only `SIGNED` with `body` and 128-hex-character Ed25519 signature. Application service endpoint rejects SIGNED. Cryptographic verification is independent of kernel peer checks.

Reuse the existing exact signed body fields: verb, nonce, expires, bindings, checkpoint, payload. Nonce is 32 lowercase hex; expiry is strictly future and at most 60 seconds ahead; checkpoint is 64 hex. Bindings retain source, config, release, pid, invocation, epoch, boot, start, challenge. Approved identity and exact canonical bytes must match. No keys or runtime tokens grant operator status by themselves.

| Signed verb | Protected effect |
|---|---|
| RETIRE_AND_RESERVE_SUCCESSOR | Re-read exact terminal zero-use predecessor proof before/after signature verification. Atomically reserve one exact successor and nonce. Payload retains source/config/controller/live-state/archive identities and explicit unattributed-stop exception. |
| OPEN_HOLD | Approve opening only after current clean protected checkpoint; local runtime must separately CLAIM before opening. |
| AUTHORIZE_ONE | Approve one exact transport/session/request commitment after checkpoint. Does not itself accept an attempt. Outstanding approvals cannot be replaced or auto-expired into another permit. |
| TERMINAL_STOP | Approve terminal closure even during pending/unknown work. Does not settle providers or reopen anything. |

Every signed command nonce, claim and consumed permit survives restart. A claim committed without its local effect is an incomplete transaction requiring review, never a replay opportunity. Same-host root rollback remains outside the guarantee. Valid signatures prove key possession, not physical human presence; a separately qualified human signer/broker and approved process lifetime are required.

No production command has been signed or submitted. All signatures in tests are disposable. The original V2 OPERATOR_STOP and CLOSED_COMPLETE epoch remain untouched; operator-reported maintenance is not retirement authority.
