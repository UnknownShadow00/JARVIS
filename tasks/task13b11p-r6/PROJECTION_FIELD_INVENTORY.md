# Projection field inventory — V2

Exactly 16 fields. Every field is trusted P4-owned control-plane data, projected by the confirmation-owning boundary outside P7. Trusted means an owner obligation, not authenticated origin or authority to execute. No field is model-derived. Identifiers reuse correlation.py NewTypes (runtime exact str); PrimaryAction and PermissionClass reuse types.py. No lifecycle type is imported.

| Exact name | Exact type | Source | Owning subsystem | Consuming guards | Required because | Trusted? | Absence valid? |
|---|---|---|---|---|---|---|---|
| `confirmation_id` | `ConfirmationId` | `record.binding.confirmation_id` | P4 boundary | B-04, B-06 | optional correlation child association; single identity replaces record/binding identity alias | Yes, owner projection | No |
| `session_id` | `SessionId` | `record.binding.session_id` | P4 boundary | B-01, B-06 | owner and bound session are the same record property | Yes, owner projection | No |
| `state` | `Literal["PENDING", "EXECUTING", "SUCCEEDED", "FAILED", "DENIED", "EXPIRED", "CANCELLED"]` | `record.state.value` | P4 boundary | B-02, B-05 | pending eligibility and execution-started membership; no lifecycle enum imported | Yes, owner projection | No |
| `expires_at` | `datetime (timezone-aware)` | `record.expires_at` | P4 boundary | B-03 | exact half-open freshness comparison at admitted evaluated_at | Yes, owner projection | No |
| `audit_session_id` | `SessionId` | `record.audit_ref.session_id` | P4 boundary | B-04 | audit association with bound and current session | Yes, owner projection | No |
| `audit_turn_id` | `TurnId` | `record.audit_ref.turn_id` | P4 boundary | B-04 | preserves the original creation-turn reference, including across continuation turns | Yes, owner projection | No |
| `invocation_id` | `InvocationId \| None` | `record.invocation_id` | P4 boundary | B-05 | explicit existing claim linkage must be absent | Yes, owner projection | Yes: None means no linked invocation |
| `action_type` | `PrimaryAction` | `record.binding.action_type` | P4 boundary | B-06, B-07 | compare actual routed action and reject non-action outcomes | Yes, owner projection | No |
| `capability` | `str` | `record.binding.capability` | P4 boundary | B-06 | compare JARVIS permission query capability | Yes, owner projection | No |
| `tool_name` | `str` | `record.binding.tool_name` | P4 boundary | B-06 | compare authoritative expected tool | Yes, owner projection | No |
| `permission_class` | `PermissionClass` | `record.binding.permission_class` | P4 boundary | B-06 | compare actual S07 permission class | Yes, owner projection | No |
| `policy_version` | `str` | `record.binding.policy_version` | P4 boundary | B-06 | compare frozen P4 policy version | Yes, owner projection | No |
| `canonicalization_version` | `str` | `record.binding.canonicalization_version` | P4 boundary | B-06 | compare P3 version and expected.version | Yes, owner projection | No |
| `target` | `str \| None` | `record.binding.target` | P4 boundary | B-06 | compare actual route.target, including exact None | Yes, owner projection | Yes: only where actual route.target is None |
| `raw_arguments` | `Mapping[str, FrozenPlainValue]` | `record.binding.raw_arguments` | P4 boundary | B-06 | full exact raw binding equality, including extra keys | Yes, owner projection | No; empty mapping is a value |
| `canonical_arguments` | `Mapping[str, FrozenPlainValue]` | `record.binding.canonical_arguments` | P4 boundary | B-06 | full exact canonical binding equality | Yes, owner projection | No; empty mapping is a value |

`FrozenPlainValue = None | bool | int | float | str | bytes | tuple[FrozenPlainValue, ...] | frozenset[FrozenPlainValue] | Mapping[str, FrozenPlainValue]`. Containers are recursively immutable snapshots; mappings are fresh privately backed read-only proxies, never views onto a caller-retained mutable dict. Exact built-in scalar types only; no arbitrary instances, enum objects inside argument values, callable, model object, store or lifecycle object. Numeric comparisons preserve exact scalar type. This restriction makes the already-required plain immutable control-plane boundary explicit; no new authority is admitted.

Excluded after guard analysis: `user_id` (V1 expressly does not constrain it); `created_at`, `resolved_at`, `provenance_ref`, `state_machine_version` (no B-guard consumes them); second copies of binding confirmation/session identifiers (record properties alias binding values); `audit_confirmation_id` (record constructor already enforces equality and B-04 consumes only the optional current correlation child); `execution_started` (exactly state membership in EXECUTING/SUCCEEDED/FAILED); `pending`, `terminal`, `claimed`, `fresh` (redundant derived booleans); permission outcome (recomputed at S07); any confirmation-approved or ready boolean (no existing grant semantic). The full twelve-field P4 claim binding remains P4-owned; this sixteen-field observation does not replace that binding or participate in a claim.
