# Task 13B11E — Rule Versioning

## 1. The literal

```
CANONICALIZATION_VERSION = "1"
```

13B11A does not specify the literal; it specifies only that the version exists and is carried on
`ToolInvocation.canonicalization_version` and in the audit event. `"1"` is the smallest stable
initial value. It is a **string** because that is the type the frozen P0 `ToolInvocation` field and
the P1 audit field already use.

It versions **the rule set**, not the contract. Contract v1 and audit schema v3 are separate and
were not touched; `"1"` implies nothing about a contract v2.

## 2. What the version is for

| Consumer | Why it needs the version |
|---|---|
| audit (`dispatch.invoked`) | the recorded invocation can be reproduced exactly |
| `ToolInvocation` | the invocation states which rule set produced its canonical arguments |
| confirmation binding (P4) | an approval granted under one rule set must not execute under another — risk R-07, "the user confirms X and Y executes" |
| rollback | reverting a rule change is identifiable in the log rather than invisible |

## 3. When the version must change

Any change to observable behaviour: adding an alias, removing one, changing a canonical value,
changing a match policy, or changing the scope of a rule. A change that alters what
`canonicalize()` returns for any input requires a new version, so that two invocations recorded
under the same version are guaranteed to have been canonicalized the same way.

Comments, docstrings and internal refactoring that cannot change any output do not.

## 4. How a future version should be introduced

The version is one module-level constant and the rules are one tuple, so a v2 is a data change plus
a constant bump. Two properties should hold when that happens:

* old audit records keep their `"1"` and remain interpretable — the version is recorded, never
  inferred;
* a pending confirmation carrying `"1"` must be re-derived and compared before execution rather
  than being executed under the new rules (`CONFIRMATION_STATE_PLAN.md` §4, R-07).

Neither is implemented here — P4 owns confirmation — but the version exists so that P4 can.

## 5. Stability today

Every result carries `version="1"`, including results where nothing changed. A test asserts the
literal, a test asserts it is a string, and the determinism test asserts it is stable across 1,000
calls.
