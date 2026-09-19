# Task 13B11G — Traceability

Each row: what was built → the contract clause that requires it → the class or rule it realises →
the invariant it protects → the future consumer that will read it.

## 1. Artifact → clause

| Artifact | Contract clause | Realises | Invariant | Future consumer |
|---|---|---|---|---|
| `classify()` deriving one class before any response | §5.1 (NORMATIVE) — derive a request class deterministically, before response construction, from user text and control-plane state | all nine `RequestClass` members | INV-016 (the lane decision is deterministic and never made by a model) is only reachable if its input class is too | P3 action router; P6 obligation engine |
| `ClassificationReason` on every result | §5.1 — "each classification MUST carry a machine-readable reason" | 11 reasons, one per rule | audit replay: a stored classification can be re-checked against the rule set that produced it | P1 audit writer (schema v3), P11 replay |
| `CLASSIFIER_VERSION` + `rule_id` | §5.3 — segmentation and the action lexicon MUST be data, versioned and auditable, not model inference and not benchmark-specific string matching | the rule table as data | reproducibility on replay (P3 exit criterion, `IMPLEMENTATION_PHASES.md`) | P11 A/B and readiness |
| leading-clause cut + clause-initial head token | §5.4 (NOTE) — the validated router recognises an action verb only in clause-initial position after an optional polite/temporal prefix | R-01…R-04 | §7.1: a reporting clause is non-executable metadata and must not displace the action | P3 action router (CT-017) |
| `AMBIGUOUS_REFERENTS`, R-01 first | §17.1 — MUST NOT dispatch and MUST NOT invent a target when a required target is missing or unresolved | `AMBIGUOUS_ACTION` | no invented destructive target | P5 dispatcher (CT-005); P6 `REQUEST_TARGET` obligation |
| `DECLARATIVE_FACT` distinct from `ACTION_REQUEST` | §16.1 — user-supplied operational state MUST NOT be silently promoted into independently verified state | R-10 | INV-010 (every operational final response has a non-model-raw provenance source) | P2 ledger intake; P6 attribution |
| `STATUS_CHECK_REQUEST` distinct from a user conclusion | §16.1 — a user's own report is not verified state | R-04, R-09 | a status claim needs tool evidence, not a restatement | P3 router's read-only actions; P13 capability |
| `GENERAL_EXPLANATION` surviving operational vocabulary | §4.1 — CONVERSATIONAL includes general explanation, definition and non-operational technical discussion | R-08 | INV-001 (operational raw model prose never becomes final user-visible output) — only a correctly conversational turn may let prose stand | P3 lane policy (`lane.decide`) |
| `VALUE_QUERY` / `MISSING_CONTEXT_QUERY` split on the caller's key set | §5.1 — the class is derived from the text **and** the control plane's own state | R-05, R-06, R-07 | both are always-operational, so the split cannot widen what a model may say | P2 ledger lookup; P6 obligation |
| `CONFIRMATION_SENSITIVE_ACTION` as a class only | §12 owns whether confirmation is required; §11 owns permission | R-02 | classification never grants execution authority | P4 permission engine; P5 confirmation manager |
| `ClassifierError`, no fallback class | §5.1 + the fail-closed principle of §3 | none — an error is not a class | malformed input cannot reach the conversational lane by accident | every caller |

## 2. Boundary traces the task specification asked for

| Requirement | Where it lands |
|---|---|
| deterministic classification → JARVIS control-plane ownership | §2 system ownership lists `request_classification` as a control-plane responsibility; this module is the first production implementation of it. Gap **G-01** in `CONTRACT_GAP_ANALYSIS.md` — "intent classification is partly LLM" — is the gap this closes, additively: `app/brain/router.py` still owns the live path and is byte-identical. |
| declarative-vs-action distinction → execution-truth boundary | R-10 vs R-01/R-02/R-03. "The deployment target is staging" supplies a value; it does not deploy. §10.2 makes the same point for corrections: a correction changes the *supplied* value and must not be rendered as a change to the world. |
| ambiguity classification → no invented target | R-01 fires before R-02 and R-03, so a sensitive verb with an unknown target is `AMBIGUOUS_ACTION`, never a sensitive action against a guessed object. §17.1, CT-005. |
| general explanation → conversational-lane allowance | R-08 is the only rule producing the one class the lane policy may route conversationally when no operational condition holds (13B11F truth table: 2 of 1,152 rows). Misclassifying an operational turn as `GENERAL_EXPLANATION` is the single classification error that could let raw prose stand, which is why R-08 sits at rank 8, below every operational rule. |
| status check → future read-only router behaviour | R-04 and R-09 mark the turns for which the router will select a read-only action and the obligation engine will require a tool-grounded answer. The classifier selects no tool and names no action type. |

## 3. Conformance tests this phase prepares

`IMPLEMENTATION_PHASES.md` lists CT-005, CT-009, CT-016 and CT-017 as P3's conformance set. None
can be executed by the classifier alone — each needs the router, the dispatcher or the lane —
but each depends on a class this phase now produces:

| Test | Needs from the classifier |
|---|---|
| CT-005 — ambiguous target prevents dispatch | `AMBIGUOUS_ACTION` on action form with an absent or deictic target |
| CT-009 — multi-action does not silently partially execute | a class for the request while the router detects the second action; `PRECEDENCE.md` row 12 |
| CT-016 — the lane decision is deterministic | a deterministic `RequestClass`, which is the lane policy's first argument |
| CT-017 — a reporting clause never adds an action | the leading-clause cut, so "and tell me whether it worked" cannot displace the action clause |

## 4. Deferred operator decisions — untouched

`lane` is still not one of the 17 contract audit fields; the redaction secret-key list was not
introduced; `ProvenanceSource` still has exactly 8 members with no `TIMEOUT`. Schema version is
still 3. Asserted by test in `classifier_non_activation_test.py` §5 and printed in
`13-static-review-and-hermes-non-use.txt` §8.
