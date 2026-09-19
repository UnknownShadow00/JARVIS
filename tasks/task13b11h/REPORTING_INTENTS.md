# Task 13B11H — Reporting Intent

## 1. Non-executable metadata

Contract §7.1: `REPORTING_INTENT` is **non-executable metadata**. A reporting clause **MUST NOT**
cause an additional action, a second dispatch, or an additional tool proposal to be authorized.
INV-017 states the same as an invariant.

Contract §7.2: *"Open VS Code and tell me whether it worked."* **MUST** yield exactly one
`OPEN_APP` proposal with reporting intent `REPORT_SUCCESS`. It **MUST NOT** yield two actions.

## 2. The production enum

`ReportingIntent` from `app/execution/types.py`, six members, imported and never redefined:
`REPORT_RESULT`, `REPORT_SUCCESS`, `REPORT_FAILURE`, `REPORT_COMPLETION`, `REPORT_STATUS`, `NONE`.

## 3. Extraction, separate from action extraction

Two independent passes over the request:

* **action extraction** walks the segmented clauses and ignores `REPORTING` clauses entirely;
* **reporting extraction** searches the whole request for a reporting anchor and reads only the
  tail that follows it.

They share no state. A reporting clause can therefore never contribute a verb to the action pass,
and the action pass can never consume the reporting tail.

```
anchor:  \b(?:tell\s+me|let\s+me\s+know|keep\s+me\s+posted|report(?:\s+back)?|confirm
          |notify\s+me|inform\s+me|show\s+me|update\s+me)\b
```

No anchor → `ReportingIntent.NONE` and no reporting clause. Note the anchor set omits the bare
`say` that the clause-start pattern includes: `say` opens a reporting clause but is too common
mid-sentence to anchor one. Both patterns are frozen exactly as C4 froze them.

## 4. The keyword families, in frozen precedence order

| Order | Intent | Keywords |
|---|---|---|
| 1 | `REPORT_FAILURE` | fail, fails, failed, failing, failure, broke, broken, error, errors |
| 2 | `REPORT_COMPLETION` | complete, completes, completed, completion, done, finish, finished, finishes, gone, over |
| 3 | `REPORT_SUCCESS` | work, works, worked, working, succeed, succeeds, succeeded, success, successful, opens, opened |
| 4 | `REPORT_STATUS` | status, reachable, unreachable, healthy, unhealthy, up, down, live, alive, available, unavailable, state |
| 5 | `REPORT_RESULT` | result, results, outcome, what happened, response, output |
| — | `REPORT_RESULT` | **default** when an anchor is present and no family matches |

Order matters and is frozen: "tell me whether the deployment failed or completed" has keywords in
two families and resolves to `REPORT_FAILURE`, because failure is the outcome the user most needs
told accurately. Asserted by a precedence test, not left to pattern order.

`REPORT_RESULT` appears twice deliberately — as the fifth family and as the generic default. The
C4 pre-registration states it: *"REPORT_RESULT is the generic value when a reporting clause is
present with no failure/completion/success/status keyword."*

## 5. Reporting intent is independent of the action

A reporting intent is extracted even when the primary action is `NONE`, `UNKNOWN_ACTION` or
`MULTI_ACTION_UNSUPPORTED`. Three frozen regression rows prove this matters:

| Row | Request | Action | Intent |
|---|---|---|---|
| `g:G03` | "Restart the API and tell me when it's healthy." | `UNKNOWN_ACTION` | `REPORT_STATUS` |
| `g:G08` | "Production is the target; tell me what that means, don't deploy." | `NONE` | `REPORT_RESULT` |
| `k:K10` | "The database seems down; tell me what that means." | `NONE` | `REPORT_RESULT` |

Recording what the user asked to be told, while refusing to act, is what lets the later obligation
engine (§14) answer honestly instead of silently.

## 6. What it never does

It never adds an action, never becomes a target, never bypasses a later confirmation, and never
licenses a claim the tool result does not contain (§7.2). The router emits the intent and the
matched clause text; asserting anything about an outcome is §15 and §16 work.
