# Test Plan — Task 13B11J

317 new tests in three files. Each derives from a document frozen before the module existed.

| File | Tests | Derives from |
|---|---|---|
| `tests/execution/confirmation_test.py` | 119 | `CONFIRMATION_MODEL.md`, `BINDING_CONTRACT.md`, `STORE_API.md`, `EXPIRY_AND_FRESHNESS.md`, `AUDIT_COMPATIBILITY.md` |
| `tests/execution/confirmation_transitions_test.py` | 71 | `transition-table.json` — read as data, SHA-256 asserted |
| `tests/execution/confirmation_non_activation_test.py` | 127 | the phase boundary: passive, unwired, legacy untouched |

## 1. Identifier (7 tests)

Well formed by `correlation.is_well_formed_id`, 32 hex characters, 200 minted ids all distinct,
JSON-serializable, opaque — no target, tool, session, capability or prompt text recoverable — and a
supplied id must be well formed or creation is refused.

## 2. Creation (10 tests)

Initial state is exactly `PENDING`, `execution_started` is `False`, `resolved_at` and
`invocation_id` are `None`. The binding has exactly the twelve frozen fields. Permission class and
policy version reach the binding unchanged. Raw and canonical arguments are both retained
(INV-006). The audit ref agrees with the record. Binding and state are frozen; a caller's mapping
is copied, not aliased; nested sequences are frozen to tuples and cannot be written through a
returned record.

## 3. Creation guards (13 tests)

Refused: a decision that is not `REQUIRE_CONFIRMATION` (both `ALLOW` and `DENY`, and two real
capabilities measured through the live `decide()`); a foreign outcome or class; a blank policy
version; each of the three non-confirmable actions; naive `created_at` or `expires_at`; a window
that is not in the future; a correlation that already carries an `invocation_id`; a correlation
bound to a different confirmation; blank required text; non-string argument keys.

One test proves P4 compatibility without an import: it calls the real `decide()`, asserts
`matched_row == capability`, and feeds the decision's three fields in.

## 4. Exact binding (19 tests)

The stored binding is accepted; a separately constructed equal binding is accepted; a `list` and a
`tuple` argument compare equal. Then **twelve single-field mutations**, one at a time — action type,
capability, tool name, target, target→`None`, permission class, policy version, canonicalization
version, user id, canonical arguments, canonical arguments→empty, raw arguments — each refused with
`ConfirmationBindingMismatch`, each leaving the record `PENDING` with its binding intact. Also: a
changed `confirmation_id` inside the binding, a nested argument change, and two pending actions in
one session where each approval reaches only its own record.

## 5. Session isolation (6 tests)

Another session cannot `get`, `confirm`, `deny` or `cancel` the record; the record stays `PENDING`
after every attempt; the wrong-session error string is asserted **identical** to the unknown-id
error string; a record cannot be fetched by target, tool name or capability; a blank session is
refused.

## 6. Expiry (8 tests)

The half-open boundary at five explicit timestamps — `T0`, one microsecond before, exactly
`expires_at`, one microsecond after, one day after. Approval at the boundary is refused and the
record becomes `EXPIRED`; approval one microsecond earlier still reaches the dispatcher wall. Every
access (`get`, `deny`, `cancel`) expires a stale record. A stale record never reaches the binding
check. `expire` while still fresh is refused. Naive `now` is refused on three entry points. No TTL
constant exists in the module.

No `sleep`, no real waiting, no wall clock anywhere in the suite.

## 7. Replay resistance (4 tests)

Each of the three terminal states is reached, then approval is attempted three times — all refused,
final state terminal, `execution_started` still `False`. A terminal id cannot be re-registered. A
double `deny` is an explicit error, not a silent success. A caller holding a pre-transition record
object holds data, not authority.

## 8. Store (10 tests)

Duplicate id refused; a record that does not start `PENDING` refused (`DENIED` and `EXECUTING`); a
pending record carrying an `invocation_id` refused; a foreign object refused; unknown id and
non-string id refused; two stores share nothing; the public surface is exactly
`add/cancel/confirm/deny/expire/get`; no listing, "latest", search or iteration accessor exists;
a transition returns a new record and keeps the identical binding object.

## 9. Transition corpus (71 tests)

The frozen file's shape and SHA-256. The state and event vocabularies equal the frozen lists, seven
and six members. No `CONFIRMED` member. Terminal states and dispatcher-owned edges match the
corpus. **Every one of the 42 cells** is parametrized: allowed cells return the frozen target
state, forbidden cells raise `InvalidConfirmationTransition` with the frozen reason. The module's
own `TRANSITIONS` is asserted equal to the corpus's allowed edges. The 30 terminal refusals are
counted. `PENDING` never accepts a dispatch result. Then the three applied edges end to end, the
terminal-refusal matrix, and the confirm wall.

## 10. The no-execution edge (6 tests)

A valid approval raises `ConfirmationDispatcherUnavailable` and the record is byte-equal afterwards
— `PENDING`, `resolved_at` `None`, `invocation_id` `None`, `execution_started` `False`. Five
repeats are deterministic and change nothing. Confirm on each terminal state is an invalid
transition. No method name on the store contains "succeed", "fail", "execute" or "dispatch". The
error is a `NotImplementedError`.

## 11. Model non-authority (8 tests)

`ModelDraft` and `ToolProposal` refused as an argument value, as a deeply nested argument value, as
a permission outcome, as a permission class, as a binding, as a session id and as an id. Eight
affirmative strings refused as confirmation ids with the record left `PENDING`. No field name on
either dataclass is drawn from an eleven-name forbidden list. Statically: no public function
accepts any of eighteen model-shaped parameter names, and **the module compares against no string
literal at all** — asserted over every `ast.Compare` operand.

## 12. Audit and provenance compatibility (9 tests)

The payload is JSON round-trippable; reports `PENDING` with nothing executed; carries the binding
and the correlation id; holds no key in `FORBIDDEN_REASONING_FIELDS` after the audit validator's own
normalization; holds no conversation text. **All five** confirmation events are constructed with
the payload, passed through the real `validate()` and `to_audit_entry()`, and the envelope is
checked. The schema is asserted still v3 with the same five events and no execution-outcome event.
A `CONFIRMATION_REQUIRED` provenance record is built alongside a pending confirmation and asserted
not `VERIFIED`. The action-state and record-state vocabularies are asserted disjoint.

## 13. Non-activation (127 tests)

Zero importers under `app/`; zero references to nineteen public symbols; zero call sites of
`create_confirmation` or `next_state`; the package `__init__` does not export it; eleven named
live-path modules are clean; `to_audit_payload` is defined in exactly two passive modules and
called from no live path.

Legacy: the `_pending_confirmations` dict, the `POST /confirm/{request_id}` route and the `pop` are
all still present verbatim; none of the nineteen symbols appears in `server.py`; the legacy
confirmation slice's SHA-256 is asserted against the value measured at the parent commit.

Purity: 44 forbidden constructs absent from executable code; imports are exactly the nine expected;
`threading` is used for exactly one `Lock` and nothing else; zero `try` blocks; no mutable
module-level object; the audit hook sees zero sensitive events over 30 full exercises; thread count
unchanged; a record only ages when the caller supplies the time; 200 identical approvals give one
answer; the tables are read-only.

Nothing executes: no field value is callable, no tool name is hardcoded, every reachable record
reports `execution_started` `False`, and the audit writer, the provenance ledger and
`registry.call` are each monkeypatched to fail the test if called — then every operation is run.

## 14. Regression

| | before | after |
|---|---|---|
| full suite | 2575 passed, 11 deselected | **2892 passed, 11 deselected, 0 failed** |
| `tests/execution` | 2158 | 2475 |
| golden | 12/20, eight named failures | **12/20, the same eight** |
| legacy probe | `fc68a0b0…` | **byte-identical** |
| critical files | 24 hashes | **24 byte-identical** |
