# Allocation exception without provenance promotion

The authorized existing assertion is in `tests/execution/provenance_non_activation_test.py::test_there_are_zero_live_provenance_writes`. Its marker scan remains unchanged. Its new expected list contains exactly `app/execution/shadow_context.py:LedgerStore(`, additionally constrained by AST to one no-argument construction assigned directly to the named instance initializer.

All other modules and constructor shapes remain rejected. The existing `.record_user_fact(`/`.record_tool_result(` and `ProvenanceLedger(` prohibitions remain. New frozen assertions reject every actual P2 recorder, `_append`, `_supersede_locked`, drop/clear and generic append/update mutation calls inside context. Runtime write traps supplement static syntax, including `_build`. No operational provenance record is created by context.

Actual `LedgerStore.for_session` dictionary insertion is passive empty-ledger association, explicitly required by P2; it is not a trusted record append/update. Allocation and zero-write evidence are separate. A post-code virtual-source review rejected seven constructor/module violations and eleven writer/mutation cases (18 total), without editing production or frozen expectations. This is a targeted review, not a claim against arbitrary hostile Python source transformations.
