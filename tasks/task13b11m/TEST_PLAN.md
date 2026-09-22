# Test Plan and Result

## Pre-implementation

Freeze and hash the response matrix and exact template inventory with `response.py` absent. Run a
red test proving the new module does not exist.

## Focused tests

- every actual reason produces the exact frozen response;
- every obligation/source is covered;
- repeated objects and `to_mapping()` serialization are identical;
- trusted success/error/timeout rules and reporting-intent inertness;
- D-P6-01 denial reasons remain distinct and D-P6-02 timeout stays uncertainty-safe;
- all 41 unsupported verbs compose through real P3/P6 and produce one capability family;
- confirmation and five target families imply no execution and invent no target;
- user fact, user report, tool observation and control-state attribution differ;
- no-value and optional acknowledgement/status paths;
- provenance and invocation mismatch corpus;
- model/look-alike rejection;
- purity, static imports, audit hook, zero live consumers.

Result: 169 focused tests passed.

## Regression gates

```text
pytest: 5245 passed, 11 deselected, 0 failed
golden: 12/20, same eight failure IDs
legacy probe: fc68a0b041c8d0d41f446e9638cae5f888e4f4f6caf84d438ca0e11a30d98291
security review: 19/19
critical non-change: 24/24
```

`pip-audit` was unavailable and was not installed because package installation was outside task
scope; `pip check` reported no broken requirements.
