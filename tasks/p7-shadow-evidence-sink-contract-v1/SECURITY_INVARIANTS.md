# Threat review and defenses

| Threat | Frozen defense / remaining proof |
|---|---|
| Loss hidden as success | Success only after commit; explicit failure/uncertainty; affected coverage incomplete; independent upstream reconciliation required |
| Duplicates inflate metrics | Sequence unique only as storage order; no turn-as-attempt key; unresolved duplicates cannot form valid samples; D02/D07 policy deferred |
| Trace/turn confusion | Preserve exact authoritative correlation plus distinct observational trace; no trace fallback/new IDs |
| Cross-session mixing | Serialize existing same-turn context exactly; trusted caller association and validation; reconcile by session/turn, never shared global authority |
| Tampered stored record | Exact version/shape/hash validation and sealed evaluated set; SHA256 not writer authentication |
| Partial/corrupt input | Fail closed; preserve invalid material; no repair/hidden truncation or complete-window claim |
| Raw secret enrichment | 18-field allowlist plus six-field sink envelope; no arbitrary object traversal/raw errors or user/model text |
| Audit/provenance contamination | Dedicated local evidence only; no writers/fallback/promotion |
| Clock grants authority | Reuse aware UTC helper only for acceptance chronology; no IDs/latency/policy/threshold dependence |
| Host local-time ambiguity | +00:00 ISO value required; reject naive/non-UTC values; sequence controls order |
| Storage failure breaks legacy | Shadow receipt/error isolation and future D07 consumer tests; no mode/policy/model/tool fallback |
| Network exfiltration | Local backend only, confined private root; no sink network or inherited export authority; verify backup interaction before implementation |
| Retention destroys evidence | No automatic TTL/prune/destructive rotation; all three P7 retention gates and explicit cleanup authorization |
| Path/symlink escape | Core-controlled namespace under canonical data root; no client paths; verify confinement before any future write |
| Crash/ack ambiguity | Recover durable order/set, classify unresolved coverage; upstream recoverable intent/accounting before complete claim |
| Storage/CPU denial of service | No numerical resource/admission choice here; full/quota failure is explicit; D07 isolation/bounds still required |

Type/hash validation cannot prove a hostile in-process actor's origin, execution absence or a complete measurement interval. Current work is a documentation review, not a security-tested running sink.
