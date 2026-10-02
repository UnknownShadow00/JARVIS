# RESULT REPLAY — specified, not implemented

Normative: 13B11P-R1 `RESULT_REPLAY.md`. Unblocked and ready; mode C needs no confirmation
import, because its fields 16 and 17 (`ToolInvocation`, `TrustedToolResult`) live in
`types.py`. No code exists.

Settled points carried forward for the implementation:

- Exact type identity `type(x) is TrustedToolResult` and `type(x) is ToolInvocation`. A
  dict, namespace, `ModelDraft`, `ToolProposal`, subclass or look-alike is refused by type,
  not coerced. No `from_dict` and no provider-payload path.
- **Authenticity limit preserved exactly as frozen.** F-P7R1-01 stays open. The
  implementation must not attempt to close it with secret markers, hidden signatures, new
  provenance fields, stack inspection or caller introspection. What it enforces is type
  identity, C-01…C-08 linkage, and agreement between the replayed settled authority fields
  and what the frozen engines decide for this turn.
- `confirmation_claimed` is derived as
  `result.executed is True and invocation.permission_outcome is REQUIRE_CONFIRMATION`.
  **Never** from `invocation.confirmation_id is not None` — dispatcher gate 5 returns
  `CONFIRMATION_REQUIRED` with that id present and nothing claimed. The two frozen P6
  contradiction checks permit no other mapping.
- Per-status disposition, all with zero executor calls: `SUCCESS` -> `REPORT_TOOL_SUCCESS`
  with values only from `result.facts`; `ERROR` -> `REPORT_TOOL_ERROR` /
  `trusted_tool_error`; `TIMEOUT` -> `REPORT_TOOL_ERROR` / `trusted_tool_timeout`, outcome
  unknown, no re-dispatch, confirmation lifecycle untouched; `CONFIRMATION_REQUIRED` ->
  `executed=False` preserved and `P6-01a` `REQUEST_CONFIRMATION`, never converted into a
  tool failure; `BLOCKED` -> `executed=False` preserved and
  `REPORT_CAPABILITY_UNAVAILABLE` / `dispatch_blocked` where that existing rule wins.
- **F-P7R1-02 preserved.** Replay of a non-dispatchable-action refusal stays outside v1
  (guard C-00a). Replay behaviour is not widened in this task, and the planned C-00a check
  uses `obligations.NON_ACTION_OUTCOMES`, which is the identical three-member set, so no
  dispatcher symbol is referenced.
