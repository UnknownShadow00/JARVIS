# Consolidated next-unit structural decision packet

These are proposals only. Neither current test is edited by the R4 observation task. For the minimal direct typed-recovery sink design, the complete current-tree sweep identifies **two existing helper-function transitions**. Their dependent callers remain byte-identical and gain the same positive proof, rather than each deleting its assertion.

| Function | Exact current assertion / conflict | Narrow proposed relationship |
|---|---|---|
| tests/execution/shadow_observation_test.py::assert_observation_structure | `assert 'shadow_observation' not in text and 'ShadowObservationRecordV1' not in text`; `assert not (ROOT/'app/execution'/name).exists()` where name includes shadow_observation_sink.py | Exact sink existence and sole passive ShadowObservationRecordV1 consumer. Preserve observer direct imports/calls/privacy/fingerprint/hash, every other zero-consumer restriction, and scheduler/evaluator absence |
| tests/execution/pipeline_contract_support.py::assert_presence | `s=p.read_text();assert 'execution.pipeline' not in s and 'run_recorded_turn' not in s, str(p)`; `if isinstance(n,ast.ImportFrom):assert not any(a.name=='pipeline' for a in n.names)` | Only exact sink PipelineStage/PipelineStopReason symbol imports for explicit V1 enum recovery. Preserve pipeline public API, observer five-symbol budget, all engine-call bans and all other consumers |

Proposed observer helper replacement pattern, with exact SINK path and a new sink-focused AST proof (to be frozen in the next session):

```python
for path in (ROOT/'app').rglob('*.py'):
    if path == MODULE:
        continue
    if path == SINK:
        assert_sink_structure()  # exact record + UTC + enum + reviewed backend budget
        continue
    text = path.read_text()
    assert 'shadow_observation' not in text and 'ShadowObservationRecordV1' not in text
assert SINK.is_file()
for name in ('shadow_scheduler.py', 'shadow_evaluator.py'):
    assert not (ROOT/'app/execution'/name).exists()
```

Keep all earlier observer-local AST/fingerprint/hash checks. assert_sink_structure must positively prove only record-type consumption/validation/recovery construction, exact chronology helper, enumerated data enum types and the single reviewed persistence backend; zero sink consumers/live callers; no observer producer call; no context/ingress/store/engine/service lookup, audit/P2/model or dynamic import. It must not be a blanket allowlist.

Proposed PB04 replacement branch after the existing exact observer branch:

```python
if p == ROOT/'app/execution/shadow_observation_sink.py':
    assert_sink_structure()
    continue
```

The new proof must require `from app.execution.pipeline import PipelineStage, PipelineStopReason` only (no aliases/module import) and permit those enum constructors solely for explicit validated decoding. No AdmissionMode, PipelineStop, TurnOutcome, RecordedTurn, run_recorded_turn or engine execution is permitted to the sink. All remaining PB04 assertions stay unchanged. Router, PermissionDecision and BindingProjectionV1 owner imports are unnecessary: persisted record enums belong to types/pipeline, not the source-fact engines.

This batch is separate from the ten completed observation transitions. Exact next-session source/assertions/replacements must be re-frozen before sink code. Backend changes may affect a future import/call budget and require rechecking the full current-tree inventory; no unreviewed blanket authority is implied.
