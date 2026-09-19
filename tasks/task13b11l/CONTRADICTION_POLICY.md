# Contradiction Policy — Task 13B11L

**Design, not frozen.** Task §30 and §61 require frozen behaviour for input combinations that
cannot honestly coexist, and forbid "whichever field appears last".

## 1. The rule

An impossible combination is a **caller defect**, not a policy question. The engine raises
`ObligationDecisionError` rather than returning a decision. This follows the precedent set twice
already in this package: `permissions.py` — *"Passing one as authority is an API misuse, not a
permission question, so it raises rather than denying"* — and `dispatch.py`'s split between
`DispatchError` (type/shape) and a returned refusal (authority).

Raising is the fail-closed direction here, because there is no safe obligation to return: every
member of the enum asserts *something*, and the caller has already told the engine two
incompatible things about the world.

## 2. The corpus

| Combination | Why impossible | Behaviour |
|---|---|---|
| `PermissionOutcome.DENY` + a `TrustedToolResult` with `executed=True` | P5 cannot produce one: `DENY` refuses at gate 4 with `executed=False` | raise |
| `REQUIRE_CONFIRMATION` + executed result with no claimed approval | P5's gate 6 is the only route to execution | raise |
| `Lane.CONVERSATIONAL` + a trusted operational result | `LaneReason.TOOL_RESULT` forces `OPERATIONAL`; a caller asserting both has a broken lane call | raise |
| `AMBIGUOUS_ACTION` / `target_resolved=False` + executed result | §17.1 forbids dispatching without a resolved target | raise |
| `MULTI_ACTION_UNSUPPORTED` + executed result | §8.1: dispatch nothing | raise |
| `PrimaryAction.UNKNOWN_ACTION` + executed result | §13.1/§13.2: no nearest-tool substitution | raise |
| result whose `status` is `SUCCESS` but `executed=False` | `TrustedToolResult` invariants; only refusals carry `executed=False` | raise |
| wrong type anywhere (a mapping as a result, a bare string as a class) | shape, not policy | raise |

## 3. What is *not* a contradiction

These are ordinary states and must be decided, not refused:

* `REQUIRE_CONFIRMATION` with **no** result — rank 1, the normal confirmation turn;
* `DENY` with no result — the denial obligation. `PermissionOutcome.DENY` maps to
  `REPORT_CAPABILITY_UNAVAILABLE` at rank 6 rather than to a member of its own: the frozen
  eleven contain no `REPORT_PERMISSION_DENIED`, and inventing one would extend the contract.
  **This mapping is a genuine open question for the unblocking task**, because §19 of the task
  asks not to collapse denial, confirmation-required, unsupported capability and ambiguity into
  one category if the contract distinguishes them — and the contract's obligation set does not
  distinguish denial at all. It is recorded here rather than decided;
* `TIMEOUT` — rank 2 (`REPORT_TOOL_ERROR`) is the honest family, because §18 says the side
  effect may or may not have happened and rank 3 would claim it did. The builder, not the
  engine, is where "outcome unknown" is worded. Also open, and also recorded rather than decided;
* a conversational turn with no operational state — no obligation, `MODEL_RAW`.

## 4. Never

No contradiction resolves toward the model-friendly answer, and no malformed operational state
silently degrades to the conversational lane — that would be the §4.2 relabelling the contract
forbids, dressed as error handling.
