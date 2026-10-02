# P-B04 — RESOLVED by operator authorization in Task 13B11P-R4

The operator explicitly authorizes the canonical app/execution/pipeline.py to become the first and only passive production consumer of app/brain/hermes_adapter.py during the next implementation task. It also explicitly authorizes the historical pipeline-absence assertion to transition to presence plus non-activation. Neither transition is applied now.

R3 correctly stopped because both sites were outside its four-suite authorization. R4 resolves that authorization gap. Exact source: tests/execution/hermes_adapter_non_activation_test.py, SHA-256 28c2c99387c7a9ea20dd7b4426c7c484924b2757758afa7fd0cbfc29f15769c1. The two sites and replacement obligations are frozen separately in ADAPTER_TEST_CHANGE_INVENTORY.md and PIPELINE_GATE_TRANSITION.md.

P-B02's settled projection and P-B03's eighteen-instance inventory remain as previously approved. No confirmation or dispatcher test exception. P-B04 is closed, not conditional on live use. However, final Admission V2 and corpus freeze are withheld for the separate P-B05 guard-order/matrix conflict documented in BLOCKER_ANALYSIS.md. This authorization record does not authorize proceeding past that contract blocker.
