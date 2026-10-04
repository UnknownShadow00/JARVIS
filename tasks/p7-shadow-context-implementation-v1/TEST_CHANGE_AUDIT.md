# Exactly one pre-existing semantic transition

Entry inventory: 361 tracked production-repository files. Compare current hashes: only pre-existing changed file is `tests/execution/provenance_non_activation_test.py`. AST/source comparison: only changed function is `test_there_are_zero_live_provenance_writes`. The complete edited file is byte-identical to the transition frozen before production code. Every other entry file remains unchanged.

Its assertion block adds the single exact instance-constructor relationship. More than one line is required to constrain enclosing class/initializer, assignment, constructor count and arguments; semantic authorization count remains ONE. All original marker scans and other functions/imports remain unchanged. No other existing-test exception or relaxation exists.

New production file: app/execution/shadow_context.py. New test: tests/execution/shadow_context_test.py (54 cases). No package export was necessary. `test-change-audit.json`, the test diff and staged production diff provide exact proof. The corpus SHA256 is unchanged after its first failing run.
