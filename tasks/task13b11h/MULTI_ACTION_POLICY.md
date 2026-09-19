# Task 13B11H — Multi-Action Policy and Route Selection

## 1. The contract

Contract §8.1: two or more distinct **executable** actions in a single request **MUST NOT** be
silently partially executed. The control plane **MUST** classify the request
`MULTI_ACTION_UNSUPPORTED`, dispatch nothing, and answer with the multi-action limitation
obligation (§14). INV-012 states it as an invariant. §8.2 reserves multi-action planning for
separately authorized work.

§8.3 records the validation: 20/20 multi-action turns classified correctly in 13B10C5 with **0**
dispatches, and a specific user-facing limitation message rather than a silent refusal.

## 2. Selection order — frozen, first match wins

After segmentation, every clause is analysed independently. Then:

| Rank | Condition | Result |
|---|---|---|
| 1 | the supplied `RequestClass` is not action-bearing | `NONE`, reason `class_not_action_bearing` |
| 2 | two or more clauses yield a **supported** action | `MULTI_ACTION_UNSUPPORTED`, reason `multiple_supported_executable_actions` |
| 3 | exactly one clause yields a supported action | that action, with its target and resolution state |
| 4 | no supported action but one or more yield `UNKNOWN_ACTION` | `UNKNOWN_ACTION` from the first such clause |
| 5 | otherwise | `NONE`, reason `no_explicit_action_intent` |

Rank 2 before rank 3 is the whole point: there is no preferred-first-action behaviour. "Open VS
Code and deploy production." must not quietly become `OPEN_APP`.

## 3. What a multi-action result looks like

`primary_action = MULTI_ACTION_UNSUPPORTED`, `target = None`, `raw_target = None`,
`target_resolved = False`, `capability_available = False`, `selected_clause = None`.

`detected_actions` carries the tuple of supported actions that were found, for audit and for the
later limitation message. It is deliberately a tuple of `PrimaryAction` members with no targets,
no arguments and no tools: nothing downstream can execute from it, and the one field a dispatcher
would read — `primary_action` — says `MULTI_ACTION_UNSUPPORTED`. A test asserts that every
multi-action result has an inert `primary_action` and an empty target.

## 4. Action-bearing request classes

Four of the nine classes can carry an executable action:

```
ACTION_REQUEST   CONFIRMATION_SENSITIVE_ACTION   AMBIGUOUS_ACTION   STATUS_CHECK_REQUEST
```

Five cannot, and short-circuit to `PrimaryAction.NONE` before any lexical extraction runs:

```
VALUE_QUERY   GENERAL_EXPLANATION   DECLARATIVE_FACT   MISSING_CONTEXT_QUERY   OTHER
```

Each is required by the task boundary and by the contract: a declarative statement supplying a
value is not an act (§16.1, §10.2 — a correction changes the supplied value and **must not** be
rendered as a change to the world); a definitional question is conversational (§4.1); a value
query is answered from provenance, not by a tool; a missing-context query has nothing to act on;
and `OTHER` is reached only when no higher-precedence classifier rule fired.

**This is not an assumption.** All 67 rows of the frozen C4 regression corpus were labelled with
the sealed 13B11G classifier before this router existed, and the cross-tabulation is clean: every
row whose frozen expected action is non-`NONE` sits on an action-bearing class, and every row on
a non-action-bearing class expects `NONE`. Zero conflicts. The table is in `ROUTER_CORPUS.md` §3.

### The cost, stated

Short-circuiting is fail-closed but not free. "Anyway, open VS Code" classifies `OTHER` — its
leading clause is "anyway" — so the router returns `NONE` and the open is not routed. The
alternative, letting the router extract an action the classifier said was not there, would make
the router a second classifier and would let a request that failed every classifier action rule
still reach a dispatcher. A missed action costs a clarification; an unintended action costs an
action. This is a documented limitation, exercised by a test, not a silent one.

## 5. Supported action plus unsupported action

"Open VS Code and restart the server" yields one supported action and one `UNKNOWN_ACTION`. Rank 3
applies: `OPEN_APP`. §8.1 governs two or more *executable* actions, and an `UNKNOWN_ACTION` has no
authorized tool, so it is not executable — nothing is silently partially executed. The unsupported
clause is still visible in `clause_analysis`. Asserted by test.

## 6. Repeated same action

"Open VS Code and then open it." yields two supported `OPEN_APP` clauses and is therefore
`MULTI_ACTION_UNSUPPORTED` under rank 2. No pronoun is resolved, no deduplication is attempted and
no plan is built: deciding that the second "open it" means the same application as the first would
be exactly the coreference guess §17.1 forbids. Refusing is the conservative reading and requires
no planning engine.

## 7. Negated and reporting clauses never count

A clause opening with a negation or a reporting marker is classified before its verb is ever
examined (`CONNECTOR_GRAMMAR.md` §2), so neither can contribute an action to the count.
"Production is the target; tell me what that means, don't deploy." contains the word *deploy*
twice and routes `NONE`.
