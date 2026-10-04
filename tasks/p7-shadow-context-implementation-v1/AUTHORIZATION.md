# Exact constructor authorization

Operator authority: this task's exact D10 constructor exception; frozen Context V1 remains normative. Before production code or existing-test modification, `authorization-freeze.json`, the concrete `authorized-gate-transition.py`, and the executable focused corpus were written to Core evidence. `pre-code-freeze.sha256` records their pre-code integrity. The first run failed solely because the module was absent.

Exact file: `tests/execution/provenance_non_activation_test.py`. Exact function: `test_there_are_zero_live_provenance_writes`. Entry function:

```python
def test_there_are_zero_live_provenance_writes() -> None:
    writers = []
    for path in sorted(APP_DIR.rglob("*.py")):
        if path == PROVENANCE:
            continue
        source = path.read_text(encoding="utf-8")
        for marker in ("ProvenanceLedger(", "LedgerStore(", ".record_user_fact(", ".record_tool_result("):
            if marker in source:
                writers.append(f"{path.relative_to(PROJECT_ROOT)}:{marker}")
    assert writers == [], f"provenance written from production code: {writers}"
```

Detected relationship: the marker `LedgerStore(` classifies mandatory passive owner allocation as a writer. Additive authorization: **exactly one argument-free `LedgerStore()` call assigned directly to `self._store` in `ShadowContextV1.__init__`, only in `app/execution/shadow_context.py`**.

The frozen implemented transition is:

```python
def test_there_are_zero_live_provenance_writes() -> None:
    writers = []
    for path in sorted(APP_DIR.rglob("*.py")):
        if path == PROVENANCE:
            continue
        source = path.read_text(encoding="utf-8")
        for marker in ("ProvenanceLedger(", "LedgerStore(", ".record_user_fact(", ".record_tool_result("):
            if marker in source:
                writers.append(f"{path.relative_to(PROJECT_ROOT)}:{marker}")
    shadow_tree = ast.parse((EXECUTION_DIR / "shadow_context.py").read_text(encoding="utf-8"))
    allocations = [node for node in ast.walk(shadow_tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Name) and node.func.id == "LedgerStore"]
    owned = [node for cls in shadow_tree.body
             if isinstance(cls, ast.ClassDef) and cls.name == "ShadowContextV1"
             for method in cls.body if isinstance(method, ast.FunctionDef) and method.name == "__init__"
             for node in method.body if isinstance(node, ast.Assign) and node.value in allocations
             and len(node.targets) == 1 and isinstance(node.targets[0], ast.Attribute)
             and isinstance(node.targets[0].value, ast.Name) and node.targets[0].value.id == "self"
             and node.targets[0].attr == "_store"]
    assert (writers == ["app/execution/shadow_context.py:LedgerStore("]
            and len(allocations) == len(owned) == 1
            and not allocations[0].args and not allocations[0].keywords), (
        f"provenance written from production code or non-instance allocation: {writers}"
    )
```

Every existing marker and every other existing test function stays unchanged. The constructor's enclosing class/method, instance assignment, count and no-argument form are checked by AST. There is no execution-package wildcard, server/pipeline/adapter/provider/API/UI allowance, future-module allowance or write authorization. Semantic authorization count: ONE. A second existing-test exception would have blocked implementation; none was needed.

Actual forbidden P2 mutations: `ProvenanceLedger.record_user_fact`, `record_user_reported`, `record_tool_result`, `record_confirmation_required`, `record_control_state`, `_append`, `_supersede_locked`; `LedgerStore.drop`, `clear`; direct state append/update/replacement and provenance promotion. `_build` is also trapped because it constructs trusted records. `LedgerStore.for_session` may allocate/associate an empty ledger; it does not create trusted facts. Constructor allocation is separately proven from zero writes.
