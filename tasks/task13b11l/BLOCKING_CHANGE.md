# The Exact Upstream Change Required — Task 13B11L

This is what must land before P6 can be implemented. It is an **upstream P3 change** and this
task deliberately did not make it: task §32 says *"DO NOT modify classifier/router in this
task."*

---

## 1. The change

`app/execution/classifier.py::ACTION_VERBS` must cover every verb
`app/execution/router.py::UNSUPPORTED_VERBS` declares, so that an explicitly requested operation
with no authorized tool is action-bearing and reaches the router's own verdict.

The twenty verbs to add — the exact set difference
`UNSUPPORTED_VERBS − (ACTION_VERBS ∪ STATUS_VERBS)`:

```
backup  build   clear   commit  download  fix     flush   merge   modify  patch
pull    reset   restore revert  roll      rollback rotate scale   upgrade upload
```

## 2. Verified sufficient, read-only

`ACTION_VERBS` was rebound in a throwaway process — no file written, no commit, the binding
restored and asserted — and the full chain re-measured (evidence `06-fix-simulation.txt`):

| | before | after |
|---|---|---|
| unsupported verbs reaching `UNKNOWN_ACTION` + `OPERATIONAL` | 21 / 41 | **41 / 41** |
| conversational probes still `CONVERSATIONAL` | 8 / 8 | **8 / 8** |
| control prompts unchanged (`open vscode`, `delete /tmp/old-build`, `deploy to staging`, `check the database status`, `the api port is 8080`, `is the database up`, `open it`, `restart the api service`) | — | **8 / 8 unchanged** |
| prompts whose structured state changes | — | exactly the 20, all `OTHER/NONE/CONVERSATIONAL` → `ACTION_REQUEST/UNKNOWN_ACTION/OPERATIONAL` |

The chain then satisfies §13.1 without any P6 involvement: `ACTION_REQUEST` is in
`ALWAYS_OPERATIONAL_CLASSES`, so the lane is `OPERATIONAL`; the router returns
`UNKNOWN_ACTION` with `REQUESTED_OPERATION_HAS_NO_AVAILABLE_TOOL`; and the obligation engine
selects `REPORT_CAPABILITY_UNAVAILABLE` at rank 6 from state it already has.

## 3. The operator decision this needs

Adding a verb to `ACTION_VERBS` makes the request action-bearing. Adding it *also* to
`SENSITIVE_ACTION_VERBS` makes it `CONFIRMATION_SENSITIVE_ACTION` instead of `ACTION_REQUEST`.
Both reach `REPORT_CAPABILITY_UNAVAILABLE` today, because no tool exists for any of them — so
the choice does not change today's answer. It changes the answer the day a tool *is* added, and
it is the same shape of decision as the 13B11I permission matrix sign-off (D-01…D-10).

None of the twenty is currently in `SENSITIVE_ACTION_VERBS`. Recommended split, for the operator
to confirm or overrule:

| Recommended sensitive | Rationale |
|---|---|
| `rollback`, `revert`, `reset`, `restore`, `clear`, `flush`, `patch`, `merge`, `upgrade` | state-changing or destructive the moment a tool exists; a wrong one is expensive to undo |
| `backup`, `build`, `commit`, `download`, `fix`, `modify`, `pull`, `roll`, `rotate`, `scale`, `upload` | not inherently destructive; ordinary action requests |

`roll` deserves a note: it is in the router's list as a prefix guard for "roll back", and as a
bare verb it is close to meaningless. Consider whether it belongs in either lexicon at all.

## 4. Scope of the unblocking task

Small, but it touches a sealed module, so it needs the standing method:

1. freeze and hash the new lexicon and the expected class/route/lane outcome for all 41 verbs
   **before** editing `classifier.py`;
2. make the one-frozenset change (plus `SENSITIVE_ACTION_VERBS` per the operator's answer);
3. re-run the sealed 13B11G classifier tests, the 13B11H router tests and the lane tests —
   expect movement only in the twenty rows, and assert the other rows byte-identical;
4. re-run `pytest`, the golden (must stay 12/20, same eight IDs) and the legacy probe (must stay
   `fc68a0b0…`);
5. re-verify that nothing else under `app/` changed.

`router.py` needs no change at all. Nothing in P4 or P5 is affected: permissions key on
capability, and `UNKNOWN_ACTION` is already non-dispatchable at both the confirmation layer
(`NON_CONFIRMABLE_ACTIONS`) and the dispatcher (`NON_DISPATCHABLE_ACTIONS`).

## 5. Alternatives considered and rejected

| Alternative | Why not |
|---|---|
| Make the router the single lexicon authority and have the classifier consult it | correct in the long run, but it modifies two sealed modules and inverts a dependency the router's own design comment relies on. Larger blast radius for the same outcome |
| Add a distinguishing `ClassificationReason` (e.g. `UNRECOGNISED_OPERATION`) while leaving the class `OTHER` | still requires a classifier lexicon change to detect the verb, *and* a lane-policy change so `OTHER` + that reason becomes operational. Two sealed modules instead of one |
| Let P6 treat `OTHER` as capability-unavailable | answers "thanks" with a refusal. Rejected in `P3_RECONCILIATION.md` §4 |
| Let P6 parse the request text | forbidden by task §12 and contract §15.3 |
