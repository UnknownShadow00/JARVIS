# Record to durable local observation evidence

Input: the exact immutable ShadowObservationRecordV1, with all 18 required fields and explicit nullable values from D03. Validate its versioned type and its frozen inert-record shape; never recalculate route, binding, comparison, permission, obligation or operational response. It grants no authority even when genuine.

A trusted JARVIS caller establishes source provenance and associates the record to its upstream submission/window. UUID shape or dataclass type alone does not authenticate origin. Reject arbitrary mappings, extra fields, mutable/service-bearing objects, fabricated authority and source objects. Persist only the explicit V1 allowlist; do not blindly serialize dataclasses or traverse request/P2/transport objects.

Output: a sink receipt; accepted means the complete entry is durably committed under the approved future local backend contract. A queued object/task/buffer never qualifies. Failed or uncertain persistence produces an explicit nonaccepted receipt. Sink failures must be contained by the future shadow caller before reaching legacy processing.

D04 authorizes this future semantic persistence boundary, not a live writer today. No registry, dispatcher, executor, provider, server, P2 store, audit logger, service locator or client-selected path is input.
