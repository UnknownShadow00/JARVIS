# Task 13B11F — The Lane Policy

## 1. What a lane is

Contract §4.1: every turn is assigned deterministically to exactly one lane **before any response
is constructed**, and the assignment is never made by a language model (INV-016).

* **OPERATIONAL** — the final user-visible response is built by the control plane from a trusted
  source (§3.2) and is never raw model prose (INV-001, INV-010).
* **CONVERSATIONAL** — model prose may be user-visible, subject to the usual safety and leakage
  checks.

## 2. What a lane is not

Returning `OPERATIONAL` **does not** authorize execution, grant a permission, confirm an action,
create provenance, create trust, or dispatch a tool. Returning `CONVERSATIONAL` **does not** mark
model content as globally trusted — it only says which response-construction path the turn takes,
and the ordinary safety checks still apply to that text.

The lane is also not the request class: the classifier supplies `RequestClass` and this module
consumes it. It is not routing: no primary action, reporting intent, target, tool name or canonical
argument is produced here. It is not safety policy: no permission class, confirmation requirement
or allow/deny decision is made here.

## 3. The policy, in full

```
if request_class is not a RequestClass member   -> raise LanePolicyError
if request_class in ALWAYS_OPERATIONAL_CLASSES  -> OPERATIONAL
if any operational condition is true            -> OPERATIONAL
otherwise                                       -> CONVERSATIONAL
```

Seven classes are always operational: `VALUE_QUERY`, `ACTION_REQUEST`, `STATUS_CHECK_REQUEST`,
`DECLARATIVE_FACT`, `AMBIGUOUS_ACTION`, `MISSING_CONTEXT_QUERY`, `CONFIRMATION_SENSITIVE_ACTION`.
`GENERAL_EXPLANATION` and `OTHER` default to conversational and escalate.

Seven conditions escalate: `tool_proposal`, `tool_result`, `confirmation_required`,
`active_operational_provenance`, `operational_correction`, `action_target`,
`external_status_claim_required`. They are not weighted, ordered or combined — any one is
sufficient.

## 4. Escalation only

There is no branch that returns `CONVERSATIONAL` for a turn already found operational, and no input
that can produce one. A false or absent condition never downgrades an always-operational class; the
128-combination sweep over each of those seven classes yields `{OPERATIONAL}` and nothing else.
That is the structural form of §4.2: a turn that is operational must not be re-labelled
conversational in order to let model prose reach the user.

## 5. Why `GENERAL_EXPLANATION` escalates

The contract YAML calls its second list `always_conversational_classes`, which read alone would
make that class immune to the seven conditions. The normative text says otherwise, and the
normative text governs: §4.1 defines OPERATIONAL by what a turn *involves*, naming "a tool result"
among them; §4.3 says the conditions apply "additionally", which is only meaningful for classes not
already unconditionally operational; §4.2 forbids the opposite outcome outright; and INV-001 and
INV-010 fail if a turn holding a tool result is handed to the conversational lane. Of the two
readings, only this one cannot make model prose more trusted. Recorded in full in
`TRUTH_TABLE.md` §6 — it is an interpretation of the frozen contract, not a change to it.

The practical case: the user asks what blue-green deployment is, and the same turn carries a tool
result. The explanation is still explanation, but the turn now holds an operational fact, and a
response that mixes the two must be built by the control plane. The lane says so.

## 6. Fail-closed

Malformed input raises `LanePolicyError`; it never yields a lane. Falling back to
`CONVERSATIONAL` on bad input would be a raw-prose bypass reachable by corrupting the deterministic
state, so there is no fallback lane at all. `RequestClass` is a `str` enum, so a bare
`"VALUE_QUERY"` compares and hashes equal to the member — membership is therefore checked by
`isinstance`, not by equality or table lookup.

## 7. Why the conditions are booleans the caller supplies

`active_operational_provenance` and `operational_correction` are facts about the P2 ledger, but the
policy does not read the ledger. Passing the projection keeps the function pure, keeps it testable
as a table, and stops the lane policy acquiring a hidden dependency on P2 storage — which is also
what the task required. The same applies to the router-owned and confirmation-owned conditions.

## 8. Reasons

Contract §14.1 names "lane reasons" as a frozen input to the obligation engine, so `explain()`
returns a `LaneDecision` carrying an ordered `LaneReason` tuple: the always-operational class first
where it applies, then each condition that held, in declared order; or the single
`NO_OPERATIONAL_STATE` reason on a conversational turn. Reasons are metadata — they authorize
nothing and create no provenance — and `lane` is still **not** one of the seventeen contract audit
fields. That promotion remains a deferred operator decision.
