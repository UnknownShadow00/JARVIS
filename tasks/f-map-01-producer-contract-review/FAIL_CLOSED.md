# Fail-closed disposition

The producer does not create a new `PipelineStopReason`. It either supplies a coherent existing P7 input or withholds the executable projection. P7's existing stage vocabulary applies only when a well-formed `RecordedTurn` is admitted; invalid correlation can raise at S01 and must be rejected by the future ingress adapter before calling it.

| Condition | Current safe disposition |
|---|---|
| Missing/untrusted capability inventory or mapping schema | do not claim capability; withhold `expected`/`permission_projection`; if an actionable proposal reaches P7, S06 `projection_missing`; no live dispatch |
| Unsupported/unregistered action/capability | explicit unavailable `RouterContext`; P7 early nonaction/P6 path or S06 `capability_unavailable` for executable candidate |
| Ambiguous/unresolved target | keep router's `target_resolved=False`; P7 early P6 terminal; no invented target |
| Missing/ambiguous target argument field or required argument | no authoritative expected binding; S06 `projection_missing` for actionable proposal; no model repair |
| Canonicalizer error | P7 existing S06 `canonicalization_failed` if reached; producer cannot substitute a guessed map |
| Expected/query type, action, target, raw/canonical map or version disagreement | P7 S06 `projection_invalid` |
| Model proposes wrong tool, args, ID or cardinality | P7 existing S06 `proposal_tool_mismatch`, `proposal_arguments_mismatch`, `proposal_association_mismatch`, or cardinality stop |
| Invalid P4 query or policy context | S07 `permission_failed`; no fallback permission |
| Wrong/missing JARVIS correlation or snapshot session | reject at ingress / existing S01 input validation; no replacement with client/provider ID |
| Confirmation/replay state inconsistent | existing S01/S08/S09 guards; no claim, retry or synthetic result |

For the currently missing live schema, a producer must not build a partially authoritative action binding and then represent it as executable. Stopped turns remain non-renderable until F-FALLBACK-01 is settled for live use. This table describes containment, not a complete live producer algorithm.
