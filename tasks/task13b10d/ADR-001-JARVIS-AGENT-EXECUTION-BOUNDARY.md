# ADR-001 — JARVIS deterministic control plane owns operational truth and execution authority

**Status:** ACCEPTED FOR IMPLEMENTATION
**Date:** 2026-09-18
**Task:** 13B10D (architecture/contract freeze)
**Supersedes:** the implicit assumption of Tasks 13B1–13B9B that a sufficiently good model could
be trusted to report its own actions.

---

## Context

JARVIS V2 needs a conversational brain that can also act. Between Task 13B1 and Task 13B9B, six
model families were qualified against a frozen persona: qwen3.5:27b, gpt-oss:20b (LOW and MEDIUM),
ministral-3:14b, qwen3:30b-instruct, mistral-small3.2:24b and granite4.1:30b-q3_K_M. Every one of
them, including the best, asserted in prose that actions had been carried out when nothing had
run. Two follow-up attempts to fix this at the model layer — an ablation of the prompt (13B6A) and
a Hermes-native persona (13B8A) — did not remove the behaviour.

Task 13B10A then gave the model structured tools. That fixed grounding *after* a tool result
existed, but prose fabrication persisted. Task 13B10B added a semantic detector over the model's
drafts; it blocked the obvious cases but, measured later in 13B10C5's shadow mode, would still
have allowed 48 of 92 manually unsafe drafts.

The question therefore changed from "which model can be trusted to report the truth?" to "what
must the system own so that no model needs to be trusted?"

Tasks 13B10C3, 13B10C4 and 13B10C5 answered it experimentally.

## Decision

**The JARVIS deterministic control plane, not the LLM, owns operational truth and execution
authority.**

Concretely, and as frozen in `JARVIS_AGENT_EXECUTION_CONTRACT.md` v1:

* Model output is untrusted input. On an operational turn, raw model prose never becomes the
  user-visible response.
* Only an authorized JARVIS dispatcher can cause a side effect or create trusted tool provenance.
* Permissions, confirmation, routing, canonicalization, provenance, the response obligation and
  audit are control-plane responsibilities and cannot be delegated to, or overridden by, model
  text.
* Every operational turn resolves to exactly one deterministic response obligation, rendered from
  trusted state.
* The model keeps what it is good at: understanding, conversation, and proposing structured tool
  calls.

## Consequences

**Positive.**

* Safety stops depending on model quality. In 13B10C5 the model produced 92 unsafe operational
  drafts out of 350 and none reached the user; every hard safety metric was zero.
* The assistant is still useful: operational utility measured 97.2% (384/395), with grounded
  detail preserved 97.9% of the time and user-supplied facts attributed 100% of the time.
* Model swaps become cheap. A different or better model changes quality metrics, not the safety
  envelope.
* Failures become diagnosable: a wrong answer is traceable to a class, a route, an obligation and
  a source.

**Negative / costs.**

* The control plane is now substantial: router, guard, ledger, obligation layer, templates, audit.
  All of it must be implemented, tested and maintained in production, and a bug there is a safety
  bug.
* Operational responses are templated and will read more narrowly than free model prose. The
  conversational lane exists precisely to keep the assistant from sounding like a form letter.
* Utility is bounded by what provenance records. Five of 11 residual failures in C5 were exactly
  this: the extractor records no port from "Set the service port to 9100", so the later recall
  question could not be answered.
* New capabilities cost more: each new action type must declare permission class, confirmation
  sensitivity, targets, canonicalization and result fields before activation.

## Alternatives considered

1. **Trust model prose.** Rejected: six model families fabricated execution under a frozen
   persona; this is the failure the whole 13B series documents.
2. **Prompt-only execution truth** (instruct the model never to claim actions). Rejected: 13B6A
   and 13B8A tested prompt and persona changes; fabrication persisted across families.
3. **Model-only structured tool behaviour** (tools, but the model still writes the final answer).
   Rejected: 13B10A showed grounding improves only *after* a result exists; prose fabrication
   continued on turns without results.
4. **Semantic response detector alone** (13B10B). Rejected: a detector is a classifier over model
   text and inherits its own false-negative rate — 48 of 92 unsafe drafts allowed in shadow mode
   in 13B10C5. It is kept as shadow evidence, never as the gate.
5. **Deterministic provenance lock plus control plane** (13B10C3–C5). **Accepted**: measured zero
   operational raw exposure across three independent scored runs while utility rose from 81.5% to
   97.2%.

## Evidence

| Task | Verdict | Key measurement |
|---|---|---|
| 13B10C3 | provenance lock partially validated | 240 operational turns, 100 unsafe drafts, 0 exposed; utility 81.5% |
| 13B10C4 | deterministic action routing validated | routing 335/335; J04–J06 0/5 → 5/5; utility 89.3% |
| 13B10C5 | deterministic operational utility validated | 395 turns; utility 97.2%; obligation 350/350; attribution 100%; 0 exposed of 92 unsafe drafts |

All three bundles are sealed and re-verified with zero checksum failures; the C5 bundle
(`97c20424…`) was re-verified at the start of Task 13B10D.

**Limits of this evidence.** These were diagnostic runs with an inert dispatcher and synthetic
tool results, a single model, a fixed scenario set, and no production tools, no production
permission matrix and no confirmation persistence. The decision is about *architecture*, and the
evidence supports the architecture; it does not demonstrate a production implementation, which is
what the conformance tests exist to require.
