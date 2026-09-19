# Task 13B11H — Traceability

Each row: what was built → the contract clause that requires it → the routing concept it realises
→ the invariant it protects → the future consumer that will read it.

## 1. Artifact → clause

| Artifact | Contract clause | Realises | Invariant | Future consumer |
|---|---|---|---|---|
| `route()` producing one `RouteResult` per request | §5.2 (NORMATIVE) — routing MUST produce `PRIMARY_ACTION`, `REPORTING_INTENT`, `TARGET`, `MULTI_ACTION`, `CAPABILITY` | all eight `PrimaryAction` members | INV-015 (no real action from prose alone) — the action comes from a deterministic parse, never from model text | P4 permission engine; P5 dispatcher |
| clause segmentation before action selection | §5.3 — a compound request MUST be segmented deterministically so a reporting or conditional clause cannot displace the action clause | `clauses`, `clause_analysis` | INV-017 (a reporting clause never authorizes an additional action) | P6 obligation engine; CT-017 |
| frozen lexicon and grammar as module data | §5.3 — segmentation and the action lexicon MUST be data, versioned and auditable, not model inference and not benchmark-specific string matching | `ROUTER_VERSION`, `RouteReason` | reproducibility on replay (P3 exit criterion) | P11 A/B and readiness |
| `ReportingIntent` extracted by a separate pass | §7.1 — reporting intent is non-executable metadata; §7.2 — one `OPEN_APP` with `REPORT_SUCCESS`, never two actions | all six `ReportingIntent` members | INV-017 | P6 obligation; P7 response builder |
| `target` + `raw_target`, never canonicalized | §9.1 — retain raw arguments verbatim, record canonical separately, no fuzzy matching, no guessing | target with resolution state | INV-006 (raw and canonical both auditable) | P3 canonicalizer, composed after routing; P1 audit |
| `target_resolved = False`, operand kept | §17.1 — MUST NOT dispatch and MUST NOT invent a target when one is missing or unresolved | `AMBIGUOUS` routes | INV-005 (ambiguous required targets cannot be invented) | P5 dispatcher (CT-005); P6 `REQUEST_TARGET` |
| `MULTI_ACTION_UNSUPPORTED` at rank 2 | §8.1 — two or more distinct executable actions MUST NOT be silently partially executed; the control plane MUST dispatch nothing | `multi_action`, `detected_actions` | INV-012 | P6 `REPORT_MULTI_ACTION_LIMIT` (CT-009) |
| `UNKNOWN_ACTION` with no substitution | §13.1 — no authorized tool means `UNKNOWN_ACTION` and `REPORT_CAPABILITY_UNAVAILABLE`; §13.2 — no nearest-tool substitution | 41 named unsupported verbs | INV-011 (unsupported actions cannot be silently mapped to unrelated tools) | P4 capability; P6 `REPORT_CAPABILITY_UNAVAILABLE` |
| `capability_available` from a caller projection | §5.2 `CAPABILITY` — whether an authorized tool exists | boolean, never a tool name | INV-011 | P4 permission engine; P5 dispatcher |
| classifier class respected, never recomputed | §5.1 — the class is derived once, deterministically, before response construction | `ACTION_BEARING_CLASSES` | INV-018 / INV-009 depend on one class per turn, not two | the whole P7 pipeline |
| `RouterError`, no fallback route | §3 fail-closed | none — an error is not a route | malformed input cannot reach a dispatcher | every caller |

## 2. Boundary traces the task specification asked for

| Requirement | Where it lands |
|---|---|
| primary-action extraction → deterministic control-plane ownership | §2 lists `action_routing` as a control-plane responsibility. Gap **G-03** records that today's router emits `suggested_tool` rather than a primary action and never segments, *"so the C3 failure mode (reporting clause displaces the action) is structurally present."* This closes it additively; `app/brain/router.py` is byte-identical. |
| reporting-intent separation → reporting clauses non-executable | Gap **G-04** — "No representation" — is closed. §7.3 records J04/J05/J06 at 0/5 before segmentation and 5/5 after; all three are in the regression corpus and all three pass. |
| target preservation → INV-005 / no invention | Gap **G-05**: `extract_app_name` "returns whatever remains after stripping verbs, so 'open it' yields the literal target `it`" with no notion of unresolved. Here `"Open it."` yields `OPEN_APP` with `target="it"` and `target_resolved=False`. Gap **G-25** — no `REQUEST_TARGET` path — is prepared. |
| raw/canonical boundary → INV-006 | `raw_target` and `target` are both the user's words; `canonicalize()` is proven uncalled by monkeypatch. The alias the canonicalizer knows is demonstrably not applied. |
| unsupported action → INV-011 | 41 verbs each named explicitly and each tested; no near-miss verb reaches a supported action. |
| multi-action block → INV-012 | Gap **G-06** — "No segmentation; one tool is selected and run" — is closed. All 25 ordered pairs of the five supported actions are tested; none selects a first action. |

## 3. Conformance tests this phase prepares

`IMPLEMENTATION_PHASES.md` lists CT-005, CT-009, CT-016 and CT-017 as P3's conformance set. With
the classifier (13B11G) and the router (this task) both in place, three of the four now have their
full deterministic input; none can execute end to end until the dispatcher exists.

| Test | What P3 now supplies |
|---|---|
| CT-005 — ambiguous target prevents dispatch | `AMBIGUOUS_ACTION` from the classifier and `target_resolved=False` from the router |
| CT-009 — multi-action does not silently partially execute | `MULTI_ACTION_UNSUPPORTED` with an empty target and `capability_available=False` |
| CT-016 — the lane decision is deterministic | the classifier's `RequestClass`, which the lane policy already consumes |
| CT-017 — a reporting clause never adds an action | the leading-clause cut plus the separate reporting pass |

## 4. P3 is now structurally complete

| Component | Task | Production commit |
|---|---|---|
| canonicalizer | 13B11E | `e7432431` |
| lane policy | 13B11F | `a69f33e0` |
| request classifier | 13B11G | `d4eb171d` |
| action router | 13B11H | `03cab496` |

All four are pure, passive and unwired. `DEPENDENCY_GRAPH.md` line 64 places permissions (P4)
next.

## 5. Deferred operator decisions — untouched

`lane` is still not one of the 17 contract audit fields; the redaction secret-key list was not
introduced; `ProvenanceSource` still has exactly 8 members with no `TIMEOUT`. Schema version is
still 3. Asserted by test and printed in `13-static-review-and-hermes-non-use.txt` §7.
