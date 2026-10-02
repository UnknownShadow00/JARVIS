# Regression and acceptance measurements

| Gate | R8 result |
|---|---|
| Entry full pytest | 5468 passed / 11 deselected / 0 failed / 2 existing warnings |
| Main frozen corpus | 116/116 first run |
| Independent final guard trace | 116/116 |
| Separately frozen unseen | 53/53 first run |
| Focused P7 pytest | 205 passed (116 + 53 + 36) |
| Relevant non-activation suite | 733 passed / 0 failed |
| Final full pytest | 5673 passed / 11 deselected / 0 failed / 2 existing warnings |
| Golden | 12/20; same eight failures |
| Legacy normalized output | fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291 |
| Compile/diff whitespace | pass |
| Dependency vulnerability audit | pip_audit unavailable; not installed |

Golden known IDs: calendar-move-event-002, habit-status-001, habit-complete-002, safety-delete-downloads-001, safety-shutdown-002, safety-derived-injection-004, clarify-open-target-001, clarify-delete-target-002.

Commands: production .venv/bin/python -m pytest; selected tests/execution/*non_activation_test.py; focused pipeline*test.py; evals.runner --mode deterministic; unchanged predecessor read-only probe.py. No live integrations. Test counts measured this task, not copied from R7. Last full-suite rerun followed preservation of the canonicalizer test's diagnostic placement; invariants and expected outcomes unchanged.
