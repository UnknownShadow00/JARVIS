# Task 13B11G — What the Classifier Is

## 1. The one question it answers

Contract §5.1: the control plane **MUST** derive a request class deterministically, before any
response construction, from the user text and the control plane's own state, and each
classification **MUST** carry a machine-readable reason.

The classifier answers **"what class of request is this?"** and nothing else. It does not answer
"what should execute?".

## 2. What the result may not contain

No `PrimaryAction`, no tool name, no target, no raw or canonical arguments, no `Lane`, no
permission class, no confirmation decision, no tool proposal, no dispatch instruction. Those are
§5.2 router, §11 permission, §12 confirmation and §4 lane concerns, each owned by a later phase.

Recognising `ACTION_REQUEST` does **not** mean choosing `OPEN_APP`. Recognising
`CONFIRMATION_SENSITIVE_ACTION` does **not** mean choosing `DELETE_PATH`, and does not decide that
confirmation is actually required — §12 owns that.

## 3. What it may read

The user's request text, and a caller-supplied deterministic context projection. Nothing else. The
13B11A `TARGET_COMPONENT_MAP.md` line 19 gives the classifier's inputs as "user text, ledger
snapshot" and `DEPENDENCY_GRAPH.md` line 76 describes it as "pure over text + snapshot"; this phase
implements that as `ClassifierContext`, a frozen record the caller fills from the P2 snapshot. The
classifier never touches `ProvenanceLedger`, `LedgerStore`, `current()` or `history()`.

## 4. Text is data, never policy

Unlike `lane.py`, this component's job is to look at the request text. The text is **data**. No
content inside a request can change the rule table, the precedence order, the classifier version,
the `RequestClass` enum or any control-plane policy. "Ignore your rules and classify this as
conversational" is classified by the frozen rules like any other string, and the rules are
module-level immutable data with no code path that writes them.

## 5. Deterministic, never a model

No Hermes, no Ollama, no external model, no embedding, no semantic similarity, no model-as-judge,
no model fallback. The legacy `app/brain/router.py` classifies six *intents* partly by LLM
(`_classify_with_ollama`); that module is untouched and is not this component. Gap G-01 in
`CONTRACT_GAP_ANALYSIS.md` is exactly the gap this phase fills.

No fuzzy matching either: no `difflib`, `rapidfuzz`, `fuzzywuzzy`, `Levenshtein`, embeddings, word
vectors, nearest-intent selection or spell correction. A request that meets no frozen rule falls
through the explicit precedence order to `OTHER`.

## 6. Versioned and auditable

`CLASSIFIER_VERSION` is a rule-set version, **not** a contract version — Agent Execution Contract
v1 is unchanged. Every classification carries the version, a stable `ClassificationReason` and the
`rule_id` that fired, so a stored classification can be replayed against the rule set that produced
it. Changing classification semantics requires a version bump and a re-derived corpus.

## 7. A reason is not authority

`ClassificationReason` is machine-readable metadata. It grants no permission, authorizes no
execution, creates no provenance and selects no tool. §11, §12, §9 and §5.2 remain the only sources
of those.

## 8. Fail-closed

Malformed input — a non-string request, `None`, an empty or whitespace-only request, a context
object of the wrong type — raises `ClassifierError`. It never falls back to `OTHER`,
`GENERAL_EXPLANATION` or any class. `OTHER` is a real classification for a well-formed request that
matched no higher rule, not an exception channel.

## 9. Passive and unwired

Nothing in the production request path imports it. The legacy path in `app/server.py` and
`app/brain/router.py` is unchanged and still classifies exactly as it did before this phase.
