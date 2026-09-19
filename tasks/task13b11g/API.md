# Task 13B11G — Classifier API

`app/execution/classifier.py`. Everything below is passive: holding a result changes nothing,
and nothing in `app/` calls any of it.

## 1. The one entry point

```python
classify(request: str, context: ClassifierContext = NO_CONTEXT) -> Classification
```

Pure, deterministic, total over valid input, and side-effect free. No clock, no filesystem, no
network, no subprocess, no environment, no settings object, no session, no model.

## 2. Input model

```python
@dataclass(frozen=True, slots=True)
class ClassifierContext:
    known_fact_keys: frozenset[str] = frozenset()
```

The deterministic context projection. `TARGET_COMPONENT_MAP.md` line 19 gives the classifier's
inputs as "user text, ledger snapshot"; `DEPENDENCY_GRAPH.md` line 76 describes it as "pure over
text + snapshot". The snapshot is **passed in**, never read: the classifier never touches
`ProvenanceLedger`, `LedgerStore`, `current()`, `history()` or `snapshot()`, so it cannot acquire a
hidden dependency on P2 storage.

Keys only, never values. The classifier must not answer the question it is classifying, and a value
in hand would tempt exactly that. Keys must match `^[a-z][a-z0-9_]*$` — the same shape
`app/execution/provenance.py` enforces, restated rather than imported for the same reason.

`NO_CONTEXT` is the empty projection. It is the conservative default: with nothing known, a value
question classifies `MISSING_CONTEXT_QUERY`, which is an always-operational class, so absent
context never widens what a model may say.

## 3. Result

```python
@dataclass(frozen=True, slots=True)
class Classification:
    request_class: RequestClass          # from app.execution.types — never redefined
    reason: ClassificationReason         # stable, machine-readable, non-authoritative
    rule_id: str                         # which frozen rule fired
    raw_request: str                     # the caller's text, byte-identical
    classifier_version: str = "1"        # rule-set version, not the contract version
```

Five fields. `to_mapping()` serializes them for future audit use; no audit event is emitted here.

`raw_request` is the original string, not the normalized one — normalization is a matching key, not
a rewrite. `classify("  Open   VS Code  ").raw_request` is `'  Open   VS Code  '`.

## 4. What the result does not contain

No `PrimaryAction`, no tool name, no target, no raw or canonical arguments, no `Lane`, no
permission class, no confirmation decision, no capability, no reporting intent, no multi-action
state, no dispatch instruction. `11-purity-and-no-router-output.txt` §2 asserts this against a
forbidden-name list and against the serialized keys.

## 5. Vocabulary

| Symbol | What it is |
|---|---|
| `CLASSIFIER_VERSION` | `"1"` — the rule-set version. Changing classification semantics bumps it. |
| `ClassificationReason` | 11 members, one per rule. Metadata: grants no permission, selects no tool, creates no provenance. |
| `Rule` | frozen record of `rule_id`, `request_class`, `reason`. |
| `RULES` | the precedence tuple. First match wins, so behaviour cannot depend on branch order. |
| `RULE_INDEX` | read-only `mappingproxy` from rule id to rule. |
| `ClassifierError` | a `ValueError`. Raised for malformed input; there is no fallback class. |

Helpers `normalize`, `leading_clause`, `strip_polite_prefix` and `candidate_fact_keys` are exported
so tests and future phases can inspect the matching key without re-deriving it.

## 6. Errors

`ClassifierError` for: a non-string request; a `RequestClass` or `ClassificationReason` member
passed as the request (both subclass `str`, so a member would otherwise classify and look correct);
an empty or whitespace-only request; a request with no classifiable leading clause; a non-
`ClassifierContext` context; a `known_fact_keys` that is not a set; a non-string or illegally
shaped fact key.

None of these returns `OTHER`. `OTHER` is a classification for a well-formed request that meets no
higher-precedence rule, not an error channel.
