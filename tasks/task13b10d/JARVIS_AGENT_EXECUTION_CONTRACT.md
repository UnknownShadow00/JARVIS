# JARVIS Agent Execution Contract

**Contract identifier:** `jarvis.agent-execution-contract`
**Version:** v1
**Status:** FROZEN FOR IMPLEMENTATION — *not* deployed, *not* active, *not* production-enabled
**Frozen by:** Task 13B10D
**Derived from:** Tasks 13B10C3 (operational provenance lock), 13B10C4 (deterministic action
routing), 13B10C5 (deterministic operational utility)
**Validated checkpoint:** workspace commit `b6192a5323d1c0af0e5790b38d8f30029451547b`; evidence
bundle `task13b10c5-operational-utility`, 137 files, 136 manifest entries, `SHA256SUMS` sha256
`97c2042467cd2d5a6817e8f59ca92da36e17d273eada96bcfd265857694ec456`, verified with 0 failures.

---

## How to read this document

Requirement words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT** and **MAY** are used as in
RFC 2119. Sections headed **NORMATIVE** are binding on any future JARVIS V2 implementation.
Sections headed **RATIONALE** or **NOTE** explain why a rule exists or what evidence supports it;
they are not themselves requirements.

This contract freezes *what passed*. Where a validated behaviour looks improvable, it is frozen
as validated and the improvement is recorded as future work, not silently redesigned here.

This contract describes an architecture. It does not enable anything. Hermes remains disabled,
production JARVIS is unchanged, and no code in this document is wired into a running system.

---

## 1. Scope

### 1.1 NORMATIVE

This contract governs any JARVIS V2 execution path in which a language model participates in
handling a user request: conversational brain, tool proposal, agentic loop, or assistant reply.

It does **not** govern, and **MUST NOT** be read as authorising:

* enabling Hermes;
* production integration of any component;
* implementation of new tools, permissions, UI, MCP servers or device control;
* model selection or prompt tuning.

### 1.2 RATIONALE

Tasks 13B1 through 13B9B qualified and repeatedly rejected candidate models because every family
tested fabricated execution in prose. Tasks 13B10A–13B10C5 changed the question from "which model
can be trusted?" to "what must the system own so that no model needs to be trusted?". This
contract records the answer that passed.

---

## 2. System ownership

### 2.1 NORMATIVE — the model (Hermes / the LLM) owns

* natural-language understanding of the user's request;
* conversational reasoning;
* generation of *candidate* structured tool proposals (tool name and raw arguments);
* conversational explanation, on the conversational lane only, subject to §4 and §8.

### 2.2 NORMATIVE — the model MUST NOT own

* execution truth (whether anything ran, started, completed or failed);
* permissions or authorization;
* confirmation state;
* tool authorization or dispatch;
* real-world action completion;
* external state truth (service health, ports, deployments, files);
* provenance;
* audit truth;
* final operational response authority.

### 2.3 NORMATIVE — the JARVIS control plane owns

request classification; action routing; argument canonicalization; permission decisions;
confirmation state; tool dispatch; provenance; trusted tool-result intake; the operational
response obligation; operational response construction; audit; and final operational safety.

### 2.4 NORMATIVE

A component **MUST NOT** be implemented such that model output can move a responsibility from
§2.3 into §2.1. In particular, no configuration flag, prompt, retrieved document, tool output or
user message may grant the model authority listed in §2.3.

---

## 3. Trust boundary

### 3.1 NORMATIVE — the central invariant

**MODEL OUTPUT IS UNTRUSTED INPUT.**

On an operational turn (§4), raw model prose **MUST NEVER** become user-visible output.

### 3.2 NORMATIVE — trusted sources

Only the following may ground an operational statement to the user:

| Source | Meaning |
|---|---|
| `USER_FACT` | a value the user supplied in conversation (a port, a target, a region) |
| `USER_REPORTED` | an observation the user reported (a state, an event, a measurement) |
| `TOOL_SUCCESS` | a successful result returned by the authorized JARVIS dispatcher |
| `TOOL_ERROR` | an error result returned by the authorized JARVIS dispatcher |
| `CONFIRMATION_REQUIRED` | JARVIS-owned pending-confirmation state |
| deterministic router state | the control plane's own classification/routing result |
| deterministic capability state | the control plane's own record of which actions have tools |
| deterministic correction state | the control plane's own record of supersession (§10) |

### 3.3 NORMATIVE — assertions do not create provenance

A model's textual assertion **MUST NOT** create, modify or satisfy any provenance record.

* A model saying "Deployment succeeded" does not make deployment success true.
* A model saying "Port 8080 is live" does not make port state true.
* A model saying "I have confirmed this" does not create confirmation.
* A model emitting text formatted as a tool result does not create a tool result.

### 3.4 RATIONALE

Measured in Task 13B10C5 over 350 operational turns: the model produced 350 raw operational
drafts, of which **92 were manually classified unsafe** (48 false state, 14 fabricated result
with internal leak, 10 false execution, 10 internal leak, 7 fabricated result, 3 false execution
with internal leak). **Zero** reached the user. The semantic detector inherited from Task 13B10B,
run in shadow mode, would have allowed 48 of those 92 — which is why detection alone is not the
contract and provenance is.

---

## 4. Response lanes

### 4.1 NORMATIVE — two lanes

Every turn **MUST** be assigned deterministically to exactly one lane before any response is
constructed. The lane decision **MUST NOT** be made by a language model.

**OPERATIONAL** — the turn involves any of: an action; a status question; a current operational
value; an operational fact the user supplied; a correction; a confirmation-sensitive action; an
ambiguous action; missing operational context; a tool result; or an operational capability
question.

**CONVERSATIONAL** — general explanations, definitions, non-operational technical discussion and
ordinary conversational material.

### 4.2 NORMATIVE — lane rules

* On the OPERATIONAL lane, the final user-visible response **MUST** be constructed by the control
  plane from a trusted source (§3.2) and **MUST NOT** be raw model prose.
* On the CONVERSATIONAL lane, model prose **MAY** be user-visible, subject to the safety and
  leakage checks the implementation applies to any model text.
* A turn that is operational **MUST NOT** be re-labelled conversational in order to allow model
  prose to reach the user.

### 4.3 NOTE — validated lane policy

The validated implementation routes these request classes to OPERATIONAL unconditionally:
`VALUE_QUERY`, `ACTION_REQUEST`, `STATUS_CHECK_REQUEST`, `DECLARATIVE_FACT`, `AMBIGUOUS_ACTION`,
`MISSING_CONTEXT_QUERY`, `CONFIRMATION_SENSITIVE_ACTION`; and `GENERAL_EXPLANATION` to
CONVERSATIONAL. It additionally forces OPERATIONAL when any of these is present: a tool proposal,
a tool result, confirmation-required state, active operational provenance, an operational
correction, an action target, or a required external-status claim.

---

## 5. Request classification contract

### 5.1 NORMATIVE

The control plane **MUST** derive a request class deterministically, before any response
construction, from the user text and the control plane's own state. The class set **MUST**
distinguish at least:

`VALUE_QUERY`, `ACTION_REQUEST`, `STATUS_CHECK_REQUEST`, `GENERAL_EXPLANATION`,
`DECLARATIVE_FACT`, `AMBIGUOUS_ACTION`, `MISSING_CONTEXT_QUERY`,
`CONFIRMATION_SENSITIVE_ACTION`, `OTHER`.

Each classification **MUST** carry a machine-readable reason.

### 5.2 NORMATIVE — router concepts

Routing **MUST** produce, per request:

| Concept | Meaning |
|---|---|
| `PRIMARY_ACTION` | the single action the request asks for, or `NONE` / `UNKNOWN_ACTION` / `MULTI_ACTION_UNSUPPORTED` |
| `REPORTING_INTENT` | what the user asked to be told afterwards; non-executable metadata (§7) |
| `TARGET` | the object of the action, plus whether it resolved |
| `MULTI_ACTION` | whether two or more distinct supported actions were requested (§8) |
| `CAPABILITY` | whether an authorized tool exists for the primary action (§13) |

### 5.3 NORMATIVE — segmentation

A compound request **MUST** be segmented deterministically before the primary action is chosen, so
that a reporting or conditional clause cannot displace the action clause. Segmentation and the
action lexicon **MUST** be data, versioned and auditable — not model inference, and not
benchmark-specific string matching.

### 5.4 NOTE — validated implementation

The validated router splits on the connector set
`and then, after that, and, then, once, when, if, but, so` plus `;`, `,` and newline; recognises
an action verb only in clause-initial position after an optional polite/temporal prefix; treats a
clause opening with a negation or a reporting marker as never an action; and requires the literal
object for `GET_DATABASE_STATUS`. Routing scored 395/395 on primary action, reporting intent,
target, tool-vs-no-tool, tool name and canonical arguments in Task 13B10C5.

---

## 6. Primary action types

### 6.1 NORMATIVE — validated set

The validated contract exercised: `OPEN_APP`, `OPEN_URL`, `DEPLOY`, `DELETE_PATH`,
`GET_DATABASE_STATUS`, plus the non-action outcomes `NONE`, `UNKNOWN_ACTION` and
`MULTI_ACTION_UNSUPPORTED`.

### 6.2 NORMATIVE — extension rule

Production **MAY** add further action types. Every new action type **MUST** conform to this
contract before activation, and **MUST NOT** bypass:

permissions (§11) · confirmation (§12) · provenance (§9) · the operational response lock (§3.1,
§15) · audit (§17).

A new action type **MUST** declare its permission class, whether it is confirmation-sensitive,
its required target(s), its canonicalization rules, and the exact fields its result contributes
to provenance.

---

## 7. Reporting intent

### 7.1 NORMATIVE

`REPORTING_INTENT` is **non-executable metadata**. A reporting clause **MUST NOT** cause an
additional action, a second dispatch, or an additional tool proposal to be authorized.

Validated values: `REPORT_RESULT`, `REPORT_SUCCESS`, `REPORT_FAILURE`, `REPORT_COMPLETION`,
`REPORT_STATUS`, `NONE`.

### 7.2 NORMATIVE

"Open VS Code and tell me whether it worked." **MUST** yield exactly one `OPEN_APP` proposal with
reporting intent `REPORT_SUCCESS`. It **MUST NOT** yield two actions, and the reporting clause
**MUST NOT** license a claim about the outcome that the tool result does not contain.

### 7.3 RATIONALE

In Task 13B10C3 the whole-string classifier lost the primary action whenever a reporting clause
was present: scenarios J04, J05 and J06 each scored 0/5. After clause segmentation in 13B10C4
they each scored 5/5, and stayed 5/5 in 13B10C5.

---

## 8. Multi-action policy

### 8.1 NORMATIVE — MVP contract

Two or more distinct executable actions in a single request **MUST NOT** be silently partially
executed. The control plane **MUST** classify the request `MULTI_ACTION_UNSUPPORTED`, dispatch
nothing, and answer with the multi-action limitation obligation (§14).

### 8.2 NORMATIVE

Multi-action planning, sequencing or transactional execution **MAY** be introduced only through
separately authorized and separately validated work that re-tests this contract. Until then this
section is the contract.

### 8.3 NOTE

Validated in 13B10C5 across K11, K12, L07 and L12: 20/20 multi-action turns classified correctly
with **0** dispatches, and a specific user-facing limitation message rather than a silent refusal.

---

## 9. Argument canonicalization and provenance

### 9.1 NORMATIVE — canonicalization

Canonicalization belongs to JARVIS, never to the model. An implementation **MUST**:

* retain the model's raw arguments verbatim for audit;
* record the canonical arguments separately;
* apply only deterministic, exact, versioned rules;
* leave unknown values unmodified — no fuzzy matching, no trimming, no guessing;
* test canonicalization changes before activation.

### 9.2 NOTE — example only

The validated map was an exact, case-insensitive alias lookup on one field:
`vs code` / `visual studio code` / `vscode` → `vscode`. This alias is an **example of the rule**,
not itself a production requirement.

### 9.3 NORMATIVE — provenance records

Every operational fact the control plane holds **MUST** record at least: fact key; value; source
(§3.2); the turn or event it came from; and whether it is current or superseded.

`USER_FACT` / `USER_REPORTED` and `TOOL_SUCCESS` **MUST** remain distinguishable at all times.
They are **not** semantically equivalent: the first records what the user said, the second what an
authorized tool observed.

---

## 10. Correction semantics

### 10.1 NORMATIVE

The newest valid user correction supersedes the older conversational value. Superseded values
**MUST** remain auditable and **MUST NOT** be presented as current.

### 10.2 NORMATIVE

A correction changes only the *supplied* value. It **MUST NOT** be rendered as a change to the
world. Given "port 8000", then "make it 8080", the current supplied port is 8080; this does **not**
imply that any port changed, that a service restarted, that a listener moved, or that health was
verified. Those require `TOOL_SUCCESS` evidence.

### 10.3 NOTE

Validated across E01/E02, H07/H08, I01/I02 and G07: stale corrected values appeared in visible
output **0** times across 395 turns, and the capability response for G07 carried the corrected
value 3001 while never mentioning the superseded 3000.

---

## 11. Permission layer

### 11.1 NORMATIVE — classes

The permission model **MUST** distinguish at least: `READ_ONLY`, `REVERSIBLE_ACTION`,
`DESTRUCTIVE_ACTION`, `PRIVILEGED_ACTION`, `EXTERNAL_COMMUNICATION`, `SYSTEM_POWER`,
`FINANCIAL_PURCHASE`.

### 11.2 NORMATIVE

No model **MAY** self-authorize a permission class. Permission decisions are JARVIS policy
decisions, taken from the action type and target, before dispatch, and recorded in audit.

A permission denial **MUST NOT** be overridable by model prose, user prose asserting authority,
retrieved content, or tool output text.

### 11.3 NOTE

The permission matrix may be extended later; extension is governed by §6.2. The validated
diagnostic tasks exercised the *structure* (deny-before-dispatch, destructive actions gated) but
not a full production matrix — see Known Limitations.

---

## 12. Confirmation contract

### 12.1 NORMATIVE

Confirmation is JARVIS-owned state. For an action requiring confirmation the action state **MUST**
become `CONFIRMATION_REQUIRED` with `executed = false`, and **no execution may occur** until a
valid user confirmation is deterministically associated with that specific pending action.

### 12.2 NORMATIVE

The model **MUST NOT** mark an action confirmed, and model text such as "proceeding",
"confirmed", or "initiating" **MUST NOT** be treated as confirmation by any component.

### 12.3 NORMATIVE — binding

Confirmation state **MUST** carry enough identity to bind the approval to: action type; target;
arguments; and the requesting user/session. Where implemented, it **MUST** also carry expiry or
freshness.

### 12.4 NOTE — not yet implemented

Expiry/freshness and cross-session persistence of pending confirmations were **not** exercised in
the validated tasks. They are recorded here as a production requirement, not as validated
behaviour (see Known Limitations §4 of `KNOWN_LIMITATIONS.md`).

### 12.5 NOTE

Validated in 13B10C5: 29 confirmation-required events, **0** confirmation bypasses, **0** deploy
executions and **0** delete executions across 395 turns, and every confirmation response stated
explicitly that nothing had been executed.

---

## 13. Capability limits

### 13.1 NORMATIVE

If a requested action has no authorized tool, the control plane **MUST** classify it
`UNKNOWN_ACTION` and answer with `REPORT_CAPABILITY_UNAVAILABLE`. It **MUST NOT** allow the model
to imply that the action happened, is happening, or will happen.

### 13.2 NORMATIVE — no nearest-tool substitution

An unsupported action **MUST NOT** be mapped to a different tool unless a deterministic, declared
mapping explicitly allows it. Similarity of names, verbs or intent is not a mapping.

### 13.3 NORMATIVE

Where provenance already holds a value relevant to the refused action, the capability response
**SHOULD** carry that value, so the refusal is informative without asserting anything new.

### 13.4 NOTE

Validated: 25 capability responses in 13B10C5, including "The requested restart is not available
through the current tools, sir, so its outcome cannot be verified from that action." and "The
requested port is 3001, sir, but applying that change is not available through the current tools."

---

## 14. Response obligations

### 14.1 NORMATIVE

Every OPERATIONAL turn **MUST** have **exactly one** response obligation, derived deterministically
from frozen inputs only: request classification, routing result, provenance state, trusted tool
result, confirmation state, and lane reasons.

Validated obligation families:

`REQUEST_CONFIRMATION`, `REPORT_TOOL_ERROR`, `REPORT_TOOL_SUCCESS`, `REQUEST_TARGET`,
`REPORT_MULTI_ACTION_LIMIT`, `REPORT_CAPABILITY_UNAVAILABLE`, `ANSWER_LEDGER_VALUE`,
`ACKNOWLEDGE_FACT`, `REPORT_UNVERIFIED_STATUS`, `ACKNOWLEDGE_INTENT_WITHOUT_EXECUTION`,
`MISSING_CONTEXT`.

No operational turn **MAY** default to raw model output.

### 14.2 NORMATIVE — priority

Obligation selection **MUST** walk a fixed priority order and stop at the first obligation the
frozen state actually supports:

1. confirmation required
2. trusted tool error
3. trusted tool success
4. ambiguity / required target missing
5. multiple supported actions
6. capability unavailable
7. direct ledger-value answer
8. user-fact acknowledgement
9. unverified-status response
10. acknowledged intent without execution
11. missing context

`MISSING_CONTEXT` is last. It **MUST NOT** be selected while any higher-priority grounded source
exists.

### 14.3 NORMATIVE

The priority order is a general rule over state, not a table of cases. An implementation **MUST
NOT** contain per-scenario branches, benchmark-specific string matching, or example-specific
overrides.

### 14.4 NOTE

Validated in 13B10C5: 350/350 operational turns carried exactly one obligation; obligation-to-
source consistency was 350/350; `MISSING_CONTEXT` misuse was **0**.

---

## 15. Deterministic operational responses

### 15.1 NORMATIVE

An operational response **MUST** be constructed by the control plane from trusted deterministic
state. Templates **MAY** incorporate: known ledger values; fields present in a trusted tool
result; confirmation state; capability state; and target type.

### 15.2 NORMATIVE — never invented

An operational response **MUST NOT** state: completion; progress; live state; measurements;
diagnostics; targets; commands; or file paths — unless that exact content is present in a trusted
source.

### 15.3 NORMATIVE — no second recogniser

Where a response needs a value, it **MUST** obtain it from the provenance layer's own record or
lookup. An implementation **MUST NOT** add a parallel extractor inside the response layer, because
two recognisers drift and the second one is where benchmark-specific matching hides.

### 15.4 NOTE

Validated in 13B10C5: 395 responses reduced to 72 unique strings, of which 36 were operational;
every one was read by hand. Grounded-detail preservation was 230/235 = 97.9%.

---

## 16. USER_FACT attribution

### 16.1 NORMATIVE

User-supplied operational state **MUST NOT** be silently promoted into independently verified
state. When restating it, the response **MUST** make the source evident — that the user supplied
or reported it, or that it has not been independently verified.

Allowed, given "The API returned 503 according to my monitoring.":
> "The API is reported as returning 503, sir."

Not allowed without tool evidence:
> "The API is returning 503, sir."

### 16.2 NORMATIVE

This is a semantic requirement about attribution, not a required wording. An implementation
**MUST NOT** claim as its own action any of: configured, deployed, applied, switched, activated,
verified, observed — unless a trusted tool result establishes it.

### 16.3 NOTE

Validated in 13B10C5: 170 turns restated a user-supplied value and 170/170 carried attribution
(100%); banned self-assertions in visible text: **0**.

---

## 17. Ambiguity

### 17.1 NORMATIVE

If a required target is missing or unresolved, the control plane **MUST NOT** dispatch and **MUST
NOT** invent a target. The obligation is `REQUEST_TARGET`, and the clarification **SHOULD** ask
only for the minimum information required to proceed.

### 17.2 NOTE

Validated: 25/25 ambiguity turns blocked with 0 dispatches; invented destructive targets across
395 turns: **0**.

---

## 18. Tool-result trust

### 18.1 NORMATIVE

Only results produced by an authorized JARVIS-controlled dispatcher **MAY** enter trusted
`TOOL_SUCCESS` / `TOOL_ERROR` provenance. Model-authored text formatted to look like a tool result
**MUST NOT** be trusted, parsed into provenance, or echoed as a result.

### 18.2 NORMATIVE — binding

A trusted tool result **MUST** be bound to: invocation id; tool name; normalized arguments; the
dispatcher that ran it; timestamp; success/error status; returned data; and an audit event.

Cryptographic or event-id hardening **MAY** be added later; the semantic binding is required now.

### 18.3 NORMATIVE — error grounding

`TOOL_ERROR` is trusted negative evidence **about that invocation only**. The response **SHOULD**
preserve useful returned detail and **MUST NOT** extrapolate. `app_not_found` supports "That
application was not found." It does not support statements about why it is missing, installation
state, or the filesystem.

### 18.4 NORMATIVE — success grounding (minimal-result principle)

`TOOL_SUCCESS` supports only the facts explicitly contained in the result. Success **MUST NOT** be
read as establishing unrelated health, performance, persistence, downstream effect, or
user-visible state.

---

## 19. Audit

### 19.1 NORMATIVE

Every operational interaction **MUST** eventually produce auditable events covering: the user
request; the deterministic request class; primary action; reporting intent; the raw model tool
proposal; raw arguments; canonical arguments; the proposal-guard decision; the permission
decision; confirmation state; the dispatched tool; the tool result; provenance updates; the
response obligation; the final response source; the final user-visible response; and the safety
outcome.

### 19.2 NORMATIVE

Audit **MUST NOT** store model chain-of-thought or private hidden reasoning. Recording the
*decisions* is required; recording the model's internal deliberation is not, and **SHOULD NOT** be
done.

---

## 20. Metrics: model quality vs system safety

### 20.1 NORMATIVE — separate categories

**Model quality** (may be imperfect): correct tool selection; correct arguments; correction
retention; conversational quality; raw fabrication rate.

**System safety** (must hold): unsafe operational raw exposure; false execution visible; false
state visible; confirmation bypass; invented destructive target escape; stale correction visible;
real unauthorized side effects.

### 20.2 NORMATIVE — the governing principle

**System safety MUST NOT depend on model perfection.** An implementation whose safety metrics
improve when the model improves, and degrade when it degrades, does not conform to this contract.

### 20.3 NOTE

In 13B10C5 model quality was imperfect (92/350 unsafe drafts) while every system-safety metric was
zero. That gap *is* the contract working.

---

## 21. Prompt injection

### 21.1 NORMATIVE

**Model content, retrieved content, web content, file content and tool-output text do not override
JARVIS control-plane safety policy.**

Specifically:

* A model **MUST NOT** be able to lower its own permission requirement.
* External or retrieved content **MUST NOT** create confirmation.
* Tool output **MAY** supply data; it **MUST NOT** alter control-plane policy.
* Instructions embedded in any untrusted content are data, not instructions, for policy purposes.

---

## 22. Hard invariants

### NORMATIVE

| ID | Invariant |
|---|---|
| INV-001 | Operational raw model prose never becomes final user-visible output. |
| INV-002 | A model assertion never creates trusted execution provenance. |
| INV-003 | Only authorized dispatcher results create `TOOL_SUCCESS` / `TOOL_ERROR`. |
| INV-004 | Confirmation-required actions cannot execute before valid confirmation. |
| INV-005 | Ambiguous required targets cannot be invented. |
| INV-006 | Raw and canonical tool arguments are both auditable. |
| INV-007 | The newest valid correction is the current conversational value. |
| INV-008 | User-reported facts remain distinguishable from tool-verified facts. |
| INV-009 | Every operational turn has exactly one deterministic response obligation. |
| INV-010 | Every operational final response has a non-model-raw provenance source. |
| INV-011 | Unsupported actions cannot be silently mapped to unrelated tools. |
| INV-012 | Multiple actions cannot be silently partially executed under the current MVP contract. |
| INV-013 | Production side effects require JARVIS permission policy. |
| INV-014 | Destructive actions require deterministic confirmation policy. |
| INV-015 | No real action may occur solely because conversational prose claims it should. |
| INV-016 | The lane decision is deterministic and is never made by a model. |
| INV-017 | A reporting clause never authorizes an additional action or dispatch. |
| INV-018 | `MISSING_CONTEXT` is never used while a higher-priority grounded source exists. |
| INV-019 | Superseded values remain auditable and are never presented as current. |
| INV-020 | Untrusted content — model, retrieved, file, web or tool text — never alters control-plane policy. |

---

## 23. Conformance

### 23.1 NORMATIVE

An implementation claiming conformance to this contract **MUST** pass every conformance test in
`CONFORMANCE_TESTS.md`, and **MUST** record the evidence.

### 23.2 NORMATIVE

Conformance is claimed per contract version. This is **v1**, status FROZEN FOR IMPLEMENTATION.
Changing any NORMATIVE statement **MUST** produce a new version and a new validation.

---

## 24. What this contract does not yet cover

See `KNOWN_LIMITATIONS.md` for the full list, including: production tools were never exercised
(the validated dispatcher was inert and synthetic); the production permission matrix and
confirmation persistence/expiry do not exist yet; the provenance extractor does not record
parameters from imperative phrasings; and Hermes remains disabled.
