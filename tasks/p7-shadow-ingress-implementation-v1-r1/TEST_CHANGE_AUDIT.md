# Exactly ONE pre-existing transition

All entry tracked files were hashed before coding. Only pre-existing changed file: `tests/execution/shadow_context_test.py`. Source/AST comparison identifies only `test_exact_import_graph_and_zero_production_consumers` as changed. The entire resulting file is byte-identical to the authorized version frozen before code.

Every other entry file remains unchanged, including shadow_context.py and the prior provenance constructor gate. No second security/non-activation exception, pipeline structural change or historical sealed expectation rewrite exists.

New test: tests/execution/shadow_ingress_test.py, 64 cases/52 security cases. Frozen unseen corpus: 20 external cases. New production module: app/execution/shadow_ingress.py. Full pytest increases exactly 64, from 5775 to 5839, with 11 deselected and zero failures. No broad consumer allowlist or assertion deletion replaces the old graph; the new structural assertions require the exact graph and retained bans.
