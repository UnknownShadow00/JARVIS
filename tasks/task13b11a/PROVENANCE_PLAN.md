# Provenance Ledger Plan

**Status:** plan only. No ledger exists in production today (gap G-17).

## 1. Record shape

```
ProvenanceRecord:
  record_id        opaque id
  turn_id          conversation turn that produced it
  fact_key         e.g. "deployment_target", "port", "preferred_region", "observation"
  value            scalar or small structured value
  source_type      USER_FACT | USER_REPORTED | TOOL_SUCCESS | TOOL_ERROR |
                   CONFIRMATION_REQUIRED | ROUTER_STATE | CAPABILITY_STATE | CORRECTION_STATE
  trust_class      SUPPLIED (user said it) | VERIFIED (dispatcher observed it) | CONTROL (our own state)
  invocation_id    set when source_type is TOOL_SUCCESS / TOOL_ERROR
  created_at       UTC
  status           CURRENT | SUPERSEDED
  superseded_by    record_id | null
  session_id       owner scope
```

`trust_class` is deliberately separate from `source_type`: the contract's rule is about whether a
statement may be presented as verified (§9.3, §16), and one boolean per record makes that check
trivial and hard to get wrong in a template.

## 2. Operations

| Operation | Rule |
|---|---|
| `record_user_fact(turn, key, value)` | trust_class SUPPLIED; supersedes an earlier CURRENT record with the same `fact_key` in the same session |
| `record_user_observation(turn, text, parsed)` | source `USER_REPORTED`, trust SUPPLIED; never overwrites a VERIFIED record |
| `record_tool_result(invocation, result)` | source `TOOL_SUCCESS`/`TOOL_ERROR`, trust VERIFIED; one record per fact the result explicitly contains |
| `current(fact_key)` | the single CURRENT record, or none |
| `history(fact_key)` | all records, newest first — audit view |
| `snapshot()` | the immutable view passed to the classifier, obligation engine and response builder |

Supersession never deletes (§10, INV-019). A `USER_FACT` correction supersedes the previous
`USER_FACT`; it does **not** supersede a `TOOL_SUCCESS` record, because a user statement cannot
overwrite an observation — it creates a newer SUPPLIED record alongside it, and the response layer
is responsible for saying which is which.

## 3. Scope and lifetime — recommendation

**Start in-memory per conversation session, with an append-only JSONL mirror for audit.**

Reasoning grounded in the current architecture:

* There is no database in production (`CURRENT_ARCHITECTURE_MAP.md` §11); introducing one for v1
  would be the largest and least reversible part of the change.
* Audit already writes JSONL asynchronously with rotation (`app/logs/audit.py`), so mirroring
  provenance events there costs little and gives replay/debug without a schema migration.
* The validated C3/C4/C5 behaviour was per-session in-memory provenance, so this is also the
  shape that has actually been measured.

Deferred to a later task, once the ledger has proven itself: persistence of the *current* fact set
across restarts and deep sleep. The lifecycle section of the integration plan states what must
survive; the honest v1 position is that provenance does **not** survive a process exit, and the
response layer must therefore treat an empty ledger as "not available in the current context"
rather than as "nothing is true".

## 4. Interaction with existing memory components

`app/memory/*` (mem0 client, RAG, procedural, graphiti) are *semantic* stores for recall quality.
They are **not** provenance and must never be read as trusted operational state: content retrieved
from them is untrusted content under §21. The ledger is a separate, small, control-plane structure.

## 5. What the ledger is not allowed to hold

* Model-authored facts of any kind (INV-002).
* Free-form model prose.
* Anything derived by similarity, embedding or inference.
* Chain-of-thought (§19.2).
