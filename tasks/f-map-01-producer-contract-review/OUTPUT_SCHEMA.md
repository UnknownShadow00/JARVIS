# Required projection outputs — incomplete live schema

No new authority-bearing type is introduced. The existing P7 handoff fields are the output contract: `RouterContext`, `CanonicalizationResult | None` and `PermissionRequest | None`, plus consistency of the separately JARVIS-built `AdapterRequest.tool_schemas`. All are immutable snapshots or existing frozen dataclasses. The complete **field names and types** are frozen below; **live derivation of tool/arguments is blocked**.

Trust level for every row is **JARVIS-owned comparison/query data only**: valid type and origin let P7 compare and let P4 decide, but never prove permission, confirmation or execution. No row may be copied from raw client/provider/model data as an authority assertion.

| Output field | Type / owner | Source and P7 consumer | Failure |
|---|---|---|---|
| `router_context.supported_actions` | `frozenset[PrimaryAction]`; JARVIS capability source | approved available-action intersection; S03/S06; not `DEFAULT_ROUTER_CONTEXT` as a live grant | absent/untrusted inventory: no live executable projection |
| `expected.tool_name` | `str`; binding schema (unfrozen) | closed capability→tool namespace; S06 exact tool/advertisement | unresolved: no expected result; executable path stops projection_missing |
| `expected.raw_arguments` | immutable mapping; binding schema (unfrozen) | deterministic request/route→required tool args incl. target field; S06 P3 linkage | missing/ambiguous: no expected result |
| `expected.canonical_arguments` | immutable mapping; P3 | `canonicalize(expected.tool_name, expected.raw_arguments)`; S06 whole map | P3 error: canonicalization_failed; do not repair |
| `expected.version` / `applied_rules` | `str` / tuple; P3 | current `CANONICALIZATION_VERSION` and actual P3 rule record; S06 | version/lineage conflict: projection_invalid |
| `permission_projection.capability` | `str`; P4 declared pair + approved availability | S06 P4 action/capability and `row_for` checks; S07 `decide` | unsupported/unregistered: capability_unavailable |
| `permission_projection.primary_action` | `PrimaryAction`; P3 route | exact route action; S06 | mismatch: projection_invalid |
| `permission_projection.target` / `target_resolved` | `str|None` / `bool`; P3 route | exact routed target/resolution; S06 | unresolved target follows P6 early terminal; mismatch projection_invalid |
| `permission_projection.canonical_target` | `str|None`; JARVIS binding schema (unfrozen) | P4 policy target representation; no model extraction | no defined correspondence: no live projection |
| `permission_projection.raw_arguments` / `canonical_arguments` | immutable mappings; P3/JARVIS | exact expected raw/canonical maps; S06, S07 | mismatch: projection_invalid |
| `permission_projection.approval_mode` | `ApprovalMode`; P4/operator config | existing tightening context; S07 | invalid: permission_failed |
| `permission_projection.satisfied_constraints` | `frozenset[Constraint]`; existing constraint owners | only independently checked facts; S07 | unproved claim omitted; no client/model grant |
| `permission_projection.overwrite` | `bool|None`; existing deterministic source | only if capability rule needs it; S07 | unresolved: existing P4 deny/fail behavior |

`PermissionDecision` is **not** a producer output: P7 calls `permissions.decide()` at S07. `RouteResult` and `Classification` are not `RecordedTurn` fields: P7 recomputes them at S02/S03. The output has no callable, store, registry handle, dispatcher, executor, provider client, confirmation machine or shortcut authority boolean. It grants no execution authority.
