# Service authority client — protocol version 1

One request per connection: unsigned 4-byte network-order length followed by strict UTF-8 JSON, maximum 65,536 bytes. Exact envelope: `version`, `operation`, `arguments`. Version must be integer 1 (not boolean); duplicate keys, nonfinite values, extra fields and ancillary descriptors refuse. Whole read/write is bounded (configured at most 5 seconds), with at most eight accepted workers and no retries. Error reply is a fixed nonsecret refusal. A failed/missing reply is uncertain, not a refund.

| Operation | Exact arguments | Effect |
|---|---|---|
| READ | empty | Read protected public state; no secrets/signing capability |
| CHECK | expected {seq,seal}, allow_terminal boolean | Compare fixed controller state to protected history |
| CLAIM | expected, nonce | Burn delivery of an already signed operator command before local effects |
| CONSUME | expected, permit | Burn one authorized ordinal, never refund |
| BIND | expected | Read exact actual D09 ID from pinned controller path and associate it once |
| SEND | expected, ordinal, role, request_digest | Record possible-send for exact approved resource and actual D09 substep |
| SETTLE | expected | Consult fixed independent terminal reader; no terminal proof on wire |
| CHECKPOINT | expected, bundle | Bundle is exactly 32 lowercase hexadecimal characters, not a path; consult fixed snapshot root |
| TERMINATE | empty | Preserve local terminal evidence; incomplete/unknown never becomes complete |

ServiceAuthorityClient exposes read/check/accept/send/settle/checkpoint/terminal methods and has no journal, protected path, protected DB or private key. The derived backup projection is not a second authority. Calls are synchronous and bounded; runtime serializes one attempt. Conflicting concurrent calls may refuse on stale sequence, safely burning already committed operations.

Unix transport independently validates kernel SO_PEERCRED against pinned UID/PID and Linux process start/boot identity, before and after frame receipt. The client also authenticates the helper process and protected socket inode. PID/UID JSON claims have no meaning. Fixed helper-side readers receive no executable wire callbacks, SQL, arbitrary paths or imports. The dependency-injected Python readers are installer/test construction only.

Bearer REST/WS authentication grants none of these administrative powers. A compromised service can request fail-stop or cause denial of service; it cannot grant a permit, sign a command, refund acceptance or resolve remote uncertainty. Enforcing all possible network access by a compromised UID also requires the separately reviewed production egress/service policy; this candidate does not install that policy.

ReleaseIdentityReader takes an installer-protected inventory and config path, not service-supplied names. Its source binding hashes canonical inventory JSON; text-manifest/archive hashes are separately recorded and must reconcile before future signing. The full-release canonical map is supplied as review evidence, not active configuration.
