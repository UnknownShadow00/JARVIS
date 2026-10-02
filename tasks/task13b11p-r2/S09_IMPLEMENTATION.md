# S09 — specified, not implemented

S09 is **recorded result admission**, never "dispatch now". It is unblocked and ready.

| Mode | S09 behaviour |
|---|---|
| `INITIAL_TURN` | reached *eligible* with an actual `ALLOW` and no admitted result: `STOP(S09_RESULT, result_invalid)`, `executed=False`, `result=None`. The recorded-only core holds no executor, so it stops rather than acquiring one. |
| `CONFIRMATION_CONTINUATION` | unreachable by construction; mode B's only S08 outputs are *waiting* and *stop*. |
| `RESULT_REPLAY` | guards C-01…C-08 in order; pass -> continue to S10 with `ObligationState.result = turn.result`; fail -> `STOP(S09_RESULT, result_invalid)`, result **not** retained. |

C-01 result/invocation identity; C-02 tool and action description agreement; C-03
correlation child; C-04 route agreement; C-05 expected-binding and canonical-argument
agreement; C-06 canonicalization and policy version agreement; C-07 the replayed
permission outcome and class equalling what `permissions.decide` returns for this turn;
C-08 historical support pair linkage and distinctness.

Deliberately **not** re-checked at S09: `status`/`executed`/`facts` consistency. That rule
already belongs to the obligation engine's result-shape contradiction check, and
duplicating it in the pipeline would copy a frozen component's logic. An internally
impossible replayed result therefore surfaces as
`STOP(S11_OBLIGATION, obligation_failed, component_reason=<the existing owner code>)`.

Zero dispatcher entries, zero executor calls, zero new invocations, zero new trusted
results, zero claims — structural, because none of those is reachable from `RecordedTurn`.
