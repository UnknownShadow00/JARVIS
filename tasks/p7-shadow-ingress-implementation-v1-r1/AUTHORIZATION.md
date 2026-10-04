# Exact operator authorization

The operator's retry authorizes ONE existing semantic transition: `tests/execution/shadow_context_test.py::test_exact_import_graph_and_zero_production_consumers`. No other existing exception is authorized or used.

Old blocking assertions:

```python
assert 'shadow_context' not in text
assert 'ShadowContextV1' not in text and 'SettledShadowTurnContextV1' not in text
assert not (ROOT / 'app/execution/shadow_ingress.py').exists()
```

Newly allowed module: `app/execution/shadow_ingress.py`. Newly allowed context symbol: exactly `SettledShadowTurnContextV1` from `app.execution.shadow_context`, without an alias. Required new graph: one passive context consumer, ingress; zero ingress consumers. The mutable owner, store, private mutable state, minting, acquisition, downstream imports/calls, dynamic imports and service locators remain forbidden. Observation remains absent. The original context import budget remains intact.

Before production code/test edits, Core evidence froze `authorization-freeze.json`, both function versions, the complete authorized test file, both executable corpora and expected outcomes. `pre-code-freeze.sha256` verified all eight entries. The complete replacement function is recorded below; its production copy is byte-exact. Prior blocked/context evidence and historical corpus are preserved unchanged.

```python
def test_exact_import_graph_and_zero_production_consumers():
    allowed = {'__future__', 'dataclasses', 'datetime', 'types',
               'app.execution.correlation', 'app.execution.provenance'}
    tree = ast.parse(MODULE.read_text())
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            assert n.module in allowed and n.level == 0
        elif isinstance(n, ast.Import):
            assert False, 'all imports must be explicit and frozen'

    ingress = ROOT / 'app/execution/shadow_ingress.py'
    assert ingress.is_file()
    ingress_tree = ast.parse(ingress.read_text())
    imports = [n for n in ast.walk(ingress_tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    assert all(isinstance(n, ast.ImportFrom) and n.level == 0 for n in imports)
    assert [(n.module, tuple((a.name, a.asname) for a in n.names)) for n in imports] == [
        ('__future__', (('annotations', None),)),
        ('dataclasses', (('dataclass', None),)),
        ('app.execution.shadow_context', (('SettledShadowTurnContextV1', None),)),
    ]
    forbidden = {
        'ShadowContextV1', 'LedgerStore', 'ProvenanceLedger',
        'new_session_id', 'new_turn_id', 'new_turn_context',
        'eval', 'exec', '__import__', 'getattr', 'setattr', 'open',
        'globals', 'locals', 'vars', 'registry', 'dispatcher', 'executor',
    }
    assert not ({n.id for n in ast.walk(ingress_tree) if isinstance(n, ast.Name)} & forbidden)
    assert all(not n.attr.startswith('_') or n.attr == '__post_init__'
               for n in ast.walk(ingress_tree) if isinstance(n, ast.Attribute))
    validation_calls = []
    for n in ast.walk(ingress_tree):
        if not isinstance(n, ast.Call):
            continue
        if isinstance(n.func, ast.Name):
            assert n.func.id in {'dataclass', 'type', 'ValueError'}
        else:
            assert isinstance(n.func, ast.Attribute)
            assert isinstance(n.func.value, ast.Name)
            assert (n.func.value.id, n.func.attr) == ('SettledShadowTurnContextV1', '__post_init__')
            assert not n.keywords and len(n.args) == 1
            assert ast.dump(n.args[0]) == ast.dump(ast.Attribute(
                value=ast.Name(id='self', ctx=ast.Load()), attr='context', ctx=ast.Load()))
            validation_calls.append(n)
    assert len(validation_calls) == 1

    context_consumers = []
    ingress_consumers = []
    for path in sorted((ROOT / 'app').rglob('*.py')):
        text = path.read_text()
        if path != MODULE and any(marker in text for marker in (
                'shadow_context', 'ShadowContextV1', 'SettledShadowTurnContextV1')):
            context_consumers.append(path)
        if path != ingress and any(marker in text for marker in (
                'shadow_ingress', 'ShadowIngressEnvelopeV1')):
            ingress_consumers.append(path)
        if path in (MODULE, ingress):
            continue
        assert 'shadow_context' not in text
        assert 'ShadowContextV1' not in text and 'SettledShadowTurnContextV1' not in text
        assert 'shadow_ingress' not in text and 'ShadowIngressEnvelopeV1' not in text
    assert context_consumers == [ingress]
    assert ingress_consumers == []
    assert not (ROOT / 'app/execution/shadow_observation.py').exists()
```
