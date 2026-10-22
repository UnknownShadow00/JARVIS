# Possible-send and D06 accounting

Runtime order: fixed request serialization/bounds → D06 precheck → local D09 POSSIBLE_SEND → protected SEND acknowledgment → OwnedProvider/D06/domain acquisition and fake transport. A conflict before local begin remains a refusal; races or lost acknowledgment after intent remain conservative uncertainty. Protected role maps to an installer-provided exact contract digest, and the actual local endpoint/model/profile/request/attempt must match before SEND.

Allowed per-attempt order is optional legacy_router, exactly one legacy_trivial or legacy_normal, then granite. Repeat/conflicting roles refuse. The original four requests permit at most three classifier, four responder and four observer operations. There is no retry, fallback, streaming, auto load/unload or next-permit action.

A SEND record proves intent may have reached transport; it does not prove inference. SETTLE accepts only the helper's configured independently associated terminal witness. Tests supply fake responses/witnesses. Socket closure, client cancellation, local timeout, service restart and an untrusted clean flag never establish remote completion. Missing witness leaves protected pending state even if a local component claims terminal completion.

The existing OwnedProvider preserves D06 remote unknown after cancellation/uncertain send. D04 joins remain actual observation commits, never inferred from delivery or provider completion. A D04 append/join fault prevents the next checkpoint/permit; legacy delivery truth remains separate. Terminal closure retains pending intent and incomplete state.

No real endpoint/GPU topology or external actor exclusivity was verified. D06 only coordinates participants that honor its lease. Other clients, unloaders, alias writers, provider restarts and shared GPU actors require independent inventory/isolation and an approved exclusive qualification window. No live model was contacted or changed.
