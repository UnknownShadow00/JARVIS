# Independent source review scope

This is a new adversarial examination of the verified Gate6I implementation. It is not an external certification or a claim of separate human review. The review traced the actual configured protected graph and inspected the future privileged runner.

| Boundary | Source and trace | Finding / qualification |
|---|---|---|
| REST and WS | ingress.Ingress → monitored Runtime.request → ServiceAuthorityClient.before_accept → AuthorityService.CONSUME → Store.accept → BIND | Bearer/continuation checks precede admission. Bearer exposes no signed command route. Four global accepts remain nonrefundable. |
| Operator | OperatorCommandClient → real Unix listener → kernel identity → AuthorityService.SIGNED → Authority.check/Ed25519 → RuntimeJournal.signed | Signature and OS identity separate; signed approval does not itself apply local OPEN. |
| Administrative application | Runtime.apply_protected_command → remote approved command → CLAIM → local control/open/arm | Local direct control also consumes the same protected approval; no service SIGN verb. |
| Provider | Runtime._generate → local possible-send → protected SEND → OwnedProvider/D06 → NativeTransport → new protected DISPATCH → fake native HTTP | Confirmed direct dispatch bypass repaired at the native seam. One-use dispatch is another event for the same accepted substep, not another attempt counter. |
| Settlement | correlated native result → local terminal record → protected SETTLE with installer-side witness | No witness means refusal; cancellation/socket closure cannot create terminal evidence. Real independent witness remains absent. |
| Evidence/checkpoint | D04 EvidenceBridge → D09 receipt join → CheckpointWriter → protected fixed ControllerReader | Captured bounded file bytes replace privileged repeated/path-based reads; schemas and bounded SQLite work checked. |
| Stop/restart | close local admissions → drain/account → protected TERMINATE → reconcile actual terminal status | Found and fixed false local COMPLETE after unbound protected acceptance. Restart cannot rebind/reopen. |
| Runner privilege boundary | root parent ↔ distinct role processes | Fork descriptor inheritance and pickle reception replaced by spawn and bounded fixed-type JSON. |

Secondary constructors and old HighWater/build_isolated_app paths remain explicit OFFLINE_EVALUATION_ONLY baseline fixtures. They are not production startup entrypoints. No module import installs a listener, starts inference or imports operational dispatch. contracts.build_production_runtime always refuses. The protected factory binds its native transport to the same authority client as admission/checkpoints. The new regression directly invokes both OwnedProvider and NativeTransport on that graph and requires refusal without SEND.

Limits: arbitrary code execution inside the service process could instantiate its own HTTP client or alter Python objects. This helper is not an egress proxy and Python object identity is not an OS capability boundary. A future production design must independently constrain provider reachability and writable imports/interpreter/dependencies. No claim is made that these isolated software checks contain arbitrary service-code execution. Root/host rollback, production signer custody/presence and independent completion witness remain outside the qualification obtained here. No demonstrated bypass remains in the tested configured graph; this does not establish absence of all defects.
