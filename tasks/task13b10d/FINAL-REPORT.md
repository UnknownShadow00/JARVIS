# JARVIS V2 — Task 13B10D Final Report
## Freeze JARVIS Agent Execution Contract — architecture/contract freeze only

## 1. Verdict

**JARVIS AGENT EXECUTION CONTRACT V1 FROZEN**

All freeze prerequisites are established: the C5 checkpoint verifies, the canonical normative
contract is complete, the machine-readable contract parses and validates, the invariant list is
complete, conformance tests are specified, implementation boundaries and traceability are
recorded, the ADR is accepted, known limitations are explicit, the consistency review found zero
unresolved contradictions, production and Hermes are unchanged, the evidence is sealed, and the
workspace commit is clean.

No model inference was run. No production file was touched.

## 2. C5 checkpoint and evidence verification

Workspace checkpoint: HEAD was `b6192a5323d1c0af0e5790b38d8f30029451547b` ("test(13b10c5):
TEST-ONLY deterministic operational utility layer and evidence"), working tree clean, 35 files
tracked under `tasks/task13b10c5/`.

C5 evidence bundle `task13b10c5-operational-utility`:

| Check | Expected | Observed |
|---|---|---|
| Files | 137 | **137** |
| Manifest entries | 136 | **136** |
| `SHA256SUMS` sha256 | `97c20424…4ec456` | **matches** |
| `sha256sum -c SHA256SUMS` | 0 failures | **136 OK, 0 failures** |
| Manifest excludes itself | yes | **yes** (0 self-references) |

The C3 and C4 bundles were re-verified in the C5 task and were not re-opened here. No file in any
prior evidence bundle was modified by this task.

## 3. Production and Hermes freeze proof

| Item | Required | Observed |
|---|---|---|
| JARVIS commit | `2d7a2ec816500610eafdba4c1a3c0d73f5594c18` | **matches** |
| JARVIS working tree | clean | **clean** (0 porcelain lines) |
| `hermes_enabled` | false | **false** (config line 168) |
| JARVIS `config.yaml` mtime | untouched | **2026-09-07T22:06:46Z** |
| Hermes commit | `2237be355906fbe6065ce1815711eee52b2d646e` | **matches** |
| Hermes working tree | clean | **clean** |
| Ollama | unchanged | **0.31.2, no models resident** |
| Model / NVIDIA / RAM / swap | unchanged | **not touched** |

JARVIS was inactive during this task because it had reached its own deep-sleep timeout at
08:40:11Z and logged `resource_auto_deep_sleep_exit`. That is normal lifecycle behaviour and was
not modified.

## 4. Contract version and status

**JARVIS Agent Execution Contract v1** — id `jarvis.agent-execution-contract`, status
**FROZEN FOR IMPLEMENTATION**. Explicitly not DEPLOYED, not ACTIVE, not production-enabled. The
status value is asserted by the validator, which also fails if it is ever set to a deployed value.

## 5. Canonical execution contract

`JARVIS_AGENT_EXECUTION_CONTRACT.md` — 24 sections, RFC-2119 language, with NORMATIVE and
RATIONALE/NOTE clearly separated. It freezes what passed in C3/C4/C5 rather than redesigning it:
ownership, trust boundary, lanes, request classification, action types, reporting intent,
multi-action policy, canonicalization and provenance, corrections, permissions, confirmation,
capability limits, response obligations and their priority, deterministic response construction,
attribution, ambiguity, tool-result trust, audit, metric separation, prompt injection, twenty hard
invariants, and conformance.

## 6. Authority and ownership boundaries

The model owns understanding, conversational reasoning, candidate structured tool proposals, and
conversational-lane explanation. It does not own execution truth, permissions, confirmation
state, tool authorization, action completion, external state truth, provenance, audit truth, or
final operational response authority. Those twelve responsibilities belong to the JARVIS control
plane, and no flag, prompt, document or tool output may move one of them back to the model.

## 7. Trust boundary

**Model output is untrusted input.** On an operational turn raw model prose never becomes
user-visible output, and a model's textual assertion never creates provenance: saying "deployment
succeeded" does not make it so, and text shaped like a tool result is not a tool result. Trusted
sources are exactly `USER_FACT`, `USER_REPORTED`, `TOOL_SUCCESS`, `TOOL_ERROR`,
`CONFIRMATION_REQUIRED`, and the control plane's own router, capability and correction state.

## 8. Operational vs conversational lanes

Two lanes, decided deterministically and never by a model. OPERATIONAL covers action, status,
current value, operational user fact, correction, confirmation-sensitive action, ambiguity,
missing context, tool result and capability; its final response is always control-plane
constructed. CONVERSATIONAL covers explanation and ordinary discussion; model prose may be
user-visible there. An operational turn may never be relabelled conversational to let prose
through (INV-016).

## 9. Request and action contract

Nine request classes (`VALUE_QUERY`, `ACTION_REQUEST`, `STATUS_CHECK_REQUEST`,
`GENERAL_EXPLANATION`, `DECLARATIVE_FACT`, `AMBIGUOUS_ACTION`, `MISSING_CONTEXT_QUERY`,
`CONFIRMATION_SENSITIVE_ACTION`, `OTHER`), each with a machine-readable reason. Routing produces
`PRIMARY_ACTION`, `REPORTING_INTENT`, `TARGET` (with resolution state), `MULTI_ACTION` and
`CAPABILITY`. Validated action types: `OPEN_APP`, `OPEN_URL`, `DEPLOY`, `DELETE_PATH`,
`GET_DATABASE_STATUS`, plus `NONE`, `UNKNOWN_ACTION` and `MULTI_ACTION_UNSUPPORTED`. New action
types are allowed but must declare permission class, confirmation sensitivity, targets,
canonicalization and result fields, and may bypass nothing (`may_bypass: []`).

## 10. Canonicalization contract

Owned by JARVIS. Raw arguments retained verbatim, canonical arguments recorded separately, exact
versioned rules only, no fuzzy matching, unknown values unmodified, changes tested before
activation. The `vs code → vscode` alias is documented as an **example of the rule**, not as a
production requirement.

## 11. Permission contract

Seven classes: `READ_ONLY`, `REVERSIBLE_ACTION`, `DESTRUCTIVE_ACTION`, `PRIVILEGED_ACTION`,
`EXTERNAL_COMMUNICATION`, `SYSTEM_POWER`, `FINANCIAL_PURCHASE`. No model may self-authorize;
decisions are made before dispatch and recorded in audit; a denial cannot be overridden by model
prose, user prose, retrieved content or tool output. The concrete matrix is **not** implemented —
recorded as a known limitation and an entry criterion.

## 12. Confirmation contract

JARVIS-owned state. A confirmation-sensitive action becomes `CONFIRMATION_REQUIRED` with
`executed = false`, and nothing executes until a valid confirmation is deterministically bound to
that pending action by action type, target, arguments and requesting user/session. The model
cannot confirm, and "proceeding" is not confirmation. Expiry/freshness is specified as a
production requirement and is explicitly marked as not yet validated.

## 13. Provenance contract

Every operational fact records fact key, value, source, source turn/event, and current-or-
superseded status. Source categories are distinguished permanently: `USER_FACT` / `USER_REPORTED`
mean the user said it; `TOOL_SUCCESS` / `TOOL_ERROR` mean an authorized dispatcher observed it.
The YAML encodes this as `implies_verified_state`, true only for the two tool sources, and the
validator enforces it.

## 14. Correction semantics

The newest valid correction is the current conversational value; superseded values stay auditable
and are never presented as current. A correction changes the supplied value only — it never
implies that a port moved, a service restarted, or health was verified.

## 15. Tool-result trust contract

Only authorized dispatcher results may enter trusted provenance, bound to invocation id, tool
name, normalized arguments, dispatcher, timestamp, status, returned data and an audit event.
`TOOL_ERROR` is trusted negative evidence about that invocation only. `TOOL_SUCCESS` supports only
the facts in the payload — the minimal-result principle — and never unrelated health, performance,
persistence or downstream effect.

## 16. Response-obligation contract

Exactly one obligation per operational turn, from eleven families, derived only from frozen
inputs, with a fixed priority order: confirmation → tool error → tool success → ambiguity →
multi-action → capability → ledger value → user-fact acknowledgement → unverified status →
acknowledged intent → missing context. `MISSING_CONTEXT` is last and may never be chosen while a
higher-priority grounded source exists (INV-018). Per-scenario branches and benchmark-specific
matching are forbidden.

## 17. Operational-response contract

Operational text is built from ledger values, trusted tool fields, confirmation state, capability
state and target type. It must never invent completion, progress, live state, measurements,
diagnostics, targets, commands or file paths, and the response layer must not add a second value
extractor beside the provenance layer's own.

## 18. USER_FACT / USER_REPORTED attribution

User-supplied state is never silently promoted to verified state. "The API is reported as
returning 503, sir." is allowed; "The API is returning 503, sir." is not, absent tool evidence.
JARVIS may not claim configured / deployed / applied / switched / activated / verified / observed
as its own action without a trusted result. This is a semantic requirement, not a fixed wording.

## 19. Capability and ambiguity handling

No authorized tool → `REPORT_CAPABILITY_UNAVAILABLE`, no pretence that the action happened, and no
nearest-tool substitution unless a declared deterministic mapping exists. Unresolved required
target → no dispatch, no invented target, `REQUEST_TARGET`, asking only for the minimum missing
information.

## 20. Multi-action policy

Under the v1 MVP contract, two or more distinct executable actions are never silently partially
executed: classification `MULTI_ACTION_UNSUPPORTED`, dispatch count zero, and an explicit
limitation message. Planning or sequencing may be introduced only through separately authorized
and separately validated work.

## 21. Audit contract

Seventeen required event fields spanning request, classification, routing, raw proposal, raw and
canonical arguments, guard decision, permission decision, confirmation state, dispatch, result,
provenance updates, obligation, final source, final response and safety outcome. Model
chain-of-thought and private hidden reasoning are explicitly forbidden from audit storage.

## 22. Model-quality vs system-safety metrics

The two categories are frozen separately, with the governing principle that **system safety must
not depend on model perfection**. C5 is the demonstration: model quality was imperfect (92 of 350
operational drafts manually unsafe) while every system-safety metric was zero.

## 23. Hard invariants

Twenty numbered invariants, INV-001 through INV-020, contiguously numbered and unique. The fifteen
required by the task specification are included verbatim in meaning; five were added from
validated behaviour: deterministic lane (INV-016), reporting clause never adds an action
(INV-017), `MISSING_CONTEXT` last resort (INV-018), superseded values auditable and never current
(INV-019), and untrusted content never alters policy (INV-020).

## 24. Machine-readable contract validation

`agent-execution-contract.yaml` parses under `yaml.safe_load` with 22 top-level sections.
`validate_contract.py` ran **72 checks, 72 passed, 0 failed**, covering: contract identity and
frozen status; checkpoint commit and evidence hash; invariant uniqueness, contiguity and
cross-reference into the canonical document and the traceability matrix; obligation priority ranks
1–11 with confirmation first and missing-context last; every obligation documented in the
canonical text; provenance source semantics (`implies_verified_state`); every policy flag set to
the safe value; required audit fields present and chain-of-thought forbidden; conformance test IDs
matching the specification; and a scan proving the YAML contains no IP address, home path,
credential pattern or private key.

## 25. Conformance test specification

`CONFORMANCE_TESTS.md` specifies **18** tests, CT-001 through CT-018 — the fifteen required plus
lane determinism (CT-016), reporting-clause containment (CT-017) and missing-context last resort
(CT-018). Each names its setup, required outcome, contract clause and invariants. The
specification also states four rules for running them, including that tests must run against the
real control plane and that an unsafe model draft must actually be present for a containment test
to count as a pass.

## 26. Implementation boundary map

`IMPLEMENTATION_BOUNDARIES.md` assigns owns/never-owns for UI/Gateway, Hermes, Router, Safety and
Permission layer, Tool Dispatcher, Provenance Ledger, Response Layer and Audit; fixes the
normative data-flow shape (Hermes inside the loop, dispatcher as the only door to the world); and
lists the nine seams that must exist before integration, including the feature flag.

## 27. C3/C4/C5 traceability

`TRACEABILITY.md` maps every contract clause to the task that validated it, the test-only artifact
that implemented it, and the evidence file that measured it, plus an invariant-to-evidence table.
The validator asserts that every invariant appears in the traceability matrix. The document states
that the named artifacts are test-only and must not be copied into production.

## 28. Known limitations

Ten, recorded explicitly: the model remains imperfect; safety depends on the implementation
preserving this contract; eleven residual C5 utility failures (five from the provenance extractor
not recording a parameter from an imperative phrasing, six conversational-lane blocks);
confirmation persistence and expiry do not exist; the production permission matrix is not
implemented; real production tools were never exercised; tool results were synthetic; Hermes is
still disabled; a single model and a finite authored scenario set; audit is specified, not built.

## 29. Failure and security model

`SECURITY_FAILURE_MODEL.md` enumerates eighteen expected failures (F-01…F-18) — hallucinated
completion, wrong tool, invented argument, destructive proposal, ignored correction, fake tool
result, tool failure, timeout, ambiguity, changed target, multi-action, missing capability, stale
confirmation, internal leak, prompt injection, self-authorization, side effect outside the
dispatcher, control-plane bug — and names the containment owner and validation status for each. It
marks honestly that timeout injection, stale-confirmation replay and adversarial injection corpora
were **not** exercised. It also defines four trust zones and states its non-goals.

## 30. Prompt-injection principle

Frozen as §21 and INV-020: model content, retrieved content, web content, file content and
tool-output text do not override JARVIS control-plane safety policy. A model cannot lower its own
permission requirement; external content cannot create confirmation; tool output may supply data
but never policy; instructions embedded in untrusted content are data.

## 31. Production integration entry criteria

`PRODUCTION_ENTRY_CRITERIA.md` lists EC-01…EC-14 with today's honest status: three met (contract
committed, conformance spec exists, production baseline preserved; plus no public AI endpoint),
eleven not met — conformance tests implemented, permission model, confirmation state machine,
conforming dispatcher, provenance ledger, audit, response lock, rollback path, feature-flagged
integration, and the 13B11A plan. Hermes must not be enabled until all are met and recorded, and
meeting them authorizes integration work behind a flag, not shipping.

## 32. Task 13C relationship

Task 13C was **not** started. It must be re-scoped in light of this contract: any future
structured-tool or safety task must test **JARVIS control plane + model**, not the model's prose
as a source of action truth. A task that measures only model behaviour cannot establish
conformance.

## 33. Consistency review

`consistency_review.py` sweeps all nine contract documents for seven contradiction classes —
allowing raw operational model output, treating model text as a tool result, allowing model
confirmation, bypassing permissions, treating `USER_FACT` as tool-verified, partial multi-action
execution, and unsupported tool substitution. Documents are split into semantic units (paragraph,
table row, list item; YAML line with its parent key and list item) because a contradiction is a
property of a statement, not of a hard-wrapped line.

Result: **78 concept mentions examined, 67 prohibitive, 11 adjudicated with written reasons, 0
unresolved contradictions.** The eleven adjudications are conversational-lane scoping (2), section
headings or metric names (3), rejected-alternative history, cost statements or descriptions of a
non-conforming implementation (2), an ownership table's "never owns" column, future work gated
behind separate validation, and one use of "substituted" that refers to the deterministic layer's
own template rather than to tool substitution.

## 34. Architecture decision record

`ADR-001-JARVIS-AGENT-EXECUTION-BOUNDARY.md`, status **ACCEPTED FOR IMPLEMENTATION**. Context: six
model families fabricated execution under a frozen persona. Decision: the deterministic control
plane owns operational truth and execution authority. Consequences: safety decouples from model
quality, model swaps become cheap, failures become diagnosable — at the cost of a substantial
control plane, narrower operational phrasing, utility bounded by what provenance records, and more
work per new capability. Alternatives considered and rejected with evidence: trusting model prose;
prompt-only execution truth; model-only structured tools; semantic detector alone. The evidence
section states the three task verdicts and then states the limits of that evidence — inert
dispatcher, synthetic results, one model, finite scenarios.

## 35. Production changes

**NONE.** No production JARVIS source or configuration change, no Hermes change, no model or AI VM
change, no Ollama/NVIDIA/RAM/ballooning/swap change, no lifecycle change. Hermes remains disabled.
No golden run was required or performed, per the task specification, because nothing that golden
covers was touched; the production baseline was instead verified by commit hash, clean tree and
configuration flag.

## 36. Workspace changes

One new directory, `tasks/task13b10d/`, containing the canonical contract, the machine-readable
contract, the conformance specification, the implementation boundary map, the traceability matrix,
the ADR, known limitations, the security/failure model, the production entry criteria, the two
validation scripts and their outputs, the checkpoint verification record, the authorization record
and this report — plus an appended entry in `tasks/loop-log.md`.

## 37. Evidence

`/home/jarvis/.hermes-poc/evidence/task13b10d-agent-contract/` — contract artifacts, verification
outputs, repository diff and this report. `SHA256SUMS` excludes itself and verifies with zero
failures; the file count, manifest entry count and final `SHA256SUMS` hash are recorded in the
seal output and in the session log, so that sealing never hashes a file still being written.

## 38. Workspace commit

One commit, `docs: freeze JARVIS agent execution contract v1`. The evidence bundle is sealed
before the commit — so that the sealed `repo-diff.txt` records the exact change set being
committed — and the resulting commit hash is recorded in `tasks/loop-log.md` and in the session
log rather than inside the bundle it would otherwise invalidate.

## 39. Repository cleanliness

Workspace clean after the commit; production JARVIS clean at `2d7a2ec8…`; Hermes clean at
`2237be35…`.

## 40. Recommendation

The contract is frozen and ready to be implemented against — not deployed. Hermes stays disabled,
no production implementation begins automatically, and Task 13C is not started.

Recommended next step, as a **separate approval**: **Task 13B11A — production integration plan
against Agent Execution Contract v1**, planning only, mapping the current JARVIS code, the Hermes
integration seam, the production tool server, permissions, confirmation, provenance, response
layer, audit, feature flag, rollback and a phased implementation order, with no production changes
in that task either.
