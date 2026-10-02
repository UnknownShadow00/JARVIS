# IMPORTER INVARIANT MATRIX

Measured at production `db54d615c3ee023d753e86143860c4efdc251230` by reading the existing
non-activation suites. "Excludes `app/execution/`" means the test's own source walk already
skips the control-plane package, so a sibling module there is permitted today.

| Module | Test file | Importer-test scope | Symbol-test scope | Allowlist exists? | Extensions needed by `pipeline.py` |
|---|---|---|---|---|---|
| `types` | — | — | — | — | 0 |
| `correlation` | `correlation_test.py` | not an exclusion test | — | — | 0 |
| `classifier` | `classifier_non_activation_test.py` | `_production_sources()` skips `EXECUTION_ROOT` | same walk | n/a | 0 |
| `lane` | `lane_non_activation_test.py` | excludes `app/execution/` | package-scoped | n/a | 0 |
| `canonicalize` | `canonicalize_non_activation_test.py` | `EXECUTION_DIR not in path.parents` | same | n/a | 0 |
| `provenance` | `provenance_non_activation_test.py` | `EXECUTION_DIR not in path.parents` | same | n/a | 0 |
| `hermes_adapter` | `non_activation_test.py` | named seam, already allowlisted | — | yes | 0–1 |
| `router` | `router_non_activation_test.py` | all of `app/`, excluded only by filename `router.py` | 11 symbols over the same walk | no | ~12 |
| `permissions` | `permissions_non_activation_test.py` | all of `app/`, module file only | 14 symbols, all of `app/` | no | ~15 |
| `obligations` | `obligations_non_activation_test.py` | all of `app/`, **names `app/execution/response.py`** | 11 symbols, `ObligationState`/`ObligationReason` allowed in that one file | **yes** | ~12 |
| `response` | `response_non_activation_test.py` | all of `app/`, module file only | live-path list only | no | ~2 |
| `confirmation` | `confirmation_non_activation_test.py` | all of `app/`, module file only | **19 symbols, all of `app/`, substring match** | **no** | ~20, **BLOCKED** |

Total for the ten non-blocking rows: roughly 41 assertion extensions, every one of the
kind frozen 13B11O-R1 `IMPLEMENTATION_ACCEPTANCE.md` authorizes — "name only the new
passive importer and preserve zero live wiring, with explicit justification" — and
precedented exactly by the obligation engine naming `response.py`.

## Why the obligations row is the model and the confirmation row is not

`obligations_non_activation_test.py` was *designed* to be extended: its importer assertion
is `assert hits == [str(PASSIVE_RESPONSE_MODULE.relative_to(REPO))]` and its symbol
assertion permits a named symbol subset in that one named file. Adding a second passive
consumer is a two-line change to a list, and the invariant it protects — no live wiring, no
request-path call site — is untouched.

`confirmation_non_activation_test.py` was designed **not** to be extended: `assert hits ==
[]`, with no list to add to, and nineteen symbols forbidden as substrings. A third test,
in the obligation engine's own suite, re-asserts the property with a docstring that states
the reason as a design rule rather than a convention. Extending it would not be adding a
consumer to an allowlist; it would be reversing a decision two prior phases implemented
deliberately.

## Verified non-dependency: the dispatcher

`app/execution/dispatch.py` keeps its zero importers. The pipeline needs exactly one fact
from it — the three non-dispatchable actions, for admission guard C-00a — and
`obligations.NON_ACTION_OUTCOMES` is the identical frozen three-member set
(`NONE`, `UNKNOWN_ACTION`, `MULTI_ACTION_UNSUPPORTED`), reachable through an import the
pipeline needs anyway. So no dispatcher symbol, import or call appears in any planned
pipeline source, and `dispatch_non_activation_test.py` needs no change at all. That is a
structural result, not a policy: the recorded-only pipeline has no reason to name the
dispatcher.
