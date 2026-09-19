# approval_mode — tightening only (D-09)

## Production vocabulary

`config.yaml` `safety.approval_mode` is one of `"safe"`, `"balanced"`, `"strict"`; the live value is
`"balanced"`. Legacy semantics (`app/tools/registry.py:_requires_confirmation`): confirmation when
`SAFETY_LEVEL >= 0` for `strict`, `>= 1` for `safe`, `>= 2` for `balanced`. So the legacy order from
loosest to strictest is **balanced → safe → strict**, and the same order is used here.

## The rule

`balanced` is the **floor**, not a dial. A mode may raise a decision and may never lower one:

```
strictness: ALLOW (0) < REQUIRE_CONFIRMATION (1) < DENY (2)
strictness(tighten(outcome, mode)) >= strictness(outcome)        for every outcome and mode
mode_a stricter than mode_b  =>  strictness(tighten(o, a)) >= strictness(tighten(o, b))
```

## The frozen table

| Base outcome | `balanced` (floor) | `safe` | `strict` |
|---|---|---|---|
| `ALLOW`, class `READ_ONLY` | `ALLOW` | `ALLOW` | `REQUIRE_CONFIRMATION` |
| `ALLOW`, any other class | `ALLOW` | `REQUIRE_CONFIRMATION` | `REQUIRE_CONFIRMATION` |
| `REQUIRE_CONFIRMATION` | `REQUIRE_CONFIRMATION` | `REQUIRE_CONFIRMATION` | `REQUIRE_CONFIRMATION` |
| `DENY` | `DENY` | `DENY` | `DENY` |

`safe` raising only non-`READ_ONLY` allows mirrors the legacy "confirm at level ≥ 1" boundary, which
is the mutating boundary. `strict` confirms everything, mirroring "confirm at level ≥ 0".

`DENY` is absorbing: no mode, and no other input, turns it into `REQUIRE_CONFIRMATION` or `ALLOW`.
`REQUIRE_CONFIRMATION` never becomes `ALLOW`. Tested exhaustively over every
(class × base outcome × mode) combination, plus every ordered mode pair.

## What is not changed

`config.yaml` is untouched and `registry._requires_confirmation` is untouched; the legacy gate keeps
its current symmetric behaviour on the legacy path. This table governs the passive engine only, and
nothing reads it yet.
