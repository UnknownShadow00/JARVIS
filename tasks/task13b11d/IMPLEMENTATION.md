# Task 13B11D — Implementation

Phase P2 of the agent execution contract v1 production integration: the provenance ledger. Additive,
passive, unwired.

Production commit `b9a557b4460daf240cc26f6ae932db476a5c4315`, parent
`eb4c5db1985033f2c7464fbd1bd3ae9a385199d0`, repository `/home/jarvis/JARVIS`, branch `main`,
4 files, 1,639 insertions, **0 deletions**.

## 1. Files

| File | Lines | Role |
|---|---|---|
| `app/execution/provenance.py` | 646 | records, source/trust table, ledger, snapshot, store, validation, serialization |
| `app/execution/correlation.py` | +9 | `ProvenanceRecordId` and its generator, in the existing identifier family |
| `tests/execution/provenance_test.py` | 819 | 81 tests |
| `tests/execution/provenance_non_activation_test.py` | 165 | 8 tests |

Everything else is byte-identical to the entry baseline: `config.yaml`, `config.yaml.example`,
`app/config.py`, `app/logs/audit.py`, `app/observability/tracing.py`, `app/server.py`,
`app/tools/registry.py`, `app/computer/safety.py`, `app/brain/*`, `app/resource_manager.py`,
`app/execution/__init__.py`, `app/execution/types.py`, `app/execution/audit_events.py`.

## 2. Placement and reuse

`app/execution/provenance.py` is the location the target component map names. The module **composes**
the P0 vocabulary rather than restating it: `ProvenanceSource`, `TrustClass`, `ProvenanceStatus` and
`ProvenanceRecord` all come from `app/execution/types.py`, and a test asserts the module defines no
class of those names. No C3/C4/C5 harness code was copied; the semantics moved, the code did not.

`ProvenanceRecordId` was added to `app/execution/correlation.py` because the record needs an id and
13B11C deferred exactly that identifier to P2. It is the same `uuid4().hex` family validated by the
same `is_well_formed_id()` — one scheme, not two. That is the only change to an existing file, nine
added lines, no behaviour touched.

## 3. What was implemented

See `PROVENANCE_MODEL.md`, `SOURCE_TRUST_MATRIX.md`, `CORRECTION_SEMANTICS.md` and `LEDGER_API.md`.
In short: immutable records; one frozen source → trust table with trust derived and never supplied;
keyed, trust-scoped supersession that never deletes; lookups that always carry attribution and
refuse to choose between a supplied value and a verified one; tool provenance only from a real
`TrustedToolResult`, recording only what it returned; timeout, blocked and confirmation-required
grounding nothing; per-session isolation with an explicit drop; and a JSON-safe payload that fits the
P1 `provenance.write` field without emitting anything.

## 4. What was deliberately not implemented

No wiring of any kind. No persistence, file, JSONL mirror or database. No audit emission. No
classifier, router, canonicalizer, permission engine, confirmation state machine, dispatcher,
obligation engine, response builder, raw-prose lock, Hermes adapter or shadow mode. No redaction
engine. No lifecycle connection for `drop`/`clear`. No change to the frozen P1 audit schema.

## 5. Decisions recorded for the operator

1. **`TIMEOUT` grounds no provenance.** The tool invocation contract keeps `TIMEOUT` distinct from
   `ERROR` because the side effect may or may not have happened, and no plan maps it to a provenance
   source. Rather than invent one — which would extend the frozen P0 `ProvenanceSource` enum — the
   ledger refuses a timeout with a named error and records nothing, so it can never read as success
   *or* as failure. `BLOCKED` and `CONFIRMATION_REQUIRED` are refused on the same grounds. If a
   future phase wants an explicit `UNKNOWN_OUTCOME` source, that is an operator decision to extend
   the frozen enum.
2. **`current()` refuses to choose.** When a supplied value and a verified observation both stand for
   one key, the ledger raises `AmbiguousProvenance` instead of preferring one. The preference is
   §16 response policy, owned by P6. Callers name the trust class or take the whole set.
3. **Supersession is keyed, not value-compared.** Recording the same value again supersedes and keeps
   both records, following the integration plan's rule as written and keeping "when did the user last
   say this" auditable.
4. **Fact keys are `^[a-z][a-z0-9_]*$`.** Small and predictable; widening it later is additive. A
   tool returning a key outside that shape is refused rather than silently rewritten.

## 6. Verification

`pytest -q` 553 → **642 passed**, 0 failed. Golden `12/20`, same eight IDs, before and after. The
legacy probe, captured before any P2 file was installed and again after the commit with the
byte-identical 13B11B/C fixture, is unchanged (`fc68a0b0…`). Zero live wiring, proven statically and
by test. Hermes not started, not modified; `{"models":[]}` on the shared Ollama throughout. Details
in `TEST_PLAN.md` and the sealed evidence bundle.
