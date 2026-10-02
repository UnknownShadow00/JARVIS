# Pipeline-absence inventory

Scanned all production Python assertions (excluding venv/git/cache), prior sealed evidence text, and historical workspace task records. Machine inventory records each matching occurrence with path, line, source SHA-256, classification and treatment. Candidate evidence/doc occurrences are conservatively retained, including repeated quotations; counts are occurrences, not independent tests.

| Class | Count | Treatment |
|---|---:|---|
| A historical evidence/checks | 133 | Never edit or re-purpose old verification scripts against post-implementation production; they verify the original snapshot. |
| B production assertion to transition | 1 | Only tests/execution/hermes_adapter_non_activation_test.py line 55, in test_p7_pipeline_and_runtime_activation_remain_absent. Exact replacement frozen in PIPELINE_GATE_TRANSITION.md. |
| C historical documentation references | 71 | Do not rewrite history. R4 versions the prospective gate; future implementation records absent-at-entry → present-at-exit. |

The all-production assertion scan also records unrelated voice pipeline assertions so the exclusion is reviewable. Only the canonical P7 file-existence assertion is class B. No second canonical absence assertion was found. Current R4 entry/exit and freeze checks continue to require absence and are added historical evidence, never tests to weaken.
