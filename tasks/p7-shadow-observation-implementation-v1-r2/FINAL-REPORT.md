JARVIS PASSIVE SHADOW OBSERVATION V1 BLOCKED

Exact next unauthorized relationship: observation's required passive type imports transitively load app.execution.canonicalize.

Frozen Unit C OBSERVATION.md requires pipeline types AdmissionMode, PipelineStage, PipelineStopReason, PipelineStop, TurnOutcome and BindingProjectionV1 from their existing canonical owners. D03 FAIL_CLOSED.md requires rejection of wrong exact types. Actual app/execution/pipeline.py line 16 imports canonicalize at module scope; app/execution/binding_projection.py line 12 imports canonicalize at module scope. Normal imports of the approved types therefore load the canonicalizer module. No observation code or engine invocation is needed to establish this import edge.

R2 section 11 and acceptance require canonicalizer module imported: NO. The required type-owner import closure produces YES. A fresh-process probe confirms this with zero canonicalizer calls. The owning modules also retain canonicalizer callable references for their own existing functions. Importing data types does not call those functions, but it cannot truthfully satisfy a closure containing no canonicalizer module.

Narrow authorization required: permit the existing transitive definition-only canonicalizer imports through the exact approved pipeline/binding type owners; keep observation's direct canonicalizer import/reference/call forbidden and require zero canonicalizer execution. Define module-import closure separately from the producer call graph. No production owner changes, extra type symbols, live consumers, or engine calls are requested. Alternatively, a separate authorized type-owner refactor would be required; it is outside this task's production boundary.

No eleventh existing-test exception was applied or identified as necessary at this stop. All ten approved test transitions remain unapplied; the blocker is the stronger R2 import-closure requirement, not the fingerprint declarer assertion. TYPE_CHECKING-only imports do not supply canonical runtime class identities for the frozen exact-type checks; name/shape substitution, dynamic imports, service locators, or copied classes are not approved substitutes.

Stopped before production/existing-test changes, authorization replacement/corpus freeze, or implementation run. Production HEAD remains dd2878754e82b26028593d47562ff0420cc8e0c0; context/ingress match sealed bytes; observation is absent. No commits, push, model/provider calls, or canonicalizer execution.
