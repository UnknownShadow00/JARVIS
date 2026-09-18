# Task 13B11C — Implementation

Phase P1 of the agent execution contract v1 production integration: the audit vocabulary and the
correlation identifiers every later phase joins on. Additive, passive, unwired.

Production commit `eb4c5db1985033f2c7464fbd1bd3ae9a385199d0`, parent
`521969e051f5cd725415fded0fbc8221e41c842f`, repository `/home/jarvis/JARVIS`, branch `main`,
5 files, 1,650 insertions, **0 deletions and 0 modifications**.

## 1. Files

| File | Lines | Role |
|---|---|---|
| `app/execution/audit_events.py` | 534 | event vocabulary, the 17-field record, per-event required-field table, validation, serialization |
| `app/execution/correlation.py` | 169 | typed identifiers, `CorrelationContext`, `utc_now` |
| `tests/execution/audit_events_test.py` | 639 | 49 tests |
| `tests/execution/correlation_test.py` | 148 | 13 tests |
| `tests/execution/audit_non_activation_test.py` | 160 | 8 tests |

Nothing else changed. `app/logs/audit.py`, `app/observability/tracing.py`, `app/server.py`,
`app/tools/registry.py`, `app/brain/*`, `app/resource_manager.py`, `app/config.py`, `config.yaml`,
`config.yaml.example`, `app/execution/__init__.py` and `app/execution/types.py` are all
byte-identical to the baseline (hashes in `evidence/02-…-before.txt` vs `evidence/15-final-state.txt`).

## 2. Placement decisions

`TARGET_COMPONENT_MAP.md` names `app/execution/audit_events.py` as the P1 audit module, and that is
the name used. The execution-contract vocabulary is deliberately **not** placed in
`app/logs/audit.py`: that module is the legacy transport and stays exactly as it is, so the new
trust-boundary vocabulary is reviewable in one place and the legacy writer keeps its own lifecycle.

Correlation was split into `app/execution/correlation.py` rather than living inside
`audit_events.py`. The plan names the three correlation ids (`AUDIT_PLAN.md` §2) without naming a
module, and the ids are consumed by provenance (P2), confirmation (P4) and dispatch (P5) as well as
audit — so putting them in the audit module would make audit a dependency of everything. The split
is additive and conflicts with nothing in the plan.

## 3. What was implemented

* **Vocabulary** — see `AUDIT_VOCABULARY.md`. The exact seventeen names from `AUDIT_PLAN.md` §3,
  with the count discrepancy in the 13B11A summary documented rather than silently reconciled.
* **Schema** — see `SCHEMA_V3.md`. Version 3 for these events only; legacy stays 2; same JSONL
  envelope; the seventeen contract fields, typed with P0 enums where a vocabulary already exists and
  as structured mappings where a later phase owns it.
* **Correlation** — see `CORRELATION_MODEL.md`. Five identifier classes, a frozen context with
  derived children, and an explicit separation of correlation from authorization.
* **Privacy** — no reasoning field exists in the schema, and any forbidden key inside a payload is
  rejected at any depth after name normalization.
* **Validation and serialization** — deterministic, small, total; no schema framework was built.

## 4. What was deliberately not implemented

No writer, no queue, no persistence, no background worker, no emission call site, no startup
declaration. No provenance ledger, classifier, router, canonicalizer, permission engine,
confirmation state machine, dispatcher wrapper, obligation engine, response builder, raw-prose
lock, Hermes adapter, shadow mode or Task 13C work. No redaction engine — only the passive marker
types the audit plan's retention rules imply. No deserializer for schema v3; the phase that first
replays events will own it.

## 5. Findings recorded for the operator

1. **Event-count discrepancy in the planning artifacts.** `AUDIT_PLAN.md` §3 lists thirteen entries,
   one of which expands to five confirmation events — seventeen distinct names. The 13B11A
   `FINAL-REPORT.md` §17 summarises this as "fourteen". The names are unambiguous and were
   implemented as written; the integer is a summary slip. Not a contract conflict, so not a stop
   condition. Recorded in `AUDIT_VOCABULARY.md` §2.
2. **`lane` is not one of the seventeen.** `AUDIT_PLAN.md` §2 requires the turn summary to carry the
   lane, but lane is not in the contract's seventeen fields. It is implemented as a supporting field
   and excluded from `contract_field_coverage()` so the seventeen stay exactly seventeen.
3. **No vocabulary exists yet for `proposal_guard_decision`, `confirmation_state`, `safety_outcome`
   and `permission_decision` as whole records.** The contract names the fields; the enums that would
   narrow them belong to P4/P5/P7. They are structured mappings for now, and narrowing them later is
   an additive change to this module.

## 6. Verification

`pytest -q` 483 → **553 passed**, 0 failed. Golden `12/20`, same eight IDs, before and after. The
13B11B legacy probe, run unchanged against the parent commit in a detached worktree and against
HEAD, is **byte-identical** (sha256 `fc68a0b0…`). Zero live emission call sites, proven statically
and by test. Hermes not started, not modified, `{"models":[]}` on the shared Ollama throughout.
Details in `TEST_PLAN.md` and the sealed evidence bundle.
