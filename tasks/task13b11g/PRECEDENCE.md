# Task 13B11G — Precedence

Derived from the frozen contract and the 13B10C2 selector **before** implementation. Precedence is
data: `RULES` is a tuple in this order and evaluation is first-match-wins, so no behaviour depends
on which `if` happens to be written first.

## 1. The order

```
1  R-01-action-ambiguous       AMBIGUOUS_ACTION
2  R-02-action-sensitive       CONFIRMATION_SENSITIVE_ACTION
3  R-03-action-explicit        ACTION_REQUEST
4  R-04-status-explicit        STATUS_CHECK_REQUEST
5  R-05-value-supplied         VALUE_QUERY
6  R-06-context-missing        MISSING_CONTEXT_QUERY
7  R-07-value-current          VALUE_QUERY
8  R-08-explanation            GENERAL_EXPLANATION
9  R-09-status-question        STATUS_CHECK_REQUEST
10 R-10-declarative            DECLARATIVE_FACT
11 R-11-other                  OTHER
```

This is the 13B10C2 order with the capability special-case removed and the value/context split made
explicit: the diagnostic evaluated ambiguity, then explicit action, then explicit read, then value,
then explanation, then missing-context, then the status question, then the declarative statement,
then `OTHER`.

## 2. Every documented overlap and how it resolves

| # | Overlap | Wins | Why |
|---|---|---|---|
| 1 | action verb **and** ambiguous target (`delete it`) | **AMBIGUOUS_ACTION** (1 over 2) | contract §17.1: if a required target is missing or unresolved the control plane must not dispatch and must not invent a target. Ambiguity outranks sensitivity because a sensitive action with an unknown target is the more dangerous of the two readings, and `clarify-delete-target-002` in the golden is exactly this shape. |
| 2 | action request **vs** confirmation-sensitive action (`delete ~/Downloads`) | **CONFIRMATION_SENSITIVE_ACTION** (2 over 3) | the sensitive verb family is a strict subset of the action family, so the narrower rule must be evaluated first or it could never fire. |
| 3 | sensitive verb inside a status request (`check whether the deploy finished`) | **STATUS_CHECK_REQUEST** | the leading token decides; `check` opens the clause, `deploy` does not. Rules 2 and 3 test the **clause-initial** token only. |
| 4 | status question **vs** general explanation (`why is the deployment slow?`) | **GENERAL_EXPLANATION** (8 over 9) | the explanation form is the narrower test — it matches an explanatory opener, not merely a yes/no opener — so it is evaluated first. A bare yes/no question with no explanatory opener (`is blue-green deployment safe?`) therefore classifies `STATUS_CHECK_REQUEST`, which is the 13B10C2 behaviour and a known conservative over-classification: it places the turn on the operational lane, where raw model prose cannot be final. |
| 5 | value query **vs** missing-context query (`what did I say the target was?`) | **VALUE_QUERY** when a candidate key is known (5), **MISSING_CONTEXT_QUERY** when it is not (6) | the same text is one class or the other purely on the caller-supplied context (contract §5.1 derives the class from the text *and* the control plane's own state). Both are always-operational lane classes, so neither reading can expose model prose. |
| 6 | value query **vs** general explanation (`what is the deployment target?`) | **VALUE_QUERY** only when the candidate key is known (7 before 8); otherwise **GENERAL_EXPLANATION** | contract §4.1 lists definition and non-operational technical discussion as conversational: operational vocabulary alone must not force an operational reading. `what is blue-green deployment?` has no known candidate key, so it is an explanation. |
| 7 | action-like language with a missing target that is *not* clause-initial (`I want to remove the old logs`) | **DECLARATIVE_FACT** or **OTHER**, never an action | rules 1–3 require the verb in clause-initial position, so a mentioned verb cannot become a request. |
| 8 | declarative operational fact **vs** action request (`the deployment target is staging`) | **DECLARATIVE_FACT** (10) | the clause does not open with an action verb; it opens with an article. contract §16.1 treats a user-supplied operational value as reported state, not an act: nouns like *target*, *port* and *service* never make an action. |
| 9 | general explanation containing operational nouns (`why can latency make an application feel slow?`) | **GENERAL_EXPLANATION** (8) | the explanation form matches on the interrogative opener, not on the nouns. |
| 10 | status check **vs** unsupported user conclusion (`the database is obviously down`) | **DECLARATIVE_FACT** (10) | no clause-initial status verb and not a question, so rule 4 and rule 9 both miss. contract §16.1: a user's own conclusion is user-supplied state, not independently verified state, so it is not a status check. |
| 11 | compound request (`open VS Code and tell me whether it worked`) | the **leading clause** decides → `ACTION_REQUEST` | §7.1: a reporting clause is non-executable metadata and must not displace the action. Reporting intent itself is router output (§5.2) and is not produced here. |
| 12 | two actions in one request (`open VS Code and deploy to staging`) | the **leading clause** decides → `ACTION_REQUEST` | §8 `MULTI_ACTION_UNSUPPORTED` is a **router** outcome, not a request class; `RequestClass` has no multi-action member. The classifier records the class of the request; the router detects the second action and refuses to dispatch. Documented limitation, not a silent one. |

## 3. Downgrade direction

Nothing in the table can turn an operational class into `GENERAL_EXPLANATION` or `OTHER` because a
context signal is absent: rules 5 and 6 both produce always-operational classes, and rule 7's
failure falls to rule 8 only for text that matched the explanation form in the first place. Absent
context makes the classification *more* conservative, never less.

## 4. Freeze

This table and `RULES_AND_LEXICON.md` were hashed before the module and before any scored test
existed. The implementation must reproduce them; if implementation and table disagree, the
implementation is wrong.
