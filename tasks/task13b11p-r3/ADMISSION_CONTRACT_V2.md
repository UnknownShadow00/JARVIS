> **DRAFT — NOT FROZEN. P-B04 blocks completion; see BLOCKER_ANALYSIS.md. This file does not authorize implementation.**

# P7 RECORDED-TURN ADMISSION CONTRACT V2

Explicit successor to the frozen but unimplementable Admission Contract V1. The governing pipeline remains P7 PIPELINE CONTRACT V1 (tasks/task13b11o-r1). This V2 repairs P-B02 and freezes the exact future P-B03 authorization. Contract only; production pipeline remains absent.

Normative files: RECORDED_TURN_V2.md; CONFIRMATION_PROJECTION.md; PROJECTION_FIELD_INVENTORY.md; S08_V2.md; S09_UNCHANGED.md; V1_TO_V2.md; MATRIX_MIGRATION.md; admission-matrix-v2.json; row-mapping.json; NON_ACTIVATION_TEST_AUTHORIZATION.md; TEST_CHANGE_INVENTORY.md; test-change-inventory.json; SECURITY_INVARIANTS.md; IMPLEMENTATION_ACCEPTANCE.md; DEFERRED.md; FOLLOWUPS.md. At a future authorized freeze, CONTRACT-ARTIFACTS.sha256 must seal these and this document, with FREEZE_RECORD.md recording its digest. R3 instead records DRAFT-ARTIFACTS.sha256 because P-B04 blocks freeze; no fixture artifacts were frozen.

Unchanged V1 admission, association, idempotence and failure rules remain binding wherever V2 does not explicitly replace confirmation-specific mechanics. S08 consumes only the settled immutable projection. S09 admits existing recorded results and never invokes a dispatcher. No code, production tests, policy, enum, live wiring or execution dependency is introduced.

No freeze has occurred in R3; the following discipline applies only after a future authorized freeze: no silent edits after freeze. Any discovered contract defect requires explicit new version history, fresh digests and evidence. Unrelated row movement requires STOP. An implementation disagreement must not be hidden by editing fixtures or expectations.
