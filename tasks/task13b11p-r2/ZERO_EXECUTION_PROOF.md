# ZERO-EXECUTION PROOF

## What is proven now

No pipeline exists, so the strongest available statement is also a complete one: at
production `db54d615c3ee023d753e86143860c4efdc251230`, with `app/execution/pipeline.py`
and `app/brain/pipeline.py` both absent, this task performed zero dispatcher calls, zero
executor calls, zero registry calls, zero real tool calls, zero model and provider calls,
zero confirmation mutations, zero provenance writes and zero audit emissions — measured
over the whole task, not over a corpus.

| Measured at exit | Value |
|---|---|
| `registry.call` call sites under `app/` | 4, all in `app/server.py` (unchanged) |
| `app/` importers of `app.execution` | 3, all pre-existing and passive (`app/config.py`, `app/brain/hermes_adapter.py` ×2) |
| `app/` importers of `app.execution.dispatch` | 0 |
| `app/` importers of `app.execution.confirmation` | 0 |
| `execution.mode` | `legacy` |
| Hermes / Ollama processes | 0 |
| Production tracked files changed | 0 |

## The structural proof the implementation must carry (§25)

Not yet demonstrable, because the type it rests on is not written. Recorded as the target:

the public API must be unable to accept execution machinery. `RecordedTurn` carries no
callable, executor, dispatcher, registry handle, confirmation store, ledger store, clock,
session object or authority boolean, and the module imports no dispatcher and no registry.
A reviewer must be able to establish zero execution from the type declaration and the
import list alone — not from reading every branch for a `if execute == false` guard, which
§2 explicitly forbids as the mechanism.

One structural result is already secured and will survive the repair: the dispatcher needs
**no** import at all. The only dispatcher fact the pipeline requires is the set of
non-dispatchable actions, and `obligations.NON_ACTION_OUTCOMES` is the identical frozen
three-member set, reachable through an import the pipeline needs anyway. So
`app/execution/dispatch.py` keeps its zero importers permanently, and
`dispatch_non_activation_test.py` requires no change.

The recommended P-B02 repair makes the equivalent true of the confirmation machine: with a
settled projection instead of the record, "the pipeline performs no confirmation mutation"
rests on the absence of the import rather than on an allowlist entry — strictly stronger
than what the frozen contract currently asks for.
