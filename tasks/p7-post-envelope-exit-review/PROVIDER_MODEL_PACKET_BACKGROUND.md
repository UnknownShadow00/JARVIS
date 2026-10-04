# Established provider/model options only

No model/provider queried, installed, activated or researched on the web. Current runtime availability is intentionally unverified.

13B11A PRODUCTION_INTEGRATION_PLAN §§11–12 names the historical Hermes/Granite candidate `hermes-candidate-granite41-30b-q3km-64k`, with C5 measurement history; it explicitly says Granite is not permanently selected. FEATURE_FLAG_AND_ROLLBACK §1 independently selects Hermes/Granite versus the legacy model behind the adapter. These are the two established architecture directions. The recorded adapter accepts caller-owned identity strings but contains no transport, so acceptance of any string is not evidence that every named provider/model is viable.

Option A: separately authorize the previously measured Hermes/Granite path with an exact model tag, prompt/schema normalization, resource ownership and rollback plan. Option B: separately authorize the already configured legacy model path behind the same untrusted adapter boundary, after checking it can satisfy the recorded proposal schema. Both need fresh authorized availability and quality validation; neither is selected. Shared-model unload/in-flight ownership is an explicit prerequisite in §11, not silently solved by a flag. No third provider is introduced.
