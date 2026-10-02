> **DRAFT — NOT FROZEN. P-B04 blocks completion; see BLOCKER_ANALYSIS.md. This file does not authorize implementation.**

# V1 to V2 — explicit repair history

V1 remains frozen historical evidence. It was later proven unimplementable because field 15 exposed ConfirmationRecord across the sealed P4 boundary. R2 stopped before creating pipeline.py. No V1 file, test or digest is rewritten or deleted.

V2 supersedes only the confirmation admission representation and references necessary to consume it. Field name `confirmation` remains; its type becomes SettledConfirmationProjection | None. Exact type identity is preserved with the new class. All other twenty RecordedTurn fields, three modes, closed stop reasons, result replay and expected matrix outcomes remain binding from V1. CONFIRMATION_PROJECTION.md and S08_V2.md replace the V1 lifecycle-reference mechanics; they do not grant authority.

V1's prospective audit discussion is not authorization to import lifecycle helpers or to carry whole records into P7. V2's mode-B internal diagnostic projection can expose only the admitted sixteen facts. Lifecycle version, full owner audit payload and other owner-only data stay outside P7; live audit serialization is still deferred. No fixture outcome or audit schema changes.

P-B03 is independently resolved by freezing exact future path/symbol exceptions in TEST_CHANGE_INVENTORY.md. No production test changes occur in this task. The operator's authorization applies only to those entries in the next implementation task. Additional required changes must stop for authorization.
