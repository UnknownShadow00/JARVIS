# Obligation Priority — Task 13B11L-P6

## 1. One ordering, and it is the contract's

`OBLIGATION_PRIORITY` in `app/execution/types.py` is the only ordering. The engine declares
no second list: `Rule.priority` is a property that reads `OBLIGATION_PRIORITY[self.obligation]`,
and a test asserts that for every rule.

Verified independently before implementation and again in the suite: eleven members, ranks
1–11, each exactly once, identical to contract §14.2.

| Rank | Obligation | §14.2 wording |
|---|---|---|
| 1 | `REQUEST_CONFIRMATION` | confirmation required |
| 2 | `REPORT_TOOL_ERROR` | trusted tool error |
| 3 | `REPORT_TOOL_SUCCESS` | trusted tool success |
| 4 | `REQUEST_TARGET` | ambiguity / required target missing |
| 5 | `REPORT_MULTI_ACTION_LIMIT` | multiple supported actions |
| 6 | `REPORT_CAPABILITY_UNAVAILABLE` | capability unavailable |
| 7 | `ANSWER_LEDGER_VALUE` | direct ledger-value answer |
| 8 | `ACKNOWLEDGE_FACT` | user-fact acknowledgement |
| 9 | `REPORT_UNVERIFIED_STATUS` | unverified-status response |
| 10 | `ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION` | acknowledged intent without execution |
| 11 | `MISSING_CONTEXT` | missing context |

## 2. A walk over state, not a table of cases

§14.3 forbids per-scenario branches. The engine holds twenty-one rules, each one statement
about the world, each carrying its obligation's rank. Every predicate is **conjunctive and
self-contained**: it holds only where its own obligation is the honest one.

That makes the rules order-independent, and the claim is measured rather than asserted.
`satisfied(state)` returns every rule whose predicate holds, and the matrix test checks, on
all 361 valid operational rows:

```
min(RULE_INDEX[r].priority for r in satisfied(state)) == derive(state).priority
```

So the answer is the same whether the walk stops at the first match or takes the minimum
rank. Nothing depends on declaration order.

Within a rank, several rules may hold — they select the same obligation and differ only in
the reason. The first declared supplies it, and that tie-break is documented in the module.

## 3. The two predicates the frozen table corrected

The first draft of the ladder was the validated 13B10C5 one. Freezing it against the
repaired P3 outputs showed all 41 router-unsupported verbs landing on rank 1 or rank 4
instead of rank 6 — 22 answered "shall I proceed?" and 19 answered "which one?". Both imply
an execution that can never happen, which §13.1 forbids in terms.

The defect was in the predicates, not the priority order:

* **Rank 1** now requires an action an approval could bind. §12.3 binds an approval to an
  action type *and a target*; the permission engine denies every non-executable action and
  the confirmation layer refuses to bind one. So the class-derived limb also requires
  `target_resolved is not False`.
* **Rank 4** now requires an action that *has* a tool. §17.1 speaks of a **required**
  target; an action with no tool requires nothing, so an unresolved target never displaces
  rank 6.

Measured after: 41/41 on rank 6 with reason `explicit_action_without_tool`, and the three
supported confirmation-sensitive controls (`deploy to staging`, `delete /tmp/old`,
`remove /var/log/app.log`) still on rank 1.

## 4. Overlaps

Thirty-eight overlap rows are frozen in group `G8`, one per meaningful pair of ranks in
play, each recording which must win. Where the higher number wins it is because the lower
rank's predicate is *not* satisfied, and the min-rank check above proves that rather than
assuming it. Examples:

| Row | In play | Winner | Why |
|---|---|---|---|
| `G8-6over1` | 1, 6 | 6 | an action with no tool cannot be confirmed |
| `G8-6over4` | 4, 6 | 6 | an action with no tool requires no target |
| `G8-4over1` | 1, 4 | 4 | an approval cannot bind an unresolved target |
| `G8-2v1` | 1, 2 | 2 | rank 1 requires that nothing executed |
| `G8-7v11` | 7, 11 | 7 | CT-018: a grounded value outranks missing context |
| `G8-10v7` | 7, 10 | 10 | an incidental value does not answer an action request |

## 5. `MISSING_CONTEXT` is last, and only last

INV-018 / CT-018. Rank 11b is the total fallback, so exactly one obligation always exists.
The matrix test walks every `MISSING_CONTEXT` row and asserts no value is current, no result
exists, and the only rules that hold are the two at rank 11.
