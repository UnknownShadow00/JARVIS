# Independent guard trace

Final 116/116; zero unexplained divergence. matrix-results.json records each fixture/source row, expected/actual stage, guard, reason, obligation, approved-response presence and full downstream output. guard-trace-final.json retains owner call/return events and state.

The final harness does not copy an expected guard into an observed success. It spies actual first-stop arguments, mode and guard returns, actual classify/route/explain/parser/permission calls, P6 selection and response, and audit applicability. Successful C paths prove _result_guard returned None before _render; waiting paths prove actual REQUIRE_CONFIRMATION, valid B projection where present and zero S09 entry. Owner-derived completed P6 labels are compared via an explicit semantic alias table against frozen descriptive labels. Every frozen expected_obligation_state is checked in full. Output fields/text/owner reason/priority checked; template names are contract descriptors, while exact rendered text/source is observed.

Whole-turn traces verify classify -> route -> initial lane -> parser -> final lane; proposal before permission; result association before P6; pre-result stops have no derive/build. Option A verifies Mode C, actual NONE and parsed zero, then no result admission/P6. Positive cardinality verifies NONE and actual nonzero.

First enhanced trace run 115/116 exposed a test-harness implementation omission: N14's declared owner-boundary failure injects a wrong parsed proposal ID. Actual first stop was correctly proposal association, matching stage/reason. Added that independently documented equivalence to the new harness; unchanged source and R6 expectations then passed 116/116. This was not a semantic contract defect or a production change.
