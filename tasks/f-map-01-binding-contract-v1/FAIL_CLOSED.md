# Fail-closed outcomes

| Condition | Producer outcome | Existing downstream owner |
|---|---|---|
| Invalid input type/version, wrong session/turn association, bad metadata digest/revision | Reject projection creation; ingress records the failure outside the binder | No P7 call with fabricated fields |
| Missing or ambiguous route/target, `NONE`, unsupported action | No expected binding or permission projection | P3/P6 unsupported or conversational path |
| Missing capability pair, registry key, target schema or handler metadata | No executable expected binding | Existing unsupported/capability-unavailable semantics |
| Bad app key, malformed/credentialed URL, missing/extra argument, failed canonicalization | No expected binding | Existing S06 `projection_missing` for actionable comparison where applicable |
| Missing JARVIS approval mode or P4 row | Reject projection; no client-supplied replacement | Ingress fail closed |
| Model proposes zero, multiple, different or unadvertised tool/args | Projection never changes | Existing P7 S06 proposal guards |
| Fake client/model permission or confirmation | Ignore as non-envelope authority data; reject if presented as typed owner input | P4/P5 remain authoritative |

This contract adds no `PipelineStopReason`. Ingress must distinguish a producer rejection from a successfully produced empty binding, and cannot treat either as permission to execute. Unknown fields fail validation rather than being silently dropped to obtain a match.
