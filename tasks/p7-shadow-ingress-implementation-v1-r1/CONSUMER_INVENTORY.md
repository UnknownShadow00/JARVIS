# Actual production graph

| Module | Production consumers | Kind |
|---|---|---|
| shadow_context.py | exactly app/execution/shadow_ingress.py | sole immutable settled-type/validator consumer; passive |
| shadow_ingress.py | zero | unwired |

The entire app tree is scanned for module/type references, with exact source-import checks inside ingress. Server, REST/WS/API/UI and all other app modules are non-consumers. Tests and external evidence methods are not production consumers. No package export was added.

Context mutable owner/store/private state is not consumed by ingress. Observation, sink, evaluator and scheduler remain absent. Historical Context V1 documentation and its module docstring correctly describe the pre-ingress implementation state and are preserved unchanged; this versioned inventory records the newly authorized relationship.
