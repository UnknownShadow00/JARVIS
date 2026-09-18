# Type Map — production artifact → contract clause → invariant → future consumer

Every artifact added by Task 13B11B, why the contract requires it, and which phase consumes it.
Contract references are to `JARVIS_AGENT_EXECUTION_CONTRACT.md` / `agent-execution-contract.yaml`
(commit `5dd853e2…`).

## 1. Enums

| Artifact | Contract clause | Invariant | First consumer |
|---|---|---|---|
| `ExecutionMode` | integration plan §19 (flag model) | — (operational safety of the rollout) | P7 pipeline seam |
| `ACTIVE_EXECUTION_MODES` | integration plan §19 rule 2 | — | P7 seam check |
| `Lane` | §4 response lanes | INV-016 | P3 `lane.py` |
| `RequestClass` | §5.1 request classes | INV-016 | P3 `classifier.py` |
| `PrimaryAction` | §5.2 action outcomes | INV-011, INV-012 | P3 `router.py` |
| `ReportingIntent` | §5.2 reporting intents | INV-017 | P3 `router.py` |
| `PermissionClass` | §11 permission classes | INV-013, INV-014 | P4 `permissions.py` |
| `PermissionOutcome` | §11 permission rules | INV-013 | P4 `permissions.py` |
| `ProvenanceSource` | §9.3 provenance sources | INV-002, INV-003, INV-008 | P2 `provenance.py` |
| `TrustClass` | §9.3, §16 attribution | INV-008 | P2 `provenance.py` |
| `ProvenanceStatus` | §10 supersession | INV-007, INV-019 | P2 `provenance.py` |
| `ToolResultStatus` | §18 tool result trust | INV-003 | P5 `dispatch.py` |
| `ResponseObligation` | §14 obligations | INV-009 | P6 `obligations.py` |
| `OBLIGATION_PRIORITY` | §14 frozen priority order | INV-009, INV-018 | P6 `obligations.py` |
| `OperationalResponseSource` | §15 allowed sources | INV-001, INV-010 | P6 `response.py` |
| `ConversationalResponseSource` | §4 conversational lane | INV-001 | P6 `response.py` |

## 2. Records

| Artifact | Contract clause | Invariant | First consumer |
|---|---|---|---|
| `ModelDraft` | §2.1 model output is untrusted | INV-001, INV-015 | P7 `hermes_adapter.py` |
| `ToolProposal` | §2.1 proposals carry no authority | INV-002, INV-015 | P7 `hermes_adapter.py` |
| `ToolInvocation` | §18.2 invocation binding, §9.1 canonicalization | INV-004, INV-006, INV-013 | P5 `dispatch.py` |
| `TrustedToolResult` | §18 dispatcher-only results, §18.4 minimal result | INV-003, INV-010 | P5 `dispatch.py` |
| `ProvenanceRecord` | §9.3, §10 | INV-002, INV-007, INV-008, INV-019 | P2 `provenance.py` |
| `ObligationDecision` | §14 one obligation per turn, with a reason | INV-009 | P6 `obligations.py` |
| `ApprovedOperationalResponse` | §15, §16 operational output | INV-001, INV-010 | P6 `response.py` |
| `ConversationalResponse` | §4 lane separation | INV-001, INV-016 | P6 `response.py` |
| `to_mapping` | §19 audit fields need one conversion | INV-006 (auditability) | P1 `audit_events.py` |

## 3. Configuration

| Artifact | Contract / plan clause | Behaviour | First consumer |
|---|---|---|---|
| `ExecutionConfig.mode` | plan §19 flag model | parsed, never entered | P7 |
| `ExecutionConfig.shadow_sample_rate` | plan §7 shadow mode | parsed, unused | P7 |
| `ExecutionConfig.hermes_brain` | plan §19 (model swap independent of control plane) | parsed, unused | P7 |
| `normalize_execution_section` | plan §19 rule 1 (fail to known-good) | any problem → legacy + warning | `load_settings` today |
| `execution:` block in `config.yaml` | plan §22 first task | documents the legacy default explicitly | operators |

## 4. Deliberately deferred

| Not implemented | Reason | Phase |
|---|---|---|
| Constructor restriction on `TrustedToolResult` | needs the dispatcher module that owns it | P5 |
| Obligation → source consistency table | selection policy, not vocabulary | P6 |
| Permission matrix data (`config/permissions.yaml`) | requires the operator decision recorded in `PERMISSION_MATRIX_PLAN.md` | P4 |
| Canonicalization rule set and version registry | belongs with the canonicalizer | P3 |
| Audit field schema and event names | belongs with the audit vocabulary | P1 |
| A type per obligation family, per permission class, or a generic `Trusted[T]` | ceremony without a distinct failure mode (plan §6) | never |
