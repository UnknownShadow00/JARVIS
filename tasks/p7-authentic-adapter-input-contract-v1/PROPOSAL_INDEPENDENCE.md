# Model proposal and JARVIS binding have distinct origins

BindingProjectionV1.expected/permission_projection are deterministic JARVIS P3/P4 comparison inputs. ModelDraft/ToolProposal are produced only by the canonical parser from the actual provider-derived recording (or labeled replay/test recording). No code path may take expected.tool_name/canonical_arguments or query.capability and synthesize a passing model proposal/recording.

Actual build_request automatically serializes only caller model, turn_id, ordered messages and generic tools. It inserts no route, permission, target, capability, expected arguments or binding result. BindingProjection has no tool_schemas output. Generic model-visible tool descriptions/parameter shapes are normal task context, not a precomputed answer or execution grant; actual proposal still must originate independently from provider generation and pass the deterministic guard.

The canonical adapter does not freeze the caller's system prompt/history text. Therefore this contract does not claim an actual live prompt has been inspected or independently tested. Future JARVIS prompt/normalizer policy must disclose exact projections/version and any contextual facts before measured use; no automatic feed of binding-specific answer fields is introduced here. Fingerprinting identifies that approved request, not proof of prompt quality or comparison independence by itself.

Return all provider-derived proposal content faithfully and in order. Do not filter/rank/select tool calls based on expected binding to improve match metrics. Even an authentic correct match grants no permission or execution; mismatch is meaningful observational evidence and must not be hidden.
