# One conversational acceptance; distinct provider operations

Acceptance is an immutable global UUID/ordinal/transport/session/permit record, LIVE and measurement-ineligible. Permit consumption and acceptance commit together before router, responder or Granite work. A failure consumes capacity permanently. REST1,REST2,WS3,WS4 is the candidate's explicit sequence; no client chooses the ordinal or grants a permit.

Each named substep has its own UUID, attempt foreign key, endpoint/model/profile, exact serialized-request digest and durable POSSIBLE_SEND marker/lease before the provider capability is invoked. A correlated injected ProviderResult with known_terminal=True records KNOWN_TERMINAL and KNOWN_TRANSMITTED. Timeout, stop, association mismatch or crash after possible-send preserves uncertainty; it does not infer remote completion. A pre-call marker can overstate possible transmission but never claim a send definitely occurred. Production transport validation of these claims is not implemented.

A successful L1 attempt contains router+legacy responder+Granite (three operations); L2 contains responder+Granite (two). Four successful attempts therefore mean12 or8 provider operations, respectively, while accepted count remains4. Receipt/submission counts are not proxies for all provider traffic. Tests assert peak concurrent fake generation1 and one Granite receipt per settled attempt.

| Failure | Durable/result treatment |
|---|---|
| Router/responder possible-send timeout | preserve lease remote unknown, no next substep/permit |
| Legacy fails before delivery | no fabricated client reply; accepted capacity retained |
| Legacy delivered then Granite fails/tool proposal | preserve delivery fact/history; no Granite response fallback; terminal incomplete |
| Known provider terminal but parse/tool rejection | preserve known terminal ownership; terminal pilot abort, no false remote-unknown invention |
| Delivered legacy but D04 append/join missing | local delivery retained; no settled success/checkpoint eligibility |
| Receipt appended before DB join crash | orphan evidence retained; READY checkpoint refused; FORENSIC_INCOMPLETE possible |
| Client disconnect/interrupted ASGI send | delivery INTERRUPTED_UNKNOWN; assistant text not added; stop later permits |
| Terminal commit then process crash | durable step fact retained; restart closed; no retry/replay |
| Backup failure after settlement | accepted/receipt truth retained; terminal incomplete; no next permit |
| Authentication/continuation mismatch | terminal refusal, no new provider work |

Only local ASGI-send completion is observable to the adapter. It is not proof the browser/human rendered the reply. Raw replies/inputs/credentials are absent from durable candidate receipts/ledger. Session history is in-memory bounded user/delivered-legacy text. Unsent/Granite text never enters delivered legacy history. The canonical observer is required; fabricated dummy observations are confined to tests.
