# P3 Classifier / Router Reconciliation — Task 13B11L §32

**Outcome: the cases are NOT separable from the structured P3 outputs. P6 is blocked.**

This is the analysis the task required before any implementation, and it is the reason the
verdict is `JARVIS RESPONSE OBLIGATION FOUNDATION BLOCKED`.

---

## 1. What 13B11H carried forward

`tasks/task13b11h/IMPLEMENTATION.md:106`:

> `REPORT_CAPABILITY_UNAVAILABLE` — so P6 will have to reconcile the lists. Recorded here and
> carried forward.

The two lexicons are independent frozensets in two independently sealed modules:

* `app/execution/classifier.py::ACTION_VERBS` — 44 members. Decides whether a request is
  *action-bearing at all*.
* `app/execution/router.py::UNSUPPORTED_VERBS` — 41 members. Names explicit operations for which
  no authorized tool exists, so that `UNKNOWN_ACTION` is *"a decision, not an accident"* (the
  module's own comment, contract §13.2).

## 2. The gate that makes the mismatch matter

`router.py::ACTION_BEARING_CLASSES` = {`ACTION_REQUEST`, `CONFIRMATION_SENSITIVE_ACTION`,
`AMBIGUOUS_ACTION`, `STATUS_CHECK_REQUEST`}. The router short-circuits to `PrimaryAction.NONE`
with `RouteReason.CLASS_NOT_ACTION_BEARING` for every other class, *before any lexical
extraction runs* — deliberately, "so the router never contradicts the classifier".

So `UNSUPPORTED_VERBS` is only ever consulted for a request the **classifier** already judged
action-bearing. A verb the classifier does not know cannot reach the router's verdict.

## 3. Measured, not argued

Every one of the 41 router `UNSUPPORTED_VERBS` was run through the real production chain
`classify → route → lane` (evidence `05-verb-sweep.txt`, read-only, nothing modified):

| | count |
|---|---|
| reach `UNKNOWN_ACTION` + `OPERATIONAL` — correct per §13.1 | **21 / 41** |
| fall through to `OTHER` / `NONE` / `CONVERSATIONAL` | **20 / 41** |

The twenty that fall through — the task named five of them; the real gap is four times larger:

```
backup  build   clear   commit  download  fix     flush   merge   modify  patch
pull    reset   restore revert  roll      rollback rotate scale   upgrade upload
```

All twenty produce **one identical structured signature**:

```
RequestClass.OTHER
ClassificationReason.NO_MATCHING_RULE
PrimaryAction.NONE
RouteReason.CLASS_NOT_ACTION_BEARING
target=None  target_resolved=None  multi_action=False  capability_available=False
ReportingIntent.NONE
Lane.CONVERSATIONAL
```

## 4. Why P6 cannot fix it

Plain conversational input — `"hello there"`, `"thanks"`, `"okay"`, `"hmm"`, `"good morning
sir"`, `"tell me a joke"` — produces **the same signature, byte for byte**. Measured overlap: 1
identical signature; separable by structured state: **False**.

Every candidate P6 rule fails:

| Candidate rule | Why it fails |
|---|---|
| `RequestClass.OTHER` → `REPORT_CAPABILITY_UNAVAILABLE` | answers "thanks" with a capability refusal. `OTHER`/`no_matching_rule` is the classifier's catch-all, not a capability signal |
| use `RouteReason.REQUESTED_OPERATION_HAS_NO_AVAILABLE_TOOL` | correct signal, never produced for these twenty — the class gate fires first |
| use a caller-supplied capability projection (§33) | the caller holds only the classifier and router outputs. Something must first decide "this is a requested operation", which is precisely P3's job |
| force the lane operational in P6 | contract §4.1/§4.2 and task §28 forbid P6 being a second lane classifier |
| inspect the request text in `obligations.py` | forbidden by task §12 and contract §15.3 ("no second recogniser") — and this is exactly where benchmark-specific matching hides |

There is no fifth option. The information required does not exist in P6's inputs.

## 5. The consequence is a live contract violation, not a cosmetic gap

Contract §13.1 is NORMATIVE:

> If a requested action has no authorized tool, the control plane **MUST** classify it
> `UNKNOWN_ACTION` and answer with `REPORT_CAPABILITY_UNAVAILABLE`. It **MUST NOT** allow the
> model to imply that the action happened, is happening, or will happen.

Today `"rollback the last deployment"` is assigned `Lane.CONVERSATIONAL`, and contract §4.2 says
that on the conversational lane *"model prose **MAY** be user-visible"*. So a request to roll
back a deployment currently routes to an unconstrained model answer, with no obligation, no
capability refusal and no operational source lock.

That is the exact failure this whole contract exists to prevent. It is a defect in the **P3
foundation**, present since 13B11G, and it is not P6's to repair.

Nothing is currently wired, so nothing is at risk today — but the defect must be fixed before P6
freezes a matrix whose `REPORT_CAPABILITY_UNAVAILABLE` rows depend on these inputs, and long
before any live wiring.

## 6. Why blocking is the right call rather than building P6 anyway

The obligation engine could be written today and would be correct for every turn that reaches
it. But:

1. Task §32 makes this analysis a decision gate with an explicit verdict, and §81 lists the
   reconciliation as an acceptance item.
2. The frozen obligation matrix (§46) has to be hashed *before* implementation. One of its
   inputs — which turns arrive as `REPORT_CAPABILITY_UNAVAILABLE` — is about to change. Freezing
   it now would mean re-freezing it immediately, which defeats the method that has protected
   every phase in this series.
3. The honest order is: fix the foundation, then build on it.
