# Dependency Graph

**Status:** plan only.

## 1. Graph

```
                      ┌─────────────────┐
                      │ execution config│  (feature flag, P0)
                      │   + types       │
                      └────────┬────────┘
                               │
                 ┌─────────────┼──────────────┐
                 ▼             ▼              ▼
         ┌──────────────┐ ┌──────────┐ ┌──────────────┐
         │ audit events │ │ lane     │ │ canonicalizer│
         │    (P1)      │ │  (P3)    │ │    (P3)      │
         └──────┬───────┘ └────┬─────┘ └──────┬───────┘
                │              │              │
                ▼              │              │
         ┌──────────────┐      │              │
         │  provenance  │◄─────┘              │
         │    (P2)      │                     │
         └──────┬───────┘                     │
                │                             │
                ▼                             │
         ┌──────────────┐   ┌─────────────┐   │
         │  classifier  │──►│   router    │◄──┘
         │    (P3)      │   │    (P3)     │
         └──────┬───────┘   └──────┬──────┘
                │                  │
                ▼                  ▼
         ┌─────────────────────────────┐
         │ permission engine (P4)      │
         └──────────────┬──────────────┘
                        ▼
         ┌─────────────────────────────┐
         │ confirmation manager (P4)   │
         └──────────────┬──────────────┘
                        ▼
         ┌─────────────────────────────┐
         │ dispatcher boundary (P5)    │──► registry.call (existing gate)
         └──────────────┬──────────────┘
                        ▼
         ┌─────────────────────────────┐
         │ obligation engine (P6)      │◄── provenance snapshot
         └──────────────┬──────────────┘
                        ▼
         ┌─────────────────────────────┐
         │ operational response (P6)   │  ── the raw-prose lock lives here
         └──────────────┬──────────────┘
                        ▼
         ┌─────────────────────────────┐        ┌──────────────────┐
         │ pipeline (P7)               │◄───────│ Hermes adapter   │
         └──────────────┬──────────────┘        │      (P7)        │
                        ▼                        └──────────────────┘
         ┌─────────────────────────────┐
         │ server branch + API/UI (P7) │
         └─────────────────────────────┘
```

## 2. Critical path

`config/types (P0) → audit (P1) → provenance (P2) → classifier+router (P3) → permissions (P4) →
confirmation (P4) → dispatcher (P5) → obligations+response (P6) → pipeline/adapter (P7) →
conformance (P8)`

Everything user-visible waits on P7; everything safety-relevant is settled by P6.

## 3. Independently buildable / testable

| Component | Can be built and tested alone | Why |
|---|---|---|
| canonicalizer | yes | pure function over (tool, args) |
| lane policy | yes | pure function over class + flags |
| classifier | yes, with a stub ledger snapshot | pure over text + snapshot |
| router | yes | pure over text + lexicon |
| provenance ledger | yes | pure data structure |
| permission engine | yes, with a static policy table | pure over action/target |
| obligation engine | yes, with fixtures for ledger/result/confirmation | pure selection |
| response builder | yes, with the same fixtures | pure rendering |
| confirmation manager | mostly — needs a clock and a store interface | inject both |
| dispatcher | no — needs the registry and the permission decision | integration point |
| Hermes adapter | yes, against recorded model outputs | the model is untrusted input anyway |

Eight of the eleven new components are pure functions or pure data structures with no I/O, which
is what makes the conformance tests cheap to run and the phases genuinely reversible.

## 4. Fan-in points to watch

* `app/server.py::_process` — one branch, added at P7. The only legacy file that changes.
* `app/tools/registry.py::call` — unchanged, but now has two callers (legacy and dispatcher);
  the double-execution risk in the risk register lives here.
* `app/logs/audit.py` — shared by both paths; additive event types only.
