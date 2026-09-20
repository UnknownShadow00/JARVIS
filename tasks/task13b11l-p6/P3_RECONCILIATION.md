# P3 Reconciliation — Task 13B11L-P6

The blocked task's finding, and the proof it is resolved.

## 1. What was wrong

`tasks/task13b11l/P3_RECONCILIATION.md` measured it: 20 of the router's 41
`UNSUPPORTED_VERBS` were not in `classifier.ACTION_VERBS`, so they classified `OTHER`,
routed to `NONE` and landed on `Lane.CONVERSATIONAL`, where contract §4.2 permits raw model
prose — while §13.1 (NORMATIVE) requires `UNKNOWN_ACTION` answered with
`REPORT_CAPABILITY_UNAVAILABLE`. `"rollback the last deployment"` routed to an unconstrained
model answer.

P6 could not separate those twenty from plain chat without reparsing text, which §15.3 and
the task forbid, so 13B11L **BLOCKED** rather than working around it.

## 2. What fixed it

| Task | Production | Change |
|---|---|---|
| 13B11L-R1 | `9ace0e3a` | 20 verbs added to `ACTION_VERBS` (44 → 64), 14 of them also to `SENSITIVE_ACTION_VERBS` (26 → 40) |
| 13B11L-R2 | `ea0cb320` | `CLASSIFIER_VERSION` "1" → "2", naming the repaired rule set |

## 3. Measured here, before any P6 code was written

Section 6 of this task re-ran the real `classify -> route -> lane` chain at `ea0cb320`:

```
classifier_version        2
router_version            1
lane_policy_version       1
unsupported verbs        41
reaching UNKNOWN_ACTION + OPERATIONAL   41/41
of which previously lost                20/20
plain chat still conversational          7/7
supported actions still routed           8/8
```

The blocker is gone.

## 4. Measured again, through the engine

The 41 verbs are group `G6` of the frozen matrix and a parametrized test class of their own
(`obligations_p3_reconciliation_test.py`), composed through the live chain, not hand-written:

* **41/41** reach `REPORT_CAPABILITY_UNAVAILABLE`, rank 6, reason
  `explicit_action_without_tool`;
* **20/20** of the formerly lost verbs are neither `RequestClass.OTHER` nor
  `Lane.CONVERSATIONAL`, and carry an obligation rather than none;
* **0/41** are answered with `REQUEST_CONFIRMATION`, `REQUEST_TARGET`,
  `REPORT_TOOL_SUCCESS` or `ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION` — the four that would each
  imply the action can or did happen;
* the composed classification carries `classifier_version == "2"`.

## 5. What the freeze caught on the way

Landing on the operational lane was necessary but not sufficient. Frozen against the
repaired outputs, all 41 first landed on rank 1 or rank 4:

* 22 classified `CONFIRMATION_SENSITIVE_ACTION` (the sensitive half of R1's split) would
  have been answered *"shall I proceed?"*;
* 19 with `target_resolved=False` would have been answered *"which one?"*.

Both imply an execution that can never happen. §13.1: *"It MUST NOT allow the model to imply
that the action happened, is happening, or will happen."* The rank 1 and rank 4 predicates
were corrected — see `OBLIGATION_PRIORITY.md` §3 — against production's own rules, not
against taste: the permission engine denies every non-executable action, the confirmation
layer refuses to bind one, and §12.3 requires an approval to bind a target.

R1 flagged `"reset the service"` as `AMBIGUOUS_ACTION` by precedence and left it open. It
now reaches `REPORT_CAPABILITY_UNAVAILABLE` like the rest: rank 4's class limb excludes
`UNKNOWN_ACTION`. R1's other open item — `"rollback the last deployment"` is sensitive while
`"roll back the deployment"` is ordinary — is unaffected here, because both spellings are
`UNKNOWN_ACTION` and both land on rank 6.

## 6. Chat separation

Task §49. Seven plain-chat controls stay `CONVERSATIONAL` with `PrimaryAction.NONE` and
carry **no** obligation. `"that is interesting"` is `DECLARATIVE_FACT` and therefore
operational — it was before the repair too — and is answered `ACKNOWLEDGE_FACT`, never
`REPORT_CAPABILITY_UNAVAILABLE`. Three ambiguous phrasings (`"delete it"`, `"open that"`,
`"remove the thing"`) route to a *supported* action with an unresolved target and are
answered `REQUEST_TARGET`, which is the distinction rank 4 exists to draw.

## 7. No knowledge of any of this lives in the engine

`obligations.py` contains no verb from either lexicon, no request string, no regular
expression, no import of `classifier` or `router`, and no `str` field on `ObligationState`.
Asserted three ways: an AST import-budget test, a source scan over all 41 verbs and every
control string, and the static no-raw-text tests. The composition above is the test's job.
