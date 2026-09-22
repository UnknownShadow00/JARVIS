# Traceability
| Acceptance | Evidence file in remote R2 bundle |
|---|---|
| Entry production/types/module absence | entry-state.json |
| Task A freeze and hashes | contract-digests.txt, contract-verification.txt |
| Frozen corpus and original code | pre-score-freeze.txt, source-before-compatibility.py, tests/ |
| Valid, malformed, duplicate, unknown, reasoning, multi-proposal | focused-tests.txt; case-results.json |
| Generalization without rule tuning | generalization-tests.txt; verification-after-commit.json |
| Model non-authority/purity/no consumers | focused-tests.txt; verification-after-commit.json; tests/hermes_adapter_non_activation_test.py |
| Full regression and initial failures | full-pytest.txt, full-pytest-initial.txt |
| Golden/probe | golden.json, golden.txt, legacy-probe.json |
| Critical hashes/Hermes/previous seals | verification-after-commit.json; entry-state.json |
| Exact production diff/commit | production-diff.patch; production-commit.txt |
| Workspace commit | workspace-commit.txt |
| Rollback old tests | parent-non_activation_test.py; parent-router_non_activation_test.py |
| Seal | SHA256SUMS, checked from bundle root |
