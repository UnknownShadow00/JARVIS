# Task 13B11F — Frozen Lane Truth Table

Derived from the frozen contract **before** implementation, and hashed before any scored test was
written. The implementation must reproduce this table exactly; it was not read back out of the code.

## 1. Normative sources

| Source | What it fixes |
|---|---|
| `JARVIS_AGENT_EXECUTION_CONTRACT.md` §4.1 (NORMATIVE) | the definition of each lane by what the turn *involves* |
| §4.2 (NORMATIVE) | operational responses are control-plane built; **a turn that is operational MUST NOT be re-labelled conversational in order to allow model prose to reach the user** |
| §4.3 (NOTE) | the validated class→lane assignment and the seven additional operational conditions |
| `agent-execution-contract.yaml` `response_lanes.lane_decision` | the machine-readable lists used verbatim below |
| §14.1 (NORMATIVE) | "lane reasons" are a frozen input to the P6 obligation engine |
| INV-001, INV-010, INV-016 | raw operational prose never final; operational responses have a non-model source; the lane decision is deterministic and never made by a model |

## 2. The two frozen lists, copied verbatim from the contract YAML

```
always_operational_classes:
  [VALUE_QUERY, ACTION_REQUEST, STATUS_CHECK_REQUEST, DECLARATIVE_FACT,
   AMBIGUOUS_ACTION, MISSING_CONTEXT_QUERY, CONFIRMATION_SENSITIVE_ACTION]
always_conversational_classes: [GENERAL_EXPLANATION]
additional_operational_conditions:
  - tool_proposal
  - tool_result
  - confirmation_required
  - active_operational_provenance
  - operational_correction
  - action_target
  - external_status_claim_required
```

`RequestClass` in production holds exactly nine members: the seven above, `GENERAL_EXPLANATION`,
and `OTHER`.

## 3. Class table

| # | RequestClass | Default lane | Overrides apply? | Downgrade ever allowed |
|---|---|---|---|---|
| 1 | `VALUE_QUERY` | OPERATIONAL | moot — already operational | **never** |
| 2 | `ACTION_REQUEST` | OPERATIONAL | moot | **never** |
| 3 | `STATUS_CHECK_REQUEST` | OPERATIONAL | moot | **never** |
| 4 | `DECLARATIVE_FACT` | OPERATIONAL | moot | **never** |
| 5 | `AMBIGUOUS_ACTION` | OPERATIONAL | moot | **never** |
| 6 | `MISSING_CONTEXT_QUERY` | OPERATIONAL | moot | **never** |
| 7 | `CONFIRMATION_SENSITIVE_ACTION` | OPERATIONAL | moot | **never** |
| 8 | `GENERAL_EXPLANATION` | CONVERSATIONAL | **yes** — any condition escalates | **never** |
| 9 | `OTHER` | CONVERSATIONAL | **yes** — any condition escalates | **never** |

## 4. Override conditions

Each is a deterministic boolean supplied by the caller. Any one being true is sufficient; they are
not weighted, ordered or combined. `True` can only ever move a turn toward OPERATIONAL.

| # | Condition | Contract name | Supplied later by |
|---|---|---|---|
| 1 | a tool proposal exists for the turn | `tool_proposal` | P3 router / P5 dispatcher |
| 2 | a trusted tool result exists for the turn | `tool_result` | P5 dispatcher |
| 3 | the turn is in confirmation-required state | `confirmation_required` | P4 confirmation |
| 4 | the turn involves an active operational value | `active_operational_provenance` | P2 ledger, **projected by the caller** |
| 5 | the turn carries an operational correction | `operational_correction` | P2 ledger, projected by the caller |
| 6 | the turn has an action target | `action_target` | P3 router |
| 7 | the turn requires an external status claim | `external_status_claim_required` | P3 router / P6 obligations |

## 5. Resolution rule (the whole policy)

```
if request_class is not a RequestClass member      -> raise (never a lane)
if request_class in ALWAYS_OPERATIONAL_CLASSES     -> OPERATIONAL
if any override condition is true                  -> OPERATIONAL
otherwise                                          -> CONVERSATIONAL
```

Escalation only. There is no branch anywhere that turns OPERATIONAL into CONVERSATIONAL, and no
input that can do so.

## 6. Interpretation recorded, not guessed: does an override reach `GENERAL_EXPLANATION`?

The YAML key is named `always_conversational_classes`, which read alone would make
`GENERAL_EXPLANATION` immune to the seven conditions. The contract resolves this against that
reading, and the table above follows the contract:

* §4.1 is **NORMATIVE** and defines OPERATIONAL by what the turn *involves* — "an action; a status
  question; a current operational value; an operational fact the user supplied; a correction; a
  confirmation-sensitive action; an ambiguous action; missing operational context; **a tool result**;
  or an operational capability question." A turn carrying a tool result involves a tool result
  whatever its request class, so it is operational by definition.
* §4.3 states the class assignment and then says the implementation "**additionally** forces
  OPERATIONAL when any of these is present". *Additionally* is only meaningful for turns not already
  unconditionally operational — that is, exactly `GENERAL_EXPLANATION` and `OTHER`.
* §4.2 forbids the opposite outcome outright: a turn that is operational must not be re-labelled
  conversational to let model prose reach the user. Treating an explanatory class as immune would
  produce precisely that.
* INV-001 and INV-010 fail if a turn holding a tool result is handed to the conversational lane,
  because raw model prose may then be final for a turn with operational content.
* Fail-closed: of the two readings, only this one cannot make model prose *more* trusted.

`always_conversational_classes` is therefore read as the **default** lane for that class — the
answer to "what lane when nothing operational is present" — which is how the same list functions
for `OTHER` in §4.3's own prose.

## 7. Enumeration

9 classes × 2⁷ condition combinations = **1,152 rows**, all enumerable and all covered by
parametrized tests:

* rows 1–7 × 128 combinations = **896 rows**, every one OPERATIONAL (the no-downgrade proof);
* `GENERAL_EXPLANATION`: 1 row CONVERSATIONAL (all false) + 127 OPERATIONAL;
* `OTHER`: 1 row CONVERSATIONAL (all false) + 127 OPERATIONAL.

Total: 1,150 OPERATIONAL, 2 CONVERSATIONAL.

## 8. Reasons

Contract §14.1 names "lane reasons" as a frozen input to the P6 obligation engine, so the decision
carries a deterministic, ordered reason tuple: the always-operational class, then each condition
that was true in declared order, or the single no-operational-state reason. Reasons are metadata.
They grant nothing, and they are **not** added to the 17-field audit schema — that remains a
deferred operator decision.

## 9. What the table does not decide

Not permission, not confirmation, not dispatch, not obligation, not the response text, not the
request class itself. OPERATIONAL authorizes nothing; CONVERSATIONAL trusts nothing globally.
