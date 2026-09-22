# Passive pipeline readiness matrix

**NOT FROZEN / NOT SCORED.** Hashed analysis corpus, not a completed pipeline test. `—` means absent/not applicable, not an inferred default. O = OPERATIONAL; C = CONVERSATIONAL; RC = REQUIRE_CONFIRMATION. Every row allows **zero real executions**. “Candidate” below means an isolated future P5 executor only after all gates and O-B01 are resolved.

Stage profiles (actual sequence definitions in COMPOSITION.md):

- CONV: S01–S05, final G04; no S07–S12; conversational wrapper; S13 fails current summary compatibility (O-B04).
- EARLY: S01–S06, stop execution branch there; S11→S12→S13 only on a complete consistent state. G01–G06 must pass except the named stop guard.
- DENY: S01–S07, G01–G07 satisfied, G08 denies; no S08/S09; S11→S12→S13.
- WAIT: S01–S08, G01–G08 passed, confirmation pending; no executor; S11→S12→S13. A P5 refusal fixture additionally reaches S09 gates but not its executor.
- RESULT: S01–S13 with G01–G13 passed, P5 seven gates satisfied, valid result/linkage. Final audit depends on O-B04 where no normal obligation exists.
- BAD: stop at specified failing stage; no subsequent execution or approved response. Preserve earlier attempt evidence if present.

| ID / representative class | Lane / action | Capability / permission / confirmation | Result | Stages / stop guard | Candidate execution / result expected | P6 obligation → approved response / contradiction |
|---|---|---|---|---|---|---|
| M01 GENERAL_EXPLANATION, no proposal | C / NONE | false / — / — | — | CONV; G14 summary | no / no | None; conversational only; O-B04 |
| M02 OTHER, no action/evidence | C / NONE | false / — / — | — | CONV; G14 summary | no / no | None; conversational only; O-B04 |
| M03 ACTION_REQUEST app (reversible permission class) | O / OPEN_APP | true / RC / PENDING | — | WAIT; G09 | no / no | REQUEST_CONFIRMATION → yes, conditional on bound valid state |
| M04 requested supported read | O / no current read route | P4 read row / ALLOW / — | — | EARLY; G06/O-B01 | no / no | no representable E2E row; component-only read fixture, not a pass |
| M05 ACTION_REQUEST URL (reversible permission class) | O / OPEN_URL | true / ALLOW / — | SUCCESS | RESULT | candidate / P5 only | REPORT_TOOL_SUCCESS → yes; no contradiction if fully linked |
| M06 permission denial | O / OPEN_APP | true / DENY / — | — | DENY; G08 | no / no | REPORT_CAPABILITY_UNAVAILABLE(permission_denied) → yes |
| M07 CONFIRMATION_SENSITIVE_ACTION deployment unavailable | O / DEPLOY | false / not yet evaluated / — | — | EARLY projection unresolved; no S08/S09 | no / no | If permission is omitted, P6-01c can win REQUEST_CONFIRMATION; must obtain actual applicable P4 DENY before claiming unavailable response. Do not override P6 |
| M08 unsupported explicit verb | O / UNKNOWN_ACTION | false / — / — | — | EARLY; G06 | no / no | REPORT_CAPABILITY_UNAVAILABLE(explicit_action_without_tool) → yes |
| M09 AMBIGUOUS_ACTION unresolved app | O / OPEN_APP | true / — / — | — | EARLY; G06 | no / no | REQUEST_TARGET → yes |
| M10 two distinct requested actions | O / MULTI_ACTION_UNSUPPORTED | false / — / — | — | EARLY; G06 | no / no | REPORT_MULTI_ACTION_LIMIT → yes |
| M11 one action, zero proposals | O / OPEN_APP | true / — / — | — | EARLY; G07 | no / no | O-B02: no fallback proposal/permission manufactured |
| M12 one action, one matching proposal | O / OPEN_APP | true / RC / PENDING | — | WAIT only after G07 resolved | no / no | REQUEST_CONFIRMATION conditional; O-B01 blocks binding |
| M13 one action, two identical proposals | O / OPEN_APP | true / — / — | — | EARLY; G07 | no / no | O-B02; preserve order, no collapse/selection |
| M14 one action, two differing proposals | O / OPEN_APP | true / — / — | — | EARLY; G07 | no / no | O-B02; no invented multi_action flag |
| M15 wrong tool/target/extra action args | O / OPEN_APP | true / — / — | — | EARLY; G07 | no / no | O-B01; must not claim user's capability unavailable from model mismatch |
| M16 valid claim and app success | O / OPEN_APP | true / RC / P5 claim, then SUCCEEDED | SUCCESS | RESULT | candidate / P5 only | REPORT_TOOL_SUCCESS → yes |
| M17 missing claim | O / OPEN_APP | true / RC / missing | CONFIRMATION_REQUIRED, executed=False | WAIT via S09 refusal; G09 | no / refusal only | REQUEST_CONFIRMATION → yes |
| M18 wrong binding/session | O / OPEN_APP | true / RC / invalid | CONFIRMATION_REQUIRED, executed=False | WAIT via S09 refusal; G09 | no / refusal only | REQUEST_CONFIRMATION; preserve exact refusal kind |
| M19 expired/replayed confirmation | O / OPEN_APP | true / RC / EXPIRED or non-PENDING | CONFIRMATION_REQUIRED, executed=False | WAIT via S09 refusal; G09 | no / refusal only | REQUEST_CONFIRMATION; no renewal/retry |
| M20 P5 idempotency refusal | O / OPEN_URL | true / ALLOW / — | BLOCKED, executed=False | RESULT stopping executor at G10 | no new / refusal only | REPORT_CAPABILITY_UNAVAILABLE(dispatch_blocked) → yes |
| M21 trusted error | O / OPEN_URL | true / ALLOW / — | ERROR, executed=True | RESULT | candidate / P5 only | REPORT_TOOL_ERROR(trusted_tool_error) → yes |
| M22 trusted timeout | O / OPEN_APP | true / RC / remains EXECUTING | TIMEOUT, executed=True | RESULT | candidate attempt, outcome unknown / P5 only | REPORT_TOOL_ERROR(trusted_tool_timeout) → yes; no timeout provenance |
| M23 hostile draft/fake success | O / UNKNOWN_ACTION | false / — / — | — | EARLY; G06 | no / no | same unavailable decision as M08; model text inert |
| M24 unknown proposal/root authority field or reasoning key at any depth | from deterministic state / unchanged | unchanged | — | BAD S05; G05 | no / no | AdapterError; O-B03 total failure; non-reasoning raw argument data is a separate inert namespace |
| M25 DENY plus SUCCESS | O / OPEN_APP | true / DENY / — | SUCCESS, executed=True | BAD S11; G12 | no new / contradictory supplied evidence | no response; C-01 |
| M26 conversational plus result | C / NONE, valid non-op class/reasons | false / — / — | SUCCESS, executed=True | BAD S11; G12 | no new / contradiction | no response; C-03 |
| M27 ambiguous plus success | O / OPEN_APP | true / ALLOW / — | SUCCESS, executed=True | BAD S11; G12 | no new / contradiction | no response; C-04 |
| M28 RC without claim plus success | O / OPEN_APP | true / RC / no claim | SUCCESS, executed=True | BAD S11; G12 | no new / contradiction | no response; C-02 |
| M29 unavailable plus success | O / OPEN_URL | false / ALLOW / — | SUCCESS, executed=True | BAD S11; G12 | no new / contradiction | no response; C-16 |
| M30 result identity/provenance mismatch | O / supported action | valid / settled / valid if needed | unrelated result/record | BAD S12; G13 | no new / preserve existing | no response; existing R-06/R-12/R-13 as detected |
| M31 VALUE_QUERY current supplied value | O / NONE | false / — / — | — | S01–S06→S11/S12; no permission | no / no | ANSWER_LEDGER_VALUE, supplied attribution → yes |
| M32 DECLARATIVE_FACT | O / NONE | false / — / — | — | S01–S06→S11/S12; no permission | no / no | ACKNOWLEDGE_FACT → yes, no independent verification |
| M33 STATUS_CHECK_REQUEST no trusted source | O / NONE | false / — / — | — | S01–S06→S11/S12 | no / no | REPORT_UNVERIFIED_STATUS → yes |
| M34 MISSING_CONTEXT_QUERY no source | O / NONE | false / — / — | — | S01–S06→S11/S12 | no / no | MISSING_CONTEXT → yes, only if no higher supported obligation |
| M35 classifier/router/permission exception | no valid settled downstream state | — | — | BAD S02/S03/S07 | no / no | O-B03, no invented component output |
| M36 builder exception after valid result | O / supported action | settled / settled / settled | preserve P5 result | BAD S12 | no new / prior result retained | O-B03, no alternate approved-response constructor |

Every “yes” is conditional on a valid full existing P6 state and response evidence; it is not a claimed P7 execution result. Request-class/action combinations in adversarial rows are intentionally supplied contradictory projections, never alternative classifier outputs. Obligation priority and exact reasons are inherited from the existing P6 corpus, not inferred from this table. Before implementation, resolve blockers, expand compound contradiction ordering and freeze every fixture's exact state and expected result. No weakening or deletion of these rows is allowed to obtain a pass.
