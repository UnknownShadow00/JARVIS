# Obligation Priority — Task 13B11L

**Checked against production. Complete and correct. This is not the blocking item.**

Task §9 requires the engine to reference the existing frozen constant and to block if it is
incomplete or duplicated. Measured on production `a0cc4d3` (evidence `04-priority-proof.txt`):

| Check | Result |
|---|---|
| `ResponseObligation` members | 11 |
| `OBLIGATION_PRIORITY` entries | 11 |
| members missing from the priority map | none |
| entries not corresponding to a member | none |
| ranks | `[1…11]`, each exactly once |

```
 1  REQUEST_CONFIRMATION
 2  REPORT_TOOL_ERROR
 3  REPORT_TOOL_SUCCESS
 4  REQUEST_TARGET
 5  REPORT_MULTI_ACTION_LIMIT
 6  REPORT_CAPABILITY_UNAVAILABLE
 7  ANSWER_LEDGER_VALUE
 8  ACKNOWLEDGE_FACT
 9  REPORT_UNVERIFIED_STATUS
10  ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION
11  MISSING_CONTEXT
```

This is contract §14.2's list verbatim, in order, and it matches the validated
13B10C5 `response-obligation-design.json` `priority_order` one for one.

**Rule for the implementation:** the engine walks this mapping and stops at the first obligation
the frozen state supports (§14.2). It must not contain a second hand-written ordering, and the
test that proves the walk must read `OBLIGATION_PRIORITY` rather than restate it — otherwise the
test and the code share an error.

`MISSING_CONTEXT` is last and is never selected while a higher-priority grounded source exists
(§14.2, INV-018, CT-018).
