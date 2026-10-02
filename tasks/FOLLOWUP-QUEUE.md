# Autonomous session follow-up queue
Production checkpoint: db54d615c3ee023d753e86143860c4efdc251230. Adapter foundation complete; full P7 not complete. No item below authorizes a policy/runtime change.

## BLOCKING

| ID | Next action | Current behavior / decision boundary |
|---|---|---|
| P7-PIPELINE-01 | Freeze passive pipeline input and TurnOutcome contract | Neither type nor pipeline exists; proposed draft is NOT FROZEN |
| P7-GUARD-01 | Freeze route/capability/tool/argument binding and multiple-proposal disposition | P4's OPEN_APP/apps.open and OPEN_URL/browser.open maps exist; no new capability may be inferred from model descriptors |
| P7-PROJECTION-01 | Assign exact source and identity checks for all stage projections | Current modules consume separate typed state; model cannot supply satisfied constraints, confirmation or provenance |
| P7-LANE-01 | Freeze final lane timing with proposal/result signals | Deterministic policy exists; pipeline stage assembly absent; never downgrade operational state |
| P7-FAILURE-01 | Freeze per-stage failure matrix and typed outcome | Safe conceptual behavior exists; fallback may not manufacture approval or result truth |
| P7-AUDIT-01 | Specify event projections and existing ModelDraftAuditRef construction | Reuse safe digest/reference; separate construction from emission; no full provider envelope |
| DEP-P8-01 | Keep P8 gated on full P7 exit | P7 requires pipeline and measured live shadow; only preparation is eligible now |

Recommended resolution: dedicated pipeline contract freeze against existing modules and the R3 draft/test matrix. Routine naming need not become a policy decision; guard, state ownership, constraint discharge and final response authority require explicit architectural agreement. No live activity is necessary to review that contract.

## SECURITY

| ID | Question / current behavior | Options and security consequence |
|---|---|---|
| VERIFY-AUDIT-01 | Vulnerability/type/lint/coverage tooling unavailable; pip audit attempted, pip check passed | Arrange approved tooling later; do not claim a clean vulnerability scan or install ad hoc into production |
| P7-REASONING-01 | P7 rejects reasoning/thinking in addition to P1's existing normalized names | Freeze future audit projection; excluding at source is preferred to expanding retention; no casual P1 policy change |
| D-01 | Existing browser.open/browser.search policy tension | Preserve current frozen outcomes pending operator choice; resolving it may alter browser authority |
| CONF-TTL | Confirmation numeric TTL remains deferred | Choose operator-approved values later or keep explicit test expiry only; freshness affects permission to execute |
| CONF-UX | Confirmation user experience remains deferred | Keep current behavior; redesign only with explicit approval, because approval binding must remain clear |
| P5-TIMEOUT | Timeout confirmation lifecycle remains EXECUTING | Preserve it; later decide recovery/settlement with evidence and no implicit success/retry |

## BEFORE LIVE WIRING

| ID | Question / current behavior | Required boundary |
|---|---|---|
| P7-LIVE-01 | Actual Hermes wire normalization unspecified | Separate transport fixtures and operator-approved live task; requested model/IDs/time remain caller-owned |
| P7-SHADOW-01 | No live shadow/server consumer | Define measured window, side-effect isolation, resource ownership and rollback; never enable from a draft |
| REGISTRY-01 | Real registry adapter deferred to P9 | Requires P8 exit and operator approval; no real tool execution now |
| CAPABILITY-01 | Live capability projection absent | D-08: abstract vocabulary/advertised schemas are not live grants |
| REQUEST-WIRING-01 | Server remains legacy | Explicit future integration task only; no live routing in this session |
| AUDIT-LANE | Lane audit-field evolution deferred | Preserve current schema; review exact consumer needs before changing |
| AUDIT-REDACTION | Secret-key list deferred | Do not expand retention or weaken redaction without reviewed policy |
| PROV-TIMEOUT | TIMEOUT ProvenanceSource deferred | Keep current uncertainty behavior; do not recast timeout as success |

Destructive, financial, external-messaging, actual capability grants, migrations, network/machine configuration and model replacement remain separate operator decisions if later work requires them. This session introduced none.

## LATER HARDENING

| ID | Follow-up | Current result |
|---|---|---|
| P7-LIMITS-01 | Measure and freeze parsing resource budgets | No arbitrary prompt/proposal/depth limit invented |
| EVIDENCE-AGGREGATE | Document historical classifier R1/R2 aggregate-digest formula | Their file manifests verify; undocumented aggregate formula remains unresolved |
| P7-DOC-01 | Correct stale future-phase/no-import comments in a scoped change | No production comment churn during preparatory work |
| D-P6-01 | Preserve DENY mapping until separately reviewed | REPORT_CAPABILITY_UNAVAILABLE, reason permission_denied |
| D-P6-02 | Preserve TIMEOUT mapping until separately reviewed | REPORT_TOOL_ERROR, reason trusted_tool_timeout |

Detailed questions, alternatives, recommendations and affected dependencies are in task13b11n-r3/FOLLOWUPS.md. Proposed contracts are not frozen and grant no permissions.

## Task 13B11O resolution status — 2026-09-22

P7 contract freeze remains BLOCKED. The detailed review at `task13b11o/FOLLOWUPS.md` narrows the current operator questions to O-B01 (authoritative proposal/tool/argument guard), O-B02 (zero/multiple/mismatched proposal disposition), O-B03 (typed failed-turn/fallback authority), and O-B04 (conversational turn.summary requires an obligation that P6 correctly does not produce). R3's proposals remain unfrozen; no policy or schema changed.

All other deferred items above are preserved. A supported-read end-to-end row cannot be claimed using the current routed vocabulary; keep that gap explicit rather than adding a live grant. Next step is resolving and re-freezing the passive pipeline contract, not implementation, live shadow, P8 or Task 13C.

## Task 13B11O-R1 decision freeze — 2026-09-22

Operator decisions P7-D01–D04 resolve O-B01–O-B04 for the passive recorded/static boundary. P7 PIPELINE CONTRACT V1 is now frozen in task13b11o-r1/; the original blocked documents remain unchanged. Next task is P7 PASSIVE PIPELINE IMPLEMENTATION, not live wiring.

Exact remaining prerequisites: F-TYPE-01 implements the contracted PipelineStop in that next task; F-MAP-01 blocks deriving/executing from an unfrozen production tool/argument binder, but not pure comparison with explicit static caller projections; F-FALLBACK-01 is before live responses/failure audit; F-AUDIT-01 conditionally fixes conversational summary obligation validation before live audit wiring. No fake obligation, guessed capability, schema patch or permission-policy change was made. All prior live/hardening deferrals remain preserved; see task13b11o-r1/FOLLOWUPS.md.

## Task 13B11P entry/API gate — 2026-09-22

P7 passive pipeline implementation is BLOCKED before coding under task §5. The canonical module path and four operator decisions remain resolved. P-B01 in task13b11p/FOLLOWUPS.md requests the exact whole-turn passive admission signature/input variants, particularly S08–S09 confirmation/result replay evidence versus a later isolated P5 continuation seam. The guard-only schema and PipelineStop do not by themselves supply that aggregate boundary. Do not implicitly promote the original NOT FROZEN whole-turn input proposal or infer confirmation from a record. Production remains db54d615c3ee023d753e86143860c4efdc251230; no pipeline module/commit. Resolve this interface boundary before resuming the same task. Existing before-live/hardening items remain unchanged; no P8/13C or live work.

## Task 13B11P-R1 admission contract freeze — 2026-10-02

P-B01 is RESOLVED. RECORDED-TURN ADMISSION CONTRACT V1 is frozen in `task13b11p-r1/` (18 manifest entries, manifest `203eedc6c55b2e68c3697453e0d3d0bde2556e5578ce1cfec9ad41e0998e3919`), additive to and subordinate to the unchanged P7 PIPELINE CONTRACT V1. Option 1 of `task13b11p/FOLLOWUPS.md` was taken: a recorded-only callable `run_recorded_turn(turn: RecordedTurn) -> TurnOutcome` over existing typed projections, with all replay evidence generated outside it. Option 2 — an isolated P5 continuation seam inside P7 — was explicitly not taken, and the blocked `task13b11p/` documents remain unchanged.

The design decision that makes the rest follow: `RecordedTurn` carries no callable, store, clock, executor, dispatcher, session object or authority boolean, so the zero-execution invariants are structural rather than checked. Three admission shapes are derived from three presence booleans and never declared; confirmation continuation admits `PENDING` only and has no edge to S09; result replay skips the dispatcher and resumes at S10; `confirmation_claimed` is derived from `result.executed` plus the invocation's outcome, because dispatcher gate 5 can leave a `confirmation_id` present with nothing claimed. An authorized turn with no admitted result stops at `S09_RESULT` — reachable with the real frozen policy, since `browser.open` is a genuine `ALLOW` row under `BALANCED`.

No new stop reason or stage was added: all seven named failure categories map onto the already-closed `PipelineStopReason` set. New bounded follow-ups: F-P7R1-01 (a `TrustedToolResult`'s dispatcher origin is unprovable from type identity; before live wiring), F-P7R1-02 (replay of a non-dispatchable-action refusal result excluded in v1), F-P7R1-03 (admission failure reasons are coarse; guard identity is asserted in tests). F-TYPE-01 is now fully specified for both `PipelineStop` and `RecordedTurn`. F-MAP-01, F-FALLBACK-01, F-AUDIT-01 and F-REPLAY-01 remain exactly as before, and every prior live/hardening deferral is preserved. Next task is P7 PASSIVE PIPELINE IMPLEMENTATION against the 32-row matrix `6b454b2c8d881327b88cef73ae03a6465286bb7fb589e942f1bc3789d76fb434`; no live wiring, P8 or Task 13C.

## Task 13B11P-R2 implementation gate — 2026-10-02

P7 passive pipeline implementation is BLOCKED before coding under task §46. Canonical module identity is resolved and unambiguous: `app/execution/pipeline.py` (`tasks/task13b11a/TARGET_COMPONENT_MAP.md:31`, "Integration boundary"), entry `run_recorded_turn(turn: RecordedTurn) -> TurnOutcome`. §5's block condition does not apply.

**P-B02 (blocking).** Frozen `RecordedTurn` field 15, `confirmation: ConfirmationRecord | None` with exact type identity, is unimplementable: it makes the pipeline the first module under `app/` to import `app/execution/confirmation.py`, against `confirmation_non_activation_test.py::test_no_module_under_app_imports_the_confirmation_machine` (`assert hits == []`, all of `app/`, **no allowlist**), `test_no_public_symbol_is_referenced_anywhere_under_app` (19 symbols, substring match), and `obligations_non_activation_test.py::test_the_confirmation_machine_keeps_its_zero_importers`, whose docstring states the rule normatively — an approval reaches a consumer as a settled projection, the record's lifecycle stays P4-internal. P5 and P6 each paid to preserve it; P6 re-froze a 442-row matrix to do so. No conforming implementation exists (function-local import leaves the substring; `sys.modules` is the service locator 13B11P-R1 §27 forbids; duck typing breaks the frozen type-identity rule and is weaker). This is a defect introduced by 13B11P-R1 and is the same mistake P6 already made and corrected once. Recommended repair: replace field 15 with a JARVIS-owned settled projection built outside the pipeline from `types.py` enums and plain data — all seven B-guards survive restated, the confirmation machine keeps zero importers, and S-14 becomes stronger (absence, not an allowlist). Modes A and C and 23 of 32 matrix rows stand as frozen; nine rows and seven documents need an explicit V2 with new digests. Full field table and the two rejected alternatives in `task13b11p-r2/BLOCKER_ANALYSIS.md`.

**P-B03 (scope authorization).** Any integration boundary needs ~41 non-activation assertion extensions naming the pipeline as a passive importer: `router` ~12, `permissions` ~15, `obligations` ~12 (extending the existing `response.py` allowlist), `response` ~2. Authorized *in kind* by frozen 13B11O-R1 `IMPLEMENTATION_ACCEPTANCE.md` and precedented exactly by the obligation engine naming `response.py`; weakens nothing in substance (no live wiring, no request-path call site, `registry.call` stays at 4 sites in `app/server.py`). Never quantified by a frozen document before now; needs explicit operator authorization of the scope. `dispatch_non_activation_test.py` needs **no** change — the dispatcher keeps zero importers permanently because `obligations.NON_ACTION_OUTCOMES` is the identical three-member set the pipeline needs for guard C-00a.

No fixture corpus was frozen, deliberately: §44 requires the freeze before code, and freezing against an unresolved input field would require re-freezing — the failure §44 exists to prevent. No matrix row measured, no generalization corpus, no conformance claimed. Production remains `db54d615c3ee023d753e86143860c4efdc251230` with an empty diff and `pipeline.py` absent. F-P7R1-01/02/03, F-TYPE-01, F-MAP-01, F-FALLBACK-01, F-AUDIT-01, F-REPLAY-01 and every prior deferral unchanged; FUTURE-AGENT-BRIDGE preserved, not implemented. Nightly snapshot job inspected read-only and not modified. Resolve P-B02, authorize P-B03, land admission contract V2, then resume this same unit. No P8, no 13C, no live work.
