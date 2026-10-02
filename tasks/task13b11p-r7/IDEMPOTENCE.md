# Idempotence observations

C09 evaluates the same immutable RecordedTurn twice and compares equal outputs and unchanged inputs. Runtime sentinel observations report zero new executions, invocations, result creation, claims or external writes on the tested calls. No clock or store participates. This is measured corpus scope; separate unseen generalization was not reached.
